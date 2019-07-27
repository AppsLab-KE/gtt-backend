import json
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from guardian.shortcuts import assign_perm
from django.conf import settings
from django.contrib.auth import get_user_model
from django.forms.models import model_to_dict
from django.utils.text import slugify
from .forms import (
    PostForm, RatingForm, CommentForm, ReplyForm,
)
from .models import (
    Tag, Post, Comment, Reply, Rating, Bookmark,
)
from .helpers import *

User = get_user_model()

class ViewPost(APIView):
    permission_classes = []
    def get(self, request, username, slug):
        try:
            post = Post.objects.get(slug=slug, post_author__username=username)
            if request.user.is_authenticated:
                user = User.objects.get(email=request.user)
                try:
                    Rating.objects.get(rated_post__pk=post.id, user_that_rated__pk=user.id)
                except Rating.DoesNotExist:
                    Rating.objects.create(rated_post=post, user_that_rated=user, resource_key=get_resource_key(Rating))
            post_author = model_to_dict(post.post_author, fields=['first_name', 'last_name', 'username', 'email'])
            post_author.update({'user_avatar': settings.DOMAIN_URL + post.post_author.profile.avatar.url})
            return Response({
                "slug": post.slug,
                "post_heading": post.post_heading,
                "post_heading_image": settings.DOMAIN_URL + post.post_heading_image.url,
                "post_body": post.post_body,
                "post_author": post_author,
                "tags": post.tags.all().values('tag_name'),
                "read_duration": post.read_duration,
                "date_published": post.date_published,
                "comments_count": post.comments.all().count(),
                "ratings_count": post.ratings.filter(rating=True).count(),
            })
        except Post.DoesNotExist:
            return Response({
                "details": "That post was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class ViewRatedPosts(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = User.objects.get(email=request.user)
        if 'offset' in request.data and 'limit' in request.data:
            offset = request.data.get('offset')
            limit = request.data.get('limit')
            user_rated_posts = Post.objects.filter( ratings__user_that_rated__pk=user.id, ratings__rating=True)[offset:offset+limit]
        else:
            user_rated_posts = Post.objects.filter( ratings__user_that_rated__pk=user.id, ratings__rating=True)
        response_list = list()
        for user_rated_post in user_rated_posts:
            post_author = model_to_dict(user_rated_post.post_author, fields=['first_name', 'last_name', 'username', 'email'])
            post_author.update({'user_avatar': settings.DOMAIN_URL + user_rated_post.post_author.profile.avatar.url})
            user_post = {
                "slug": user_rated_post.slug,
                "post_heading": user_rated_post.post_heading,
                "post_heading_image": settings.DOMAIN_URL + user_rated_post.post_heading_image.url,
                "post_author": post_author,
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
                post_author = model_to_dict(tag_post.post_author, fields=['first_name', 'last_name', 'username', 'email'])
                post_author.update({'user_avatar': settings.DOMAIN_URL + tag_post.post_author.profile.avatar.url})
                post = {
                    "slug": tag_post.slug,
                    "post_heading": tag_post.post_heading,
                    "post_heading_image": settings.DOMAIN_URL + tag_post.post_heading_image.url,
                    "post_author": post_author,
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
                "details": "That tag was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class ViewRecommendedPosts(APIView):
    def get(self, request):
        pass

class CreatePost(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        post_heading = request.data.get('post_heading')
        post_body = request.data.get('post_body')
        read_duration = request.data.get("read_duration")
        tags = request.data.getlist('tag')
        user = User.objects.get(email=request.user)
        if user.has_perm('posts.add_post'):
            post_form = PostForm({
                'post_heading': post_heading, 
                'post_body': post_body, 
                'read_duration': str(read_duration) + " min",
                'slug': get_slug_key(slugify(post_heading[:249])),
                }, request.FILES)
            if post_form.is_valid():
                post = post_form.save()
                post.post_author = user
                post.resource_key = get_resource_key(Post)
                post.save()
                tag_instance_list = []
                for tag in tags:
                    try:
                        tag = Tag.objects.get(tag_name__iexact=tag)
                        tag_instance_list.append(tag)
                    except Tag.DoesNotExist:
                        tag = Tag.objects.create(tag_name=tag.capitalize(), resource_key=get_resource_key(Tag), slug=slugify(tag.capitalize()[:249]))
                        tag_instance_list.append(tag)
                post.tags.add(*tag_instance_list)
                assign_perm('posts.change_post', user, post)
                assign_perm('posts.delete_post', user, post)
                return Response({
                    "details": "That post was created.",
                })
            else:
                return Response({
                    "details": json.loads(post_form.errors.as_json()),
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                    "details": "You cannot create a post.",
                }, status=status.HTTP_403_FORBIDDEN)

class UpdatePost(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, slug):
        post_heading = request.data.get('post_heading')
        post_body = request.data.get('post_body')
        read_duration = request.data.get("read_duration")
        tags = request.data.getlist('tag')
        user = User.objects.get(email=request.user)
        try:
            post = Post.objects.get(slug=slug)
            if user.has_perm('posts.change_post', post):
                post_form = PostForm({
                    'post_heading': post_heading, 
                    'post_body': post_body, 
                    'read_duration': str(read_duration) + " min",
                    'slug': post.slug,
                }, request.FILES, instance=post)
                tag_instance_list = []
                if post_form.is_valid():
                    post = post_form.save()
                    for tag in tags:
                        try:
                            tag = Tag.objects.get(tag_name__iexact=tag)
                            tag_instance_list.append(tag)
                        except Tag.DoesNotExist:
                            tag = Tag.objects.create(tag_name=tag.capitalize(), resource_key=get_resource_key(Tag), slug=slugify(tag.capitalize()))
                            tag_instance_list.append(tag)
                    post.tags.clear()
                    post.tags.add(*tag_instance_list)
                    return Response({
                        "details": "That post was updated.",
                    })
                else:
                    return Response({
                        "details": json.loads(post_form.errors.as_json()),
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    "details": "You cannot update this post.",
                }, status=status.HTTP_403_FORBIDDEN)
        except Post.DoesNotExist:
            return Response({
                "details": "That post was not found.",
            }, status=status.HTTP_404_NOT_FOUND)
            
class DeletePost(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, slug):
        user = User.objects.get(email=request.user)
        try:
            post = Post.objects.get(slug=slug)
            if user.has_perm('posts.delete_post', post):
                post.update({'archived': True})
                post.save()
                return Response({
                    "details": "Your post was deleted.",
                })
            else:
                return Response({
                    "details": "That cannot delete that post.",
                }, status=status.HTTP_403_FORBIDDEN)
        except Post.DoesNotExist:
            return Response({
                "details": "That post was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class RatePost(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, slug):
        rated = bool(int(request.data.get('rating')))
        user = User.objects.get(email=request.user)
        try:
            post = Post.objects.get(slug=slug)
            try:
                rating = Rating.objects.get(rated_post__pk=post.id, user_that_rated__pk=user.id)
                rating_form = RatingForm({
                    'rating': rated,
                }, instance=rating)
                if rating_form.is_valid():
                    rating_form.save()
                    if rated:
                        return Response({
                            "details": "You liked this post.",
                        })
                    else:
                        return Response({
                            "details": "You disliked this post.",
                        })
                else:
                    return Response({
                        "details": json.loads(rating_form.errors.as_json()),
                    }, status=status.HTTP_400_BAD_REQUEST)
            except Rating.DoesNotExist:
                return Response({
                "details": "Rating was not successful.",
            }, status=status.HTTP_404_NOT_FOUND)
        except Post.DoesNotExist:
            return Response({
                "details": "That post was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class ViewComments(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, slug):
        if 'offset' in request.data and 'limit' in request.data:
            offset = request.data.get('offset')
            limit = request.data.get('limit')
            comments = Comment.objects.filter(commented_post__slug=slug)[offset:offset+limit]
        else:
            comments = Comment.objects.filter(commented_post__slug=slug)
        response_list = list()
        for comment in comments:
            commentor = model_to_dict(comment.user_that_commented, fields=['first_name', 'last_name', 'username', 'email'])
            commentor.update({'user_avatar': settings.DOMAIN_URL + comment.user_that_commented.profile.avatar.url})
            comment = {
                "resource_token": comment.resource_key,
                "user_that_commented": commentor,
                "comment": comment.comment,
                "date_commented": comment.date_commented,
                "replies_count": comment.replies.count(),
            }
            response_list.append(comment)
        return Response(response_list)

class CreateComment(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, slug):
        comment = request.data.get('comment')
        user = User.objects.get(email=request.user)
        try:
            post = Post.objects.get(slug=slug)
            comment_form = CommentForm({
                'comment': comment,
            })
            if comment_form.is_valid():
                comment = comment_form.save()
                comment.commented_post = post
                comment.user_that_commented = user
                comment.resource_key = get_resource_key(Comment)
                comment.save()
                assign_perm('posts.change_comment', user, comment)
                assign_perm('posts.delete_comment', user, comment)
                return Response({
                    "details": "You commented on this post.",
                })
            else:
                return Response({
                    "details": json.loads(comment_form.errors.as_json()),
                }, status=status.HTTP_400_BAD_REQUEST)
        except Post.DoesNotExist:
            return Response({
                "details": "That post was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class UpdateComment(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, resource_key):
        comment = request.data.get('comment')
        user = User.objects.get(email=request.user)
        try:
            comment_instance = Comment.objects.get(resource_key=resource_key)
            if user.has_perm('posts.change_comment', comment_instance):
                comment_form = CommentForm({
                    'comment': comment,
                }, instance=comment_instance)
                if comment_form.is_valid():
                    comment_form.save()
                    return Response({
                        "details": "Your comment for this post was updated.",
                    })
                else:
                    return Response({
                        "details": json.loads(comment_form.errors.as_json()),
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    "details": "You cannot update this comment.",
                }, status=status.HTTP_403_FORBIDDEN)
        except Comment.DoesNotExist:
            return Response({
                "details": "That comment was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class DeleteComment(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, resource_key):
        comment = request.data.get('comment')
        user = User.objects.get(email=request.user)
        try:
            comment = Comment.objects.get(resource_key=resource_key)
            if user.has_perm('posts.delete_comment', comment):
                comment.update({'archived': True})
                comment.save()
                return Response({
                    "details": "Your comment for this post was deleted.",
                })
            else:
                return Response({
                    "details": "That cannot delete that comment.",
                }, status=status.HTTP_403_FORBIDDEN)
        except Comment.DoesNotExist:
            return Response({
                "details": "That comment was not found.",
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
    permission_classes = [IsAuthenticated]
    def post(self, request, resource_key):
        reply = request.data.get('reply')
        user = User.objects.get(email=request.user)
        try:
            comment = Comment.objects.get(resource_key=resource_key)
            reply_form = ReplyForm({
                'reply': reply,
            })
            if reply_form.is_valid():
                reply = reply_form.save()
                reply.replied_comment = comment
                reply.user_that_replied = user
                reply.resource_key = get_resource_key(Reply)
                reply.save()
                assign_perm('posts.change_reply', user, reply)
                assign_perm('posts.delete_reply', user, reply)
                return Response({
                    "details": "Your reply was successful.",
                })
            else:
                return Response({
                    "details": json.loads(reply_form.errors.as_json()),
                }, status=status.HTTP_400_BAD_REQUEST)
        except Comment.DoesNotExist:
            return Response({
                "details": "That comment was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class UpdateReply(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, resource_key):
        reply = request.data.get('reply')
        user = User.objects.get(email=request.user)
        try:
            reply = Reply.objects.get(resource_key=resource_key)
            if user.has_perm('posts.change_reply', reply):
                reply_form = ReplyForm({
                    'reply': reply,
                }, instance=reply)
                if reply_form.is_valid():
                    reply_form.save()
                    return Response({
                        "details": "Your reply was updated.",
                    })
                else:
                    return Response({
                        "details": json.loads(reply_form.errors.as_json()),
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    "details": "That cannot update that reply.",
                }, status=status.HTTP_403_FORBIDDEN)
        except Reply.DoesNotExist:
            return Response({
                "details": "That reply was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class DeleteReply(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, resource_key):
        user = User.objects.get(email=request.user)
        try:
            reply = Reply.objects.get(resource_key=resource_key)
            if user.has_perm('posts.delete_reply', reply):
                reply.update({'archived': True})
                reply.save()
                return Response({
                    "details": "Your reply was deleted.",
                })
            else:
                return Response({
                    "details": "That cannot delete that reply.",
                }, status=status.HTTP_403_FORBIDDEN)
        except Reply.DoesNotExist:
            return Response({
                "details": "That reply was not found.",
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
            post_author = model_to_dict(bookmark.bookmarked_post.post_author, fields=['first_name', 'last_name', 'username', 'email'])
            post_author.update({'user_avatar': settings.DOMAIN_URL + bookmark.bookmarked_post.post_author.profile.avatar.url})
            reply = {
                'resource_token': bookmark.resource_key,
                'bookmarked_post': {
                    'slug': bookmark.bookmarked_post.slug,
                    'post_heading': bookmark.bookmarked_post.post_heading,
                    "post_heading_image": settings.DOMAIN_URL + bookmark.bookmarked_post.post_heading_image.url,
                    'post_author': post_author,
                    "tags": bookmark.bookmarked_post.tags.all().values('tag_name'),
                    "read_duration": bookmark.bookmarked_post.read_duration,
                    'date_published':bookmark.bookmarked_post.date_published,
                    "comments_count": bookmark.bookmarked_post.comments.all().count(),
                    "ratings_count": bookmark.bookmarked_post.ratings.filter(rating=True).count(),
                },
                'date_bookmarked': bookmark.date_bookmarked,
            }
            response_list.append(reply)
        return Response(response_list)

class CreateBookmark(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, slug):
        user = User.objects.get(email=request.user)
        try:
            post = Post.objects.get(slug=slug)
            bookmark = Bookmark.objects.create(user_that_bookmarked=user, bookmarked_post=post, resource_key=get_resource_key(Bookmark))
            assign_perm('posts.change_bookmark', user, bookmark)
            assign_perm('posts.delete_bookmark', user, bookmark)
            return Response({
                    "details": "Your bookmark was created.",
                })
        except Post.DoesNotExist:
            return Response({
                "details": "That post was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class DeleteBookmark(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, resource_key):
        user = User.objects.get(email=request.user)
        try:
            bookmark = Bookmark.objects.get(resource_key=resource_key)
            if user.has_perm('posts.delete_bookmark', bookmark):
                bookmark.update({'archived': True})
                bookmark.save()
                return Response({
                    "details": "Your bookmark was deleted.",
                })
            else:
                return Response({
                    "details": "That cannot delete that bookmark.",
                }, status=status.HTTP_403_FORBIDDEN)
        except Bookmark.DoesNotExist:
            return Response({
                "details": "That bookmark was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

