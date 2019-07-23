from rest_framework import serializers
from .models import (
    Tag, Post, Comment, Reply, Rating, Bookmark, Archive
    )

class TagSerializer(serializers.ModelSerializer)
    class Meta:
        model = Tag
        fields = ('tag_name')

class PostSerializer(serializers.ModelSerializer)
    class Meta:
        model = Post
        fields = ('post_heading', 'post_body', 'post_author', 'tags')

class CommentSerializer(serializers.ModelSerializer)
    class Meta:
        model = Comment
        fields = ('commented_post', 'user_that_commented', 'comment')

class ReplySerializer(serializers.ModelSerializerr)
    class Meta:
        model = Reply
        fields = ('replied_comment', 'user_that_replied', 'reply')

class RatingSerializer(serializers.ModelSerializer)
    class Meta:
        model = Rating
        fields = ('rated_post', 'user_that_rated', 'rating' = models.BooleanField(default=False))

class BookmarkSerializer(serializers.ModelSerializer)
    class Meta:
        model = Bookmark
        fields = ('user_that_bookmarked', 'bookmarked_post')

class ArchiveSerializer(serializers.ModelSerializer)
    class Meta:
        model = Archive
        fields = ('user_that_archived', 'archived_post')