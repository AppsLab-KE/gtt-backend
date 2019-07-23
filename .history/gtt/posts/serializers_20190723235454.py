from rest_framework import serializers
from .models import (
    Tag, Post, Comment, Reply, Rating, Bookmark, Archive)

class TagSerializer(serializers.ModelSerializer)
    class Meta:
        model=Tag

class PostSerializer(serializers.Serializer)
    class Meta:
        model=Post

class CommentSerializer(serializers.Serializer)
    class Meta:
        model=Comment

class ReplySerializer(serializers.Serializer)
    class Meta:
        model=Reply

class RatingSerializer(serializers.Serializer)
    class Meta:
        model=Rating

class BookmarkSerializer(serializers.Serializer)
    class Meta:
        model=Bookmark

class ArchiveSerializer(serializers.Serializer)
    class Meta:
        model=Archive