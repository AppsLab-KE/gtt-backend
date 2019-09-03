import numpy as np
import scipy
import pandas as pd
import math
import random
import sklearn
import _pickle as pickle
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse.linalg import svds
from django.db.models import Q
from posts.models import Post, Rating, Comment, Bookmark
from posts.serializers import (
    RecommenderPostSerializer, ViewedSerializer, LikedSerializer, CommentedSerializer, BookmarkedSerializer,
)

#Top-N accuracy metrics consts
EVAL_RANDOM_SAMPLE_NON_INTERACTED_ITEMS = 100
USER_INTERACTIONS_COUNT = 5

class Dataset:
    post_columns = ['timestamp', 'eventType', 'contentId', 'authorPersonId', 'title', 'text']
    interaction_columns = ['timestamp', 'eventType', 'contentId', 'personId']

    def __init__(self):
        posts = Post.objects.filter(Q(ratings__rating=True)|Q(ratings__rating=False))
        post_serializer = RecommenderPostSerializer(posts, many=True)
        all_ratings = Rating.objects.all()
        viewed_serializer = ViewedSerializer(all_ratings, many=True)
        true_ratings = Rating.objects.filter(rating=True)
        liked_serializer = LikedSerializer(true_ratings, many=True)
        all_comments = Comment.objects.all()
        commented_serializer = CommentedSerializer(all_comments, many=True)
        all_bookmarks = Bookmark.objects.all()
        bookmarked_serializer = BookmarkedSerializer(all_bookmarks, many=True)
        user_interactions = viewed_serializer.data + liked_serializer.data + commented_serializer.data + bookmarked_serializer.data
        self.__shared_posts = post_serializer.data
        self.__user_interactions = user_interactions

    def get_shared_posts(self):
        return self.__shared_posts

    def get_user_interactions(self):
        return self.__user_interactions

    def get_dataframes(self):
        shared_posts_df = pd.DataFrame(self.__shared_posts, columns=self.post_columns)
        user_interactions_df = pd.DataFrame(self.__user_interactions, columns=self.interaction_columns)    
        return (
            shared_posts_df,
            user_interactions_df
        )

    def __smooth_user_preference(self, x):
        return math.log(1+x, 2)
    
    def clean_data(self):
        event_type_strength = {
            'VIEW': 1.0,
            'LIKE': 2.0, 
            'BOOKMARK': 3.0,
            'COMMENT': 4.0,
            }
        shared_posts_df, user_interactions_df = self.get_dataframes()
        user_interactions_df['eventStrength'] = user_interactions_df['eventType'].apply(lambda x: event_type_strength[x])
        users_interactions_count_df = user_interactions_df.groupby(['personId', 'contentId']).size().groupby('personId').size()
        #print('# users: %d' % len(users_interactions_count_df))
        users_with_enough_interactions_df = users_interactions_count_df[users_interactions_count_df >= USER_INTERACTIONS_COUNT].reset_index()[['personId']]
        #print('# users with at least 5 interactions: %d' % len(users_with_enough_interactions_df))
        #print('# of interactions: %d' % len(user_interactions_df))
        interactions_from_selected_users_df = user_interactions_df.merge(users_with_enough_interactions_df, 
               how = 'right',
               left_on = 'personId',
               right_on = 'personId')
        #print('# of interactions from users with at least 5 interactions: %d' % len(interactions_from_selected_users_df))
        interactions_full_df = interactions_from_selected_users_df \
                    .groupby(['personId', 'contentId'])['eventStrength'].sum() \
                    .apply(self.__smooth_user_preference).reset_index()
        #print('# of unique user/item interactions: %d' % len(interactions_full_df))
        return interactions_full_df

    def perform_evaluation(self):
        interactions_full_df = self.clean_data()
        interactions_train_df, interactions_test_df = train_test_split(interactions_full_df,
                                   stratify=interactions_full_df['personId'], 
                                   test_size=0.20,
                                   random_state=42)
        #print('# interactions on Train set: %d' % len(interactions_train_df))
        #print('# interactions on Test set: %d' % len(interactions_test_df))
        interactions_full_indexed_df = interactions_full_df.set_index('personId')
        interactions_train_indexed_df = interactions_train_df.set_index('personId')
        interactions_test_indexed_df = interactions_test_df.set_index('personId')
        return (
            interactions_train_df,
            interactions_test_df,
            interactions_full_indexed_df,
            interactions_train_indexed_df,
            interactions_test_indexed_df
        )

    def get_item_popularity(self):
        interactions_full_df = self.clean_data()
        item_popularity_df = interactions_full_df.groupby('contentId')['eventStrength'].sum().sort_values(ascending=False).reset_index()
        return item_popularity_df

    def get_items_interacted(self, person_id, interactions_df):
        interacted_items = interactions_df.loc[person_id]['contentId']
        return set(interacted_items if type(interacted_items) == pd.Series else [interacted_items])


