import numpy as np
from lightfm import LightFM
from django.db.models import Q
from posts.models import Post, Rating
from posts.serializers import PostSerializer, RatingSerializer

class PostRecommender:

    def get_data(self):
        ratings = Rating.objects.all()
        posts = Post.objects.filter(Q(ratings__rating=True)|Q(ratings__rating=False))
        rating_serializer = RatingSerializer(ratings, many=True)
        post_serializer = PostSerializer(posts, many=True)
        return (
            rating_serializer.data,
            post_serializer.data
        )

    def get_ratings(self):
        return self.get_data()[0]

    def get_post_features(self):
        return self.get_data()[1]
