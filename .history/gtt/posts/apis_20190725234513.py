from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from guardian.shortcuts import assign_perm
from django.contrib.auth import get_user_model
from django.forms.models import model_to_dict
from .models import (
    Tag, Post, Comment, Reply, Rating, Bookmark,
)
from .permissions import (
    CanCreatePost, CanCreateComment, CanCreateReply, CanCreateBookmark,
)

User = get_user_model()

class ViewPost(APIView):
    permission_classes = []
    def get(self, request, username, slug):
        if request.user.is_authenticated:
            user = User.objects.get(email=request.user)
            try:
                post = Post.objects.get(slug=slug, post_author__username=username)
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
                    "read_duration": post.read_duration,
                    "date_published": post.date_published,
                    "comments_count": post.comments.all().count(),
                    "ratings_count": post.ratings.filter(rating=True).count(),
                })
            except Post.DoesNotExist:
                return Response({
                    "message": "That post was not found.",
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            try:
                post = Post.objects.get(slug=slug, post_author__username=username)
                return Response({
                    "slug": post.slug,
                    "post_heading": post.post_heading,
                    "post_body": post.post_body,
                    "post_author": model_to_dict(post.post_author, fields=['first_name', 'last_name', 'username', 'email', 'profile__avatar']),
                    "tags": post.tags.all().values('tag_name'),
                    "read_duration": post.read_duration,
                    "date_published": post.date_published,
                    "comments_count": post.comments.all().count(),
                    "ratings_count": post.ratings.filter(rating=True).count(),
                })
            except Post.DoesNotExist:
                return Response({
                    "message": "That post was not found.",
                }, status=status.HTTP_404_NOT_FOUND)

class ViewRatedPosts(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = User.objects.get(email=request.user)
        if 'offset' in request.data and 'limit' in request.data:
            offset = request.data.get('offset')
            limit = request.data.get('limit')
            user_rated_posts = Post.objects.filter(user_that_rated__pk=user.id, rating__rating=True)[offset:offset+limit]
        else:
            user_rated_posts = Post.objects.filter(user_that_rated__pk=user.id, rating__rating=True)
        response_list = list()
        for user_rated_post in user_rated_posts:
            user_post = {
                "slug": user_rated_post.slug,
                "post_heading": user_rated_post.post_heading,
                "post_author": model_to_dict(user_rated_post.post_author, fields=['first_name', 'last_name', 'username', 'email', 'profile__avatar']),
                "tags": user_rated_post.tags.all().values('tag_name'),
                "read_duration": user_rated_post.read_duration,
                "date_published": user_rated_post.date_published,
                "comments_count": user_rated_post.comments.all().count(),
                "ratings_count": user_rated_post.ratings.filter(rating=True).count(),
            }
            response_list.append(user_post)
        return Response(response_list)

class ViewTagPosts(APIView):
    def get(self, request, tag_name):
        try:
            tag = Tag.objects.get(tag_name__iexact=tag_name)
            if 'offset' in request.data and 'limit' in request.data:
                offset = request.data.get('offset')
                limit = request.data.get('limit')
                tag_posts = tag.posts.all()[offset:offset+limit]
            else:
                tag_posts = tag.posts.all()
            response_list = list()
            for tag_post in tag_posts:
                post = {
                    "slug": tag_post.slug,
                    "post_heading": tag_post.post_heading,
                    "post_author": model_to_dict(tag_post.post_author, fields=['first_name', 'last_name', 'username', 'email', 'profile__avatar']),
                    "tags": tag_post.tags.all().values('tag_name'),
                    "read_duration": tag_post.read_duration,
                    "date_published": tag_post.date_published,
                    "comments_count": tag_post.comments.all().count(),
                    "ratings_count": tag_post.ratings.filter(rating=True).count(),
                }
                response_list.append(post)
            return Response(response_list)
        except Tag.DoesNotExist:
            return Response({
                "message": "That tag was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class ViewRecommendedPosts(APIView):
    def get(self, request):
        pass

class CreatePost(APIView):
    permission_classes = [IsAuthenticated|CanCreatePost]
    def post(self, request):
        post_heading = request.data.get('post_heading')
        post_body = request.data.get('post_body')
        read_duration = request.data.get("read_duration")
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
        post = Post.objects.create(post_heading=post_heading, post_body=post_body, post_author=user, read_duration=str(read_duration) + " min")
        post.tags.add(*tag_instance_list)
        assign_perm('change_post', user, post)
        assign_perm('delete_post', user, post)
        return Response({
            "message": "That post was created.",
        })

class UpdatePost(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, slug):
        post_heading = request.data.get('post_heading')
        post_body = request.data.get('post_body')
        tags = request.data.getlist('tag')
        try:
            post = Post.objects.get(slug=slug)
            post.update({'post_heading': post_heading, 'post_body': post_body})
            post.save()
            tag_instance_list = []
            for tag in tags:
                try:
                    tag = Tag.objects.get(tag_name__iexact=tag)
                    tag_instance_list.append(tag)
                except Tag.DoesNotExist:
                    tag = Tag.objects.create(tag_name=tag.capitalize())
                    tag_instance_list.append(tag)
            post.tags.clear()
            post.tags.add(*tag_instance_list)
            return Response({
                "message": "That post was updated.",
            })
        except Post.DoesNotExist:
            return Response({
                "message": "That post was not found.",
            }, status=status.HTTP_404_NOT_FOUND)
            
class DeletePost(APIView):
    permission_classes = [IsAuthenticated]
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
                "message": "That post was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class RatePost(APIView):
    permission_classes = [IsAuthenticated]
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
                "message": "That post was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class ViewComments(APIView):
    def get(self, request, slug):
        if 'offset' in request.data and 'limit' in request.data:
            offset = request.data.get('offset')
            limit = request.data.get('limit')
            comments = Comment.objects.filter(commented_post__slug=slug)[offset:offset+limit]
        else:
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
    permission_classes = [IsAuthenticated|CanCreateComment]
    def post(self, request, slug):
        comment = request.data.get('comment')
        user = User.objects.get(email=request.user)
        try:
            post = Post.objects.get(slug=slug)
            comment = Comment.objects.create(commented_post=post, user_that_commented=user, comment=comment)
            assign_perm('change_comment', user, comment)
            assign_perm('delete_comment', user, comment)
            return Response({
                "message": "You commented on this post.",
            })
        except Post.DoesNotExist:
            return Response({
                "message": "That post was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class UpdateComment(APIView):
    permission_classes = [IsAuthenticated]
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
    permission_classes = [IsAuthenticated]
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
    permission_classes = [IsAuthenticated]
    def get(self, request, resource_key):
        if 'offset' in request.data and 'limit' in request.data:
            offset = request.data.get('offset')
            limit = request.data.get('limit')
            replies = Reply.objects.filter(replied_comment__resource_key=resource_key)[offset:offset+limit]
        else:
            replies = Reply.objects.filter(replied_comment__resource_key=resource_key)
        response_list = list()
        for reply in replies:
            reply = {
                "resource_token": reply.resource_key,
                "user_that_replied": model_to_dict(reply.user_that_replied, fields=['first_name', 'last_name', 'username', 'email', 'profile__avatar']),
                "reply": reply.reply,
                "date_replied": reply.date_replied,
            }
            response_list.append(reply)
        return Response(response_list)

class CreateReply(APIView):
    permission_classes = [IsAuthenticated|CanCreateReply]
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

class UpdateReply(APIView):
    permission_classes = [IsAuthenticated]
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

class DeleteReply(APIView):
    permission_classes = [IsAuthenticated]
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
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = User.objects.get(email=request.user)
        if 'offset' in request.data and 'limit' in request.data:
            offset = request.data.get('offset')
            limit = request.data.get('limit')
            bookmarks = Bookmark.objects.filter(user_that_bookmarked__pk=user.id)[offset:offset+limit]
        else:
            bookmarks = Bookmark.objects.filter(user_that_bookmarked__pk=user.id)
        response_list = list()
        for bookmark in bookmarks:
            fields = [
                'slug', 
                'post_heading',
                'post_author__first_name', 
                'post_author__last_name', 
                'post_author__username', 
                'post_author__email', 
                'post_author__profile__avatar', 
                'date_published',
                ]
            post_dict = model_to_dict(bookmark.bookmarked_post, fields=fields)
            reply = {
                'resource_token': bookmark.resource_key,
                'bookmarked_post': {
                    'slug': post_dict['slug'],
                    'post_heading': post_dict['post_heading'],
                    'post_author': {
                        'first_name': post_dict['first_name'],
                        'last_name': post_dict['last_name'],
                        'username': post_dict['username'],
                        'email': post_dict['email'],
                        'profile__avatar': post_dict['profile__avatar'],
                    },
                    'date_published': post_dict['date_published'],
                },
                'date_bookmarked': bookmark.date_bookmarked,
            }
            response_list.append(reply)
        return Response(response_list)

class CreateBookmark(APIView):
    permission_classes = [IsAuthenticated|CanCreateBookmark]
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
    permission_classes = [IsAuthenticated]
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