class ModelEvaluator:

    def __init__(self):
        self.dataset = Dataset()
        self.interactions_train_df, self.interactions_test_df, self.interactions_full_indexed_df, self.interactions_train_indexed_df, self.interactions_test_indexed_df = self.dataset.perform_evaluation()

    def get_not_interacted_items_sample(self, person_id, sample_size, seed=42):
        articles_df = self.dataset.get_dataframes()[0]
        interacted_items = self.dataset.get_items_interacted(person_id, self.interactions_full_indexed_df)
        all_items = set(articles_df['contentId'])
        non_interacted_items = all_items - interacted_items
        random.seed(seed)
        if not bool(len(non_interacted_items)):
            sample_size = 0
        non_interacted_items_sample = random.sample(non_interacted_items, sample_size)
        return set(non_interacted_items_sample)

    def _verify_hit_top_n(self, item_id, recommended_items, topn):        
            try:
                index = next(i for i, c in enumerate(recommended_items) if c == item_id)
            except:
                index = -1
            hit = int(index in range(0, topn))
            return hit, index

    def evaluate_model_for_user(self, model, person_id):
        interacted_values_testset = self.interactions_test_indexed_df.loc[person_id]
        if type(interacted_values_testset['contentId']) == pd.Series:
            person_interacted_items_testset = set(interacted_values_testset['contentId'])
        else:
            person_interacted_items_testset = set([int(interacted_values_testset['contentId'])])  
        interacted_items_count_testset = len(person_interacted_items_testset) 

        person_recs_df = model.recommend_items(person_id, 
                                               items_to_ignore=self.dataset.get_items_interacted(person_id, 
                                                                                    self.interactions_train_indexed_df), 
                                               topn=10000000000)

        hits_at_5_count = 0
        hits_at_10_count = 0
        
        for item_id in person_interacted_items_testset:
            
            non_interacted_items_sample = self.get_not_interacted_items_sample(person_id, 
                                                                          sample_size=EVAL_RANDOM_SAMPLE_NON_INTERACTED_ITEMS, 
                                                                          seed=item_id%(2**32))

            items_to_filter_recs = non_interacted_items_sample.union(set([item_id]))

            valid_recs_df = person_recs_df[person_recs_df['contentId'].isin(items_to_filter_recs)]                    
            valid_recs = valid_recs_df['contentId'].values
            hit_at_5, index_at_5 = self._verify_hit_top_n(item_id, valid_recs, 5)
            hits_at_5_count += hit_at_5
            hit_at_10, index_at_10 = self._verify_hit_top_n(item_id, valid_recs, 10)
            hits_at_10_count += hit_at_10

        recall_at_5 = hits_at_5_count / float(interacted_items_count_testset)
        recall_at_10 = hits_at_10_count / float(interacted_items_count_testset)

        person_metrics = {'hits@5_count':hits_at_5_count, 
                          'hits@10_count':hits_at_10_count, 
                          'interacted_count': interacted_items_count_testset,
                          'recall@5': recall_at_5,
                          'recall@10': recall_at_10}
        return person_metrics

    def evaluate_model(self, model):
        people_metrics = []
        for idx, person_id in enumerate(list(self.interactions_test_indexed_df.index.unique().values)):
            person_metrics = self.evaluate_model_for_user(model, person_id)  
            person_metrics['_person_id'] = person_id
            people_metrics.append(person_metrics)
        #print('%d users processed' % idx)

        detailed_results_df = pd.DataFrame(people_metrics) \
                            .sort_values('interacted_count', ascending=False)
        
        global_recall_at_5 = detailed_results_df['hits@5_count'].sum() / float(detailed_results_df['interacted_count'].sum())
        global_recall_at_10 = detailed_results_df['hits@10_count'].sum() / float(detailed_results_df['interacted_count'].sum())
        
        global_metrics = {'modelName': model.get_model_name(),
                          'recall@5': global_recall_at_5,
                          'recall@10': global_recall_at_10}    
        return global_metrics, detailed_results_df

