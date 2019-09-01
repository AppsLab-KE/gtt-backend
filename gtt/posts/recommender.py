from django.db.models import Q
from posts.models import Post, Rating, Comment, Bookmark
from posts.serializers import (
    RecommenderPostSerializer, ViewedSerializer, LikedSerializer, CommentedSerializer, BookmarkedSerializer,
)

class PostRecommender:

    def get_data(self):
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
        return (
            post_serializer.data,
            user_interactions
        )

    def get_shared_posts(self):
        return self.get_data()[0]

    def get_user_interactions(self):
        return self.get_data()[1]