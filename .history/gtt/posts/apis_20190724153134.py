from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.forms.models import model_to_dict
from .models import (
    Tag, Post, Comment, Reply, Rating, Bookmark, Archive
    )

class ViewPost(APIView):
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

class CreatePost(APIView):
    def post(self, request):
        pass

class DeletePost(APIView):
    def post(self, request, slug):
        try:
            post = Post.objects.get(slug=slug)
        except Post.DoesNotExist:
            return Response({
                "message": "Post was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class UpdatePost(APIView):
    def post(self, request, slug):
        try:
            post = Post.objects.get(slug=slug)
        except Post.DoesNotExist:
            return Response({
                "message": "Post was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class RatePost(APIView):
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

class CreateComment(APIView):
    def post(self, request, slug):
        comment = request.data.get('comment')
        try:
            post = Post.objects.get(slug=slug)
            Comment.objects.create(commented_post=post, user_that_commented=user, comment=comment)
            return Response({
                "message": "You commented on this post.",
            })
        except Post.DoesNotExist:
            return Response({
                "message": "Post was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class UpdateComment(APIView):
    def post(self, request, resource_key):
        comment = request.data.get('comment')
        try:
            post = Post.objects.get(slug=slug)
            try:
                comment = Comment.objects.get(resource_key=resource_key)
                comment.update({'comment': comment})
                comment.save()
                return Response({
                    "message": "Your commented for this post was updated.",
                })
            except Comment.DoesNotExist:
                return Response({
                    "message": "That comment was not found.",
                }, status=status.HTTP_404_NOT_FOUND)
        except Post.DoesNotExist:
            return Response({
                "message": "Post was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class DeleteComment(APIView):
    def post(self, request, resource_key):
        comment = request.data.get('comment')
        try:
            post = Post.objects.get(slug=slug)
            try:
                comment = Comment.objects.get(resource_key=resource_key)
                comment.update({'comment': comment})
                comment.save()
                return Response({
                    "message": "Your commented for this post was deleted.",
                })
            except Comment.DoesNotExist:
                return Response({
                    "message": "That comment was not found.",
                }, status=status.HTTP_404_NOT_FOUND)
        except Post.DoesNotExist:
            return Response({
                "message": "Post was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class CreateReply(self, request):
    def post(self, request):
        pass

class UpdateReply(self, request):
    def post(self, request):
        pass

class DeleteReply(self, request):
    def post(self, request):
        pass

class CreateBookmark(APIView):
    def post(self, request, slug):
        try:
            post = Post.objects.get(slug=slug)
        except Post.DoesNotExist:
            return Response({
                "message": "Post was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class DeleteBookmark(APIView):
    def post(self, request, slug):
        try:
            post = Post.objects.get(slug=slug)
        except Post.DoesNotExist:
            return Response({
                "message": "Post was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class CreateArchive(APIView):
    def post(self, request, slug):
        try:
            post = Post.objects.get(slug=slug)
        except Post.DoesNotExist:
            return Response({
                "message": "Post was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class DeleteArchive(APIView):
    def post(self, request, slug):
        try:
            post = Post.objects.get(slug=slug)
        except Post.DoesNotExist:
            return Response({
                "message": "Post was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