class PopularityRecommender:
    
    MODEL_NAME = 'Popularity'
    
    def __init__(self):
        self.dataset = Dataset()
        self.popularity_df = self.dataset.get_item_popularity()
        self.items_df = self.dataset.get_dataframes()[0]
        
    def get_model_name(self):
        return self.MODEL_NAME
        
    def recommend_items(self, items_to_ignore=[], topn=10, verbose=False):
        recommendations_df = self.popularity_df[~self.popularity_df['contentId'].isin(items_to_ignore)] \
                               .sort_values('eventStrength', ascending = False) \
                               .head(topn)

        if verbose:
            if self.items_df is None:
                raise Exception('"items_df" is required in verbose mode')

            recommendations_df = recommendations_df.merge(self.items_df, how = 'left', 
                                                          left_on = 'contentId', 
                                                          right_on = 'contentId')[['eventStrength', 'contentId', 'title']]


        return recommendations_df

class Vectorizer:
    def __init__(self):
        self.dataset = Dataset()
        self.articles_df = self.dataset.get_dataframes()[0]
        stopwords_list = stopwords.words('english') + stopwords.words('portuguese')
        vectorizer = TfidfVectorizer(analyzer='word',
        ngram_range=(1, 2),
        min_df=0.003,
        max_df=0.5,
        max_features=5000,
        stop_words=stopwords_list)
        self.item_ids = self.articles_df['contentId'].tolist()
        self.tfidf_matrix = vectorizer.fit_transform(self.articles_df['title'] + "" + self.articles_df['text'])
        self.tfidf_feature_names = vectorizer.get_feature_names()

    def get_item_profile(self, item_id):
        idx = self.item_ids.index(item_id)
        item_profile = self.tfidf_matrix[idx:idx+1]
        return item_profile

    def get_item_profiles(self, ids):
        item_profiles_list = [self.get_item_profile(x) for x in ids]
        item_profiles = scipy.sparse.vstack(item_profiles_list)
        return item_profiles

    def build_users_profile(self, person_id, interactions_indexed_df):
        interactions_person_df = interactions_indexed_df.loc[person_id]
        user_item_profiles = self.get_item_profiles(interactions_person_df['contentId'])
    
        user_item_strengths = np.array(interactions_person_df['eventStrength']).reshape(-1,1)
        user_item_strengths_weighted_avg = np.sum(user_item_profiles.multiply(user_item_strengths), axis=0) / np.sum(user_item_strengths)
        user_profile_norm = sklearn.preprocessing.normalize(user_item_strengths_weighted_avg)
        return user_profile_norm

    def build_users_profiles(self): 
        interactions_full_df = self.dataset.clean_data()
        interactions_indexed_df = interactions_full_df[interactions_full_df['contentId'] \
                                                   .isin(self.articles_df['contentId'])].set_index('personId')
        user_profiles = {}
        for person_id in interactions_indexed_df.index.unique():
            user_profiles[person_id] = self.build_users_profile(person_id, interactions_indexed_df)
        return user_profiles

