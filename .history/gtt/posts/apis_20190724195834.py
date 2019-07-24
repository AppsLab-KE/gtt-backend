from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.forms.models import model_to_dict
from .models import (
    Tag, Post, Comment, Reply, Rating, Bookmark, Archive
    )

User = get_user_model()

class ViewPost(APIView):
    def get(self, request, slug):
        user = User.objects.get(email=request.user)
        try:
            post = Post.objects.get(slug=slug)
            try:
                Rating.objects.get(rated_post__pk=post.id, user_that_rated__pk=user.id)
            except Rating.DoesNotExist:
                Rating.objects.create(rated_post=post, user_that_rated=user)
            return Response({
                "slug": post.slug,
                "post_heading": post.post_heading,
                "post_body": post.post_body,
                "post_author": model_to_dict(post.post_author, fields=['first_name', 'last_name', 'username', 'email', 'profile__avatar']),
                "tags": post.tags.all().values('tag_name'),
                "date_published": post.date_published,
                "comments_count": post.comments.all().count(),
                "ratings_count": post.ratings.filter(rating=True).count(),
            })
        except Post.DoesNotExist:
            return Response({
                "message": "Post was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class ViewRatedPosts(APIView):
    def get(self, request):
        user = User.objects.get(email=request.user)
        user_rated_posts = Post.objects.filter(user_that_rated__pk=user.id, rating__rating=True)
        response_list = list()
        for user_rated_post in user_rated_posts:
            user_post = {
                "slug": user_rated_post.slug,
                "post_heading": user_rated_post.post_heading,
                "post_author": model_to_dict(user_rated_post.post_author, fields=['first_name', 'last_name', 'username', 'email', 'profile__avatar']),
                "tags": user_rated_post.tags.all().values('tag_name'),
                "date_published": user_rated_post.date_published,
                "comments_count": user_rated_post.comments.all().count(),
                "ratings_count": user_rated_post.ratings.filter(rating=True).count(),
            }
            response_list.append(user_post)
        return Response(response_list)

class ViewRecommendedPosts(APIView):
    def get(self, request):
        pass

class CreatePost(APIView):
    def post(self, request):
        post_heading = request.data.get('post_heading')
        post_body = request.data.get('post_body')
        tags = request.data.getlist('tag')
        user = User.objects.get(email=request.user)
        tag_instance_list = []
        for tag in tags:
            try:
                tag = Tag.objects.get(tag_name__iexact=tag)
                tag_instance_list.append(tag)
            except Tag.DoesNotExist:
                tag = Tag.objects.create(tag_name=tag.capitalize())
                tag_instance_list.append(tag)
        post = Post.objects.create(post_heading=post_heading, post_body=post_body, post_author=user)
        post.tags.add(*tag_instance_list)
        return Response({
            "message": "That post was created.",
        })

class DeletePost(APIView):
    def post(self, request, slug):
        try:
            post = Post.objects.get(slug=slug)
            post.update({'archived': True})
            post.save()
            return Response({
                "message": "Your post was deleted.",
            })
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
        user = User.objects.get(email=request.user)
        try:
            post = Post.objects.get(slug=slug)
            try:
                rating = Rating.objects.get(rated_post__pk=post.id, user_that_rated__pk=user.id)
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

class ViewComments(APIView):
    def get(self, request, slug):
        comments = Comment.objects.filter(commented_post__slug=slug)
        response_list = list()
        for comment in comments:
            comment = {
                "resource_token": comment.resource_key,
                "user_that_commented": model_to_dict(comment.user_that_commented, fields=['first_name', 'last_name', 'username', 'email', 'profile__avatar']),
                "comment": comment.comment,
                "date_commented": comment.date_commented,
                "replies_count": comment.replies.count(),
            }
            response_list.append(comment)
        return Response(response_list)

class CreateComment(APIView):
    def post(self, request, slug):
        comment = request.data.get('comment')
        user = User.objects.get(email=request.user)
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
            comment = Comment.objects.get(resource_key=resource_key)
            comment.update({'comment': comment})
            comment.save()
            return Response({
                "message": "Your comment for this post was updated.",
            })
        except Comment.DoesNotExist:
            return Response({
                "message": "That comment was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class DeleteComment(APIView):
    def post(self, request, resource_key):
        comment = request.data.get('comment')
        try:
            comment = Comment.objects.get(resource_key=resource_key)
            comment.update({'archived': True})
            comment.save()
            return Response({
                "message": "Your comment for this post was deleted.",
            })
        except Comment.DoesNotExist:
            return Response({
                "message": "That comment was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class ViewReplies(APIView):
    def get(self, request, resource_key):
        replies = Reply.objects.filter(replied_comment__resource_key=resource_key)
        response_list = list()
        for reply in replies:
            reply = {
                "resource_token": reply.resource_key,
                "user_that_replied": model_to_dict(reply.user_that_replied, fields=['first_name', 'last_name', 'username', 'email', 'profile__avatar']),
                "reply": reply.reply,
                "date_replied": reply.date_replied,
            }
            response_list.append(comment)
        return Response(response_list)

class CreateReply(self, request):
    def post(self, request, resource_key):
        reply = request.data.get('reply')
        user = User.objects.get(email=request.user)
        try:
            comment = Comment.objects.get(resource_key=resource_key)
            Reply.objects.create(replied_comment=comment, user_that_replied=user, reply=reply)
            return Response({
                    "message": "Your reply was successful.",
                })
        except Comment.DoesNotExist:
            return Response({
                "message": "That comment was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class UpdateReply(self, request):
    def post(self, request, resource_key):
        reply = request.data.get('reply')
        try:
            reply = Reply.objects.get(resource_key=resource_key)
            reply.update({'reply': reply})
            reply.save()
            return Response({
                "message": "Your reply was updated.",
            })
        except Comment.DoesNotExist:
            return Response({
                "message": "That reply was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class DeleteReply(self, request):
    def post(self, request, resource_key):
        try:
            reply = Reply.objects.get(resource_key=resource_key)
            reply.update({'archived': True})
            reply.save()
            return Response({
                    "message": "Your reply was deleted.",
                })
        except Reply.DoesNotExist:
            return Response({
                "message": "That reply was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class ViewBookmarks(APIView):
    def get(self, request):
        pass

class CreateBookmark(APIView):
    def post(self, request, slug):
        user = User.objects.get(email=request.user)
        try:
            post = Post.objects.get(slug=slug)
            Bookmark.objects.create(user_that_bookmarked=user, bookmarked_post=post)
            return Response({
                    "message": "Your bookmark was created.",
                })
        except Post.DoesNotExist:
            return Response({
                "message": "That post was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class DeleteBookmark(APIView):
    def post(self, request, resource_key):
        try:
            bookmark = Bookmark.objects.get(resource_key=resource_key)
            bookmark.update({'archived': True})
            bookmark.save()
            return Response({
                    "message": "Your bookmark was deleted.",
                })
        except Post.DoesNotExist:
            return Response({
                "message": "That bookmark was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

