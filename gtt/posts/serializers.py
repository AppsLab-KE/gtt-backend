from datetime import datetime
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Post, Comment, Reply, Bookmark, Rating
from .helpers import get_avatar_url

User = get_user_model()

class Event:
    content_shared = 'CONTENT_SHARED'
    viewed =  'VIEW'
    liked = 'LIKE'
    commented = 'COMMENT'
    bookmarked = 'BOOKMARK'

event = Event()

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

class RecommenderPostSerializer(serializers.ModelSerializer):
    timestamp = serializers.SerializerMethodField()
    eventType = serializers.SerializerMethodField()
    contentId = serializers.SerializerMethodField()
    authorPersonId = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    text = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            'timestamp',
            'eventType',
            'contentId',
            'authorPersonId',
            'url',
            'title',
            'text'
        )

    def get_timestamp(self, obj):
        return datetime.timestamp(obj.date_published)

    def get_eventType(self, obj):
        return event.content_shared

    def get_contentId(self, obj):
        return obj.id

    def get_authorPersonId(self, obj):
        return obj.post_author.id

    def get_url(self, obj):
        return settings.DOMAIN_URL + obj.get_absolute_url()

    def get_title(self, obj):
        return obj.post_heading

    def get_text(self, obj):
        return obj.post_body

class ViewedSerializer(serializers.ModelSerializer):
    timestamp = serializers.SerializerMethodField()
    eventType = serializers.SerializerMethodField()
    contentId = serializers.SerializerMethodField()
    personId = serializers.SerializerMethodField()

    class Meta:
        model = Rating
        fields = (
            'timestamp',
            'eventType',
            'contentId',
            'personId',
        )

    def get_timestamp(self, obj):
        return datetime.timestamp(obj.date_rated)

    def get_eventType(self, obj):
        return event.viewed

    def get_contentId(self, obj):
        return obj.rated_post.id

    def get_personId(self, obj):
        return obj.user_that_rated.id

class LikedSerializer(serializers.ModelSerializer):
    timestamp = serializers.SerializerMethodField()
    eventType = serializers.SerializerMethodField()
    contentId = serializers.SerializerMethodField()
    personId = serializers.SerializerMethodField()

    class Meta:
        model = Rating
        fields = (
            'timestamp',
            'eventType',
            'contentId',
            'personId',
        )
    
    def get_timestamp(self, obj):
        return datetime.timestamp(obj.date_rated)

    def get_eventType(self, obj):
        return event.liked

    def get_contentId(self, obj):
        return obj.rated_post.id

    def get_personId(self, obj):
        return obj.user_that_rated.id

class CommentedSerializer(serializers.ModelSerializer):
    timestamp = serializers.SerializerMethodField()
    eventType = serializers.SerializerMethodField()
    contentId = serializers.SerializerMethodField()
    personId = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            'timestamp',
            'eventType',
            'contentId',
            'personId',
        )

    def get_timestamp(self, obj):
        return datetime.timestamp(obj.date_commented)

    def get_eventType(self, obj):
        return event.commented

    def get_contentId(self, obj):
        return obj.commented_post.id

    def get_personId(self, obj):
        return obj.user_that_commented.id
    
class BookmarkedSerializer(serializers.ModelSerializer):
    timestamp = serializers.SerializerMethodField()
    eventType = serializers.SerializerMethodField()
    contentId = serializers.SerializerMethodField()
    personId = serializers.SerializerMethodField()

    class Meta:
        model = Bookmark
        fields = (
            'timestamp',
            'eventType',
            'contentId',
            'personId',
        )

    def get_timestamp(self, obj):
        return datetime.timestamp(obj.date_bookmarked)

    def get_eventType(self, obj):
        return event.bookmarked

    def get_contentId(self, obj):
        return obj.bookmarked_post.id

    def get_personId(self, obj):
        return obj.user_that_bookmarked.id