class ContentBasedRecommender:
    
    MODEL_NAME = 'Content-Based'
    
    def __init__(self):
        self.dataset = Dataset()
        self.vec = Vectorizer()
        self.item_ids = self.vec.item_ids
        self.user_profiles = self.vec.build_users_profiles()
        self.items_df = self.dataset.get_dataframes()[0]
        
    def get_model_name(self):
        return self.MODEL_NAME
        
    def _get_similar_items_to_user_profile(self, person_id, topn=1000):
        cosine_similarities = cosine_similarity(self.user_profiles[person_id], self.vec.tfidf_matrix)
        similar_indices = cosine_similarities.argsort().flatten()[-topn:]
        similar_items = sorted([(self.item_ids[i], cosine_similarities[0,i]) for i in similar_indices], key=lambda x: -x[1])
        return similar_items
        
    def recommend_items(self, user_id, items_to_ignore=[], topn=10, verbose=False):
        similar_items = self._get_similar_items_to_user_profile(user_id)
        similar_items_filtered = list(filter(lambda x: x[0] not in items_to_ignore, similar_items))
        
        recommendations_df = pd.DataFrame(similar_items_filtered, columns=['contentId', 'recStrength']) \
                                    .head(topn)

        if verbose:
            if self.items_df is None:
                raise Exception('"items_df" is required in verbose mode')

            recommendations_df = recommendations_df.merge(self.items_df, how = 'left', 
                                                          left_on = 'contentId', 
                                                          right_on = 'contentId')[['recStrength', 'contentId', 'title']]


        return recommendations_df

class CFRecommender:
    
    MODEL_NAME = 'Collaborative Filtering'
    NUMBER_OF_FACTORS_MF = 15
    
    def __init__(self):
        self.dataset = Dataset()
        self.interactions_train_df, self.interactions_test_df, self.interactions_full_indexed_df, self.interactions_train_indexed_df, self.interactions_test_indexed_df = self.dataset.perform_evaluation()
        users_items_pivot_matrix_df = self.interactions_train_df.pivot(index='personId', 
                                                          columns='contentId', 
                                                          values='eventStrength').fillna(0)

        users_items_pivot_matrix = users_items_pivot_matrix_df.as_matrix()
        users_ids = list(users_items_pivot_matrix_df.index)
        all_user_predicted_ratings = users_items_pivot_matrix
        if min(users_items_pivot_matrix.shape) > 1 and min(users_items_pivot_matrix.shape) < self.NUMBER_OF_FACTORS_MF:
            U, sigma, Vt = svds(users_items_pivot_matrix, k=min(users_items_pivot_matrix.shape))
            all_user_predicted_ratings = np.dot(np.dot(U, sigma), Vt)
        elif min(users_items_pivot_matrix.shape) > 1 and min(users_items_pivot_matrix.shape) > self.NUMBER_OF_FACTORS_MF:
            U, sigma, Vt = svds(users_items_pivot_matrix, k=self.NUMBER_OF_FACTORS_MF)
            all_user_predicted_ratings = np.dot(np.dot(U, sigma), Vt)
        self.cf_predictions_df = pd.DataFrame(all_user_predicted_ratings, columns = users_items_pivot_matrix_df.columns, index=users_ids).transpose()
        self.items_df = self.dataset.get_dataframes()[0]
        
    def get_model_name(self):
        return self.MODEL_NAME
        
    def recommend_items(self, user_id, items_to_ignore=[], topn=10, verbose=False):
        sorted_user_predictions = self.cf_predictions_df[user_id].sort_values(ascending=False) \
                                    .reset_index().rename(columns={user_id: 'recStrength'})

        recommendations_df = sorted_user_predictions[~sorted_user_predictions['contentId'].isin(items_to_ignore)] \
                               .sort_values('recStrength', ascending = False) \
                               .head(topn)

        if verbose:
            if self.items_df is None:
                raise Exception('"items_df" is required in verbose mode')

            recommendations_df = recommendations_df.merge(self.items_df, how = 'left', 
                                                          left_on = 'contentId', 
                                                          right_on = 'contentId')[['recStrength', 'contentId', 'title']]


        return recommendations_df

