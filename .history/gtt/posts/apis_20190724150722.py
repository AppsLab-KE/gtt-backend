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
                "tags": post.tags.all().values('tag_name'),
                "date_published": post.date_published,
                "comments_count": post.comments.all().count(),
                "ratings_count": post.ratings.all().count(),
            })
        except Post.DoesNotExist:
            return Response({
                "message": "Post was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class Create(APIView):
    def post(self, request):
        pass

class Delete(APIView):
    def post(self, request, slug):
        try:
            post = Post.objects.get(slug=slug)
        except Post.DoesNotExist:
            return Response({
                "message": "Post was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class Update(APIView):
    def post(self, request, slug):
        try:
            post = Post.objects.get(slug=slug)
        except Post.DoesNotExist:
            return Response({
                "message": "Post was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class Rate(APIView):
    def post(self, request, slug):
        rated = bool(request.data.get('rating'))
        try:
            post = Post.objects.get(slug=slug)
            try:
                rating = Rating.objects.get(rated_post.pk=post.id, user_that_rated.pk=user.id)
                rating.update({'rating': rated})
                rating.save()
                if rated:
                    return Response({
                        "message": "You liked this post.",
                    })
                else:
                    return Response({
                        "message": "You disliked this post",
                    })
            except Rating.DoesNotExist:
                return Response({
                "message": "Rating was not successful.",
            }, status=status.HTTP_404_NOT_FOUND)
        except Post.DoesNotExist:
            return Response({
                "message": "Post was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class Comment(APIView):
    def post(self, request, slug):
        comment = request.data.get('comment')
        try:
            post = Post.objects.get(slug=slug)
            Comment.objects.update_or_create(commented_post=post, user_that_commented=user, defaults={'comment' : comment})
        except Post.DoesNotExist:
            return Response({
                "message": "Post was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class Reply(self, request):
    def post(self, request):
        pass

class Bookmark(APIView):
    def post(self, request, slug):
        try:
            post = Post.objects.get(slug=slug)
        except Post.DoesNotExist:
            return Response({
                "message": "Post was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class Archive(APIView):
    def post(self, request, slug):
        try:
            post = Post.objects.get(slug=slug)
        except Post.DoesNotExist:
            return Response({
                "message": "Post was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

