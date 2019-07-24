from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.forms.models import model_to_dict
from .models import (
    Tag, Post, Comment, Reply, Rating, Bookmark, Archive
    )

class View(APIView):
    def get(self, request, slug):
        try:
            post = Post.objects.get(slug=slug)
            post_author = model_to_dict(post.post_author, fields=['first_name', 'last_name', 'username', 'email', 'profile__avatar'])
            return Response({
                "post_heading": post.post_heading,
                "post_body": post.post_body,
                "post_author": post_author.update({'profile_url': post.post_author.get_absolute_url()}),
                "tags": post.tags.all().value('tag_name'),
                "date_published": post.date_published,
                "comment_count": post.comments.all().count(),
            })
        except Post.DoesNotExist:
            return Response({
                "message": "Post was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class Create(APIView):
    def post(self, request):

class Delete(APIView):
    def post(self, request, slug):

class Update(APIView):
    def post(self, request, slug):

class Rate(APIView):
    def post(self, request, slug):

class Comment(APIView):
    def post(self, request, slug):

class Reply(self, request):
    def post(self, request):

class Bookmark(APIView):
    def post(self, request, slug):

class Archive(APIView):
    def post(self, request, slug):