class HybridRecommender:
    
    MODEL_NAME = 'Hybrid'
    
    def __init__(self, cb_rec_model, cf_rec_model):
        self.dataset = Dataset()
        self.cb_rec_model = cb_rec_model
        self.cf_rec_model = cf_rec_model
        self.items_df = self.dataset.get_dataframes()[0]
        
    def get_model_name(self):
        return self.MODEL_NAME
        
    def recommend_items(self, user_id, items_to_ignore=[], topn=10, verbose=False):
        cb_recs_df = self.cb_rec_model.recommend_items(user_id, items_to_ignore=items_to_ignore, verbose=verbose,
                                                           topn=1000).rename(columns={'recStrength': 'recStrengthCB'})
        
        cf_recs_df = self.cf_rec_model.recommend_items(user_id, items_to_ignore=items_to_ignore, verbose=verbose, 
                                                           topn=1000).rename(columns={'recStrength': 'recStrengthCF'})
        
        recs_df = cb_recs_df.merge(cf_recs_df,
                                   how = 'inner', 
                                   left_on = 'contentId', 
                                   right_on = 'contentId')
        
        recs_df['recStrengthHybrid'] = recs_df['recStrengthCB'] * recs_df['recStrengthCF']
        
        recommendations_df = recs_df.sort_values('recStrengthHybrid', ascending=False).head(topn)

        if verbose:
            if self.items_df is None:
                raise Exception('"items_df" is required in verbose mode')

            recommendations_df = recommendations_df.merge(self.items_df, how = 'left', 
                                                          left_on = 'contentId', 
                                                          right_on = 'contentId')[['recStrengthHybrid', 'contentId', 'title']]


        return recommendations_df


class PostRecommender:

    def checksetUp(self):
        dataset = Dataset()
        shared_posts = dataset.get_shared_posts()
        shared_posts_df, user_interactions_df = dataset.get_dataframes()
        users_interactions_count_df = user_interactions_df.groupby(['personId', 'contentId']).size().groupby('personId').size()
        if bool(len(shared_posts)) and len(users_interactions_count_df) >= USER_INTERACTIONS_COUNT:
            return True
        else:
            return False

    def setUp(self):
        try:
            with open('popularity_model.pickle', 'rb') as p:
                self.popularity_model = pickle.load(p)
            with open('content_based_model.pickle', 'rb') as p:
                self.content_based_recommender_model = pickle.load(p)
            with open('cf_recommender_model.pickle', 'rb') as p:
                self.cf_recommender_model = pickle.load(p)
            with open('hybrid_recommender_model.pickle', 'rb') as p:
                self.hybrid_recommender_model = pickle.load(p)
        except FileNotFoundError:
            self.pickle_recommenders()


    def pickle_recommenders(self):
        self.popularity_model = PopularityRecommender()
        self.content_based_recommender_model = ContentBasedRecommender()
        self.cf_recommender_model = CFRecommender()
        self.hybrid_recommender_model = HybridRecommender(self.content_based_recommender_model, self.cf_recommender_model)
        
        with open('popularity_model.pickle', 'wb') as p:
            pickle.dump(self.popularity_model, p)
        with open('content_based_model.pickle', 'wb') as p:
            pickle.dump(self.content_based_recommender_model, p)
        with open('cf_recommender_model.pickle', 'wb') as p:
            pickle.dump(self.cf_recommender_model, p)
        with open('hybrid_recommender_model.pickle', 'wb') as p:
            pickle.dump(self.hybrid_recommender_model, p)

    def get_popular_posts(self, topn):
        contentIds = self.popularity_model.recommend_items(topn=topn, verbose=True)["contentId"].tolist()
        posts = Post.objects.filter(pk__in=contentIds)
        return posts

    def get_recommended_posts(self, user_id, topn):
        contentIds = self.hybrid_recommender_model.recommend_items(user_id, topn=topn, verbose=True)["contentId"].tolist()
        posts = Post.objects.filter(pk__in=contentIds)
        return posts

