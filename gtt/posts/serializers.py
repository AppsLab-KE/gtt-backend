from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Post, Comment, Reply, Bookmark, Rating
from .helpers import get_avatar_url

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    user_avatar = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = (
            'first_name', 
            'last_name', 
            'username', 
            'email',
            'user_avatar',
        )

    def get_user_avatar(self, obj):
        if 'https' in obj.profile.avatar.url:
            return get_avatar_url('https://', obj.profile.avatar.url)
        elif 'http' in obj.profile.avatar.url:
            return get_avatar_url('http://', obj.profile.avatar.url)
        else:
            return settings.DOMAIN_URL + obj.profile.avatar.url

class ReplySerializer(serializers.ModelSerializer):
    user_that_replied = UserSerializer(read_only=True)
    class Meta:
        model = Reply
        fields = (
            'resource_key',
            'user_that_replied',
            'reply',
            'date_replied',
        )

class CommentSerializer(serializers.ModelSerializer):
    user_that_commented = UserSerializer(read_only=True)
    replies_count = serializers.SerializerMethodField()
    class Meta:
        model = Comment
        fields = (
            'resource_key',
            'user_that_commented',
            'comment',
            'date_commented',
            'replies_count',
        )

    def get_replies_count(self, obj):
        return obj.replies.count()

class PostSerializer(serializers.ModelSerializer):
    post_heading_image = serializers.SerializerMethodField()
    post_body_preview = serializers.SerializerMethodField()
    post_author = UserSerializer(read_only=True)
    tags = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    ratings_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            'slug',
            'post_heading',
            'post_heading_image',
            'post_body_preview',
            'post_author',
            'tags',
            'read_duration',
            'date_published',
            'comments_count',
            'ratings_count',
        )

    def get_post_heading_image(self, obj):
        return settings.DOMAIN_URL + obj.post_heading_image.url

    def get_post_body_preview(self, obj):
        return obj.post_body[:100] + "..."

    def get_tags(self, obj):
        return obj.tags.all().values('tag_name'),

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_ratings_count(self, obj):
        return obj.ratings.filter(rating=True).count()

class BookmarkSerializer(serializers.ModelSerializer):
    bookmarked_post = PostSerializer(read_only=True)
    
    class Meta:
        model = Bookmark
        fields = (
            'resource_key',
            'bookmarked_post',
            'date_bookmarked',
        )

class RatingSerializer(serializers.ModelSerializer):
    user_id = serializers.SerializerMethodField()
    post_id = serializers.SerializerMethodField()

    class Meta:
        model = Rating
        fields = (
            'user_id',
            'post_id',
            'rating',
        )

    def get_user_id(self, obj):
        return obj.user_that_rated.id

    def get_post_id(self, obj):
        return obj.rated_post.id