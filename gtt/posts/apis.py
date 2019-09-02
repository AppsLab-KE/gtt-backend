import json
from rest_framework import generics
from rest_framework import filters
from rest_framework import status
from .paginator import LimitOffsetPaginationWithDefault
from rest_framework.views import APIView
from rest_framework.response import Response
from guardian.shortcuts import assign_perm
from django.conf import settings
from django.contrib.auth import get_user_model
from django.forms.models import model_to_dict
from django.utils.text import slugify
from .forms import (
    PostForm, RatingForm, CommentForm, ReplyForm,
)
from .serializers import (
    CommentSerializer, ReplySerializer, PostSerializer, BookmarkSerializer,
)
from .models import (
    Tag, Post, Comment, Reply, Rating, Bookmark,
)
from .recommender import PostRecommender
from .helpers import *

User = get_user_model()
recommender = PostRecommender()

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
            serializer = PostSerializer(instance=post)
            return Response(serializer.data)
        except Post.DoesNotExist:
            return Response({
                "detail": "That post was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class ViewRatedPosts(APIView):
    def get(self, request):
        user = User.objects.get(email=request.user)
        user_rated_posts = Post.objects.filter(ratings__user_that_rated__pk=user.id, ratings__rating=True)
        paginator = LimitOffsetPaginationWithDefault()
        context = paginator.paginate_queryset(user_rated_posts, request)
        serializer = PostSerializer(context, many=True)
        return paginator.get_paginated_response(serializer.data)

class ViewTagPosts(APIView):
    permission_classes = []
    def get(self, request, tag_name):
        try:
            tag = Tag.objects.get(tag_name__iexact=tag_name)
            tag_posts = tag.posts.all()
            paginator = LimitOffsetPaginationWithDefault()
            context = paginator.paginate_queryset(tag_posts, request)
            serializer = PostSerializer(context, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Tag.DoesNotExist:
            return Response({
                "detail": "That tag was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class ViewPopularPosts(APIView):
    permission_classes = []
    def get(self, request):
        top_n = request.GET.get('top_n', 10)
        popular_posts = recommender.get_popular_posts(topn=int(top_n))
        paginator = LimitOffsetPaginationWithDefault()
        context = paginator.paginate_queryset(popular_posts, request)
        serializer = PostSerializer(context, many=True)
        return paginator.get_paginated_response(serializer.data)

class ViewRecommendedPosts(APIView):
    def get(self, request):
        top_n = request.GET.get('top_n', 10)
        user = User.objects.get(email=request.user)
        try:
            popular_posts = recommender.get_recommended_posts(user_id=user.id, topn=int(top_n))
            paginator = LimitOffsetPaginationWithDefault()
            context = paginator.paginate_queryset(popular_posts, request)
            serializer = PostSerializer(context, many=True)
            return paginator.get_paginated_response(serializer.data)
        except KeyError:
            return Response({
                "detail": "Sorry. No recommendations available for you.",
            }, status=status.HTTP_204_NO_CONTENT)

class SearchPosts(generics.ListCreateAPIView):
    permission_classes = []
    search_fields = ['tags__tag_name', 'post_author__first_name', 'post_author__last_name', 'post_author__username', 'post_heading', 'post_body']
    filter_backends = (filters.SearchFilter,)
    queryset = Post.objects.all()
    serializer_class = PostSerializer


class CreatePost(APIView):
    def post(self, request):
        post_heading = request.data.get('post_heading')
        post_body = request.data.get('post_body')
        read_duration = request.data.get("read_duration")
        tags = request.data.getlist('tag')
        user = User.objects.get(email=request.user)
        if 'post_heading_image' in request.FILES:
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
                    serializer = PostSerializer(instance=post)
                    return Response({
                        "detail": "That post was created.",
                        "post": serializer.data,
                    })
                else:
                    return Response({
                        "detail": json.loads(post_form.errors.as_json()),
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    "detail": "You cannot create a post.",
                }, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({
                    "detail": {
                        "post_heading_image": [
                            {
                                "message": "This field is required.",
                                "code": "required",
                            }
                        ]
                    },
                }, status=status.HTTP_400_BAD_REQUEST)

class UpdatePost(APIView):
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
                    updated_post = post_form.save()
                    for tag in tags:
                        try:
                            tag = Tag.objects.get(tag_name__iexact=tag)
                            tag_instance_list.append(tag)
                        except Tag.DoesNotExist:
                            tag = Tag.objects.create(tag_name=tag.capitalize(), resource_key=get_resource_key(Tag), slug=slugify(tag.capitalize()))
                            tag_instance_list.append(tag)
                    updated_post.tags.clear()
                    updated_post.tags.add(*tag_instance_list)
                    serializer = PostSerializer(instance=updated_post)
                    return Response({
                        "detail": "That post was updated.",
                        "post": serializer.data,
                    })
                else:
                    return Response({
                        "detail": json.loads(post_form.errors.as_json()),
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    "detail": "You cannot update this post.",
                }, status=status.HTTP_403_FORBIDDEN)
        except Post.DoesNotExist:
            return Response({
                "detail": "That post was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class DeletePost(APIView):
    def post(self, request, slug):
        user = User.objects.get(email=request.user)
        try:
            post = Post.objects.get(slug=slug)
            if user.has_perm('posts.delete_post', post):
                post.archived = True
                post.save()
                comments = list(post.comments.all())
                for comment in comments:
                    comment.archived = True
                    replies = list(comment.replies.all())
                    for reply in replies:
                        reply.archived = True
                    Reply.objects.bulk_update(replies, ['archived'])
                Comment.objects.bulk_update(comments, ['archived'])
                ratings = list(post.ratings.all())
                bookmarks = list(post.bookmarks.all())
                for rating in ratings:
                    rating.archived = True
                Rating.objects.bulk_update(ratings, ['archived'])
                for bookmark in bookmarks:
                    bookmark.archived = True
                Bookmark.objects.bulk_update(bookmarks, ['archived'])
                return Response({
                    "detail": "Your post was deleted.",
                })
            else:
                return Response({
                    "detail": "That cannot delete that post.",
                }, status=status.HTTP_403_FORBIDDEN)
        except Post.DoesNotExist:
            return Response({
                "detail": "That post was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class RatePost(APIView):
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
                            "detail": "You liked this post.",
                        })
                    else:
                        return Response({
                            "detail": "You disliked this post.",
                        })
                else:
                    return Response({
                        "detail": json.loads(rating_form.errors.as_json()),
                    }, status=status.HTTP_400_BAD_REQUEST)
            except Rating.DoesNotExist:
                return Response({
                "detail": "Rating was not successful.",
            }, status=status.HTTP_404_NOT_FOUND)
        except Post.DoesNotExist:
            return Response({
                "detail": "That post was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class ViewComments(APIView):
    def get(self, request, slug):
        comments = Comment.objects.filter(commented_post__slug=slug)
        paginator = LimitOffsetPaginationWithDefault()
        context = paginator.paginate_queryset(comments, request)
        serializer = CommentSerializer(context, many=True)
        return paginator.get_paginated_response(serializer.data)

class CreateComment(APIView):
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
                serializer = CommentSerializer(instance=comment)
                return Response({
                    "detail": "You commented on this post.",
                    "comment": serializer.data,
                })
            else:
                return Response({
                    "detail": json.loads(comment_form.errors.as_json()),
                }, status=status.HTTP_400_BAD_REQUEST)
        except Post.DoesNotExist:
            return Response({
                "detail": "That post was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class UpdateComment(APIView):
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
                    updated_comment = comment_form.save()
                    serializer = CommentSerializer(instance=updated_comment)
                    return Response({
                        "detail": "Your comment for this post was updated.",
                        "comment": serializer.data,
                    })
                else:
                    return Response({
                        "detail": json.loads(comment_form.errors.as_json()),
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    "detail": "You cannot update this comment.",
                }, status=status.HTTP_403_FORBIDDEN)
        except Comment.DoesNotExist:
            return Response({
                "detail": "That comment was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class DeleteComment(APIView):
    def post(self, request, resource_key):
        comment = request.data.get('comment')
        user = User.objects.get(email=request.user)
        try:
            comment = Comment.objects.get(resource_key=resource_key)
            if user.has_perm('posts.delete_comment', comment):
                comment.archived = True
                comment.save()
                replies = list(comment.replies.all())
                for reply in replies:
                    reply.archived = True
                Reply.objects.bulk_update(replies, ['archived'])
                return Response({
                    "detail": "Your comment for this post was deleted.",
                })
            else:
                return Response({
                    "detail": "That cannot delete that comment.",
                }, status=status.HTTP_403_FORBIDDEN)
        except Comment.DoesNotExist:
            return Response({
                "detail": "That comment was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class ViewReplies(APIView):
    def get(self, request, resource_key):
        replies = Reply.objects.filter(replied_comment__resource_key=resource_key)
        paginator = LimitOffsetPaginationWithDefault()
        context = paginator.paginate_queryset(replies, request)
        serializer = ReplySerializer(context, many=True)
        return paginator.get_paginated_response(serializer.data)

class CreateReply(APIView):
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
                serializer = ReplySerializer(instance=reply)
                return Response({
                    "detail": "Your reply was successful.",
                    "reply": serializer.data,
                })
            else:
                return Response({
                    "detail": json.loads(reply_form.errors.as_json()),
                }, status=status.HTTP_400_BAD_REQUEST)
        except Comment.DoesNotExist:
            return Response({
                "detail": "That comment was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class UpdateReply(APIView):
    def post(self, request, resource_key):
        reply = request.data.get('reply')
        user = User.objects.get(email=request.user)
        try:
            reply_instance = Reply.objects.get(resource_key=resource_key)
            if user.has_perm('posts.change_reply', reply_instance):
                reply_form = ReplyForm({
                    'reply': reply,
                }, instance=reply_instance)
                if reply_form.is_valid():
                    updated_reply = reply_form.save()
                    serializer = ReplySerializer(instance=updated_reply)
                    return Response({
                        "detail": "Your reply was updated.",
                        "comment": serializer.data,
                    })
                else:
                    return Response({
                        "detail": json.loads(reply_form.errors.as_json()),
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    "detail": "That cannot update that reply.",
                }, status=status.HTTP_403_FORBIDDEN)
        except Reply.DoesNotExist:
            return Response({
                "detail": "That reply was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class DeleteReply(APIView):
    def post(self, request, resource_key):
        user = User.objects.get(email=request.user)
        try:
            reply = Reply.objects.get(resource_key=resource_key)
            if user.has_perm('posts.delete_reply', reply):
                reply.archived = True
                reply.save()
                return Response({
                    "detail": "Your reply was deleted.",
                })
            else:
                return Response({
                    "detail": "That cannot delete that reply.",
                }, status=status.HTTP_403_FORBIDDEN)
        except Reply.DoesNotExist:
            return Response({
                "detail": "That reply was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class ViewBookmarks(APIView):
    def get(self, request):
        user = User.objects.get(email=request.user)
        bookmarks = Bookmark.objects.filter(user_that_bookmarked__pk=user.id)
        paginator = LimitOffsetPaginationWithDefault()
        context = paginator.paginate_queryset(bookmarks, request)
        serializer = BookmarkSerializer(context, many=True)
        return paginator.get_paginated_response(serializer.data)
        

class CreateBookmark(APIView):
    def post(self, request, slug):
        user = User.objects.get(email=request.user)
        try:
            post = Post.objects.get(slug=slug)
            bookmark = Bookmark.objects.create(user_that_bookmarked=user, bookmarked_post=post, resource_key=get_resource_key(Bookmark))
            assign_perm('posts.change_bookmark', user, bookmark)
            assign_perm('posts.delete_bookmark', user, bookmark)
            serializer = BookmarkSerializer(instance=bookmark)
            return Response({
                "detail": "Your bookmark was created successfully.",
                "bookmark": serializer.data,
            })
        except Post.DoesNotExist:
            return Response({
                "detail": "That post was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class DeleteBookmark(APIView):
    def post(self, request, resource_key):
        user = User.objects.get(email=request.user)
        try:
            bookmark = Bookmark.objects.get(resource_key=resource_key)
            if user.has_perm('posts.delete_bookmark', bookmark):
                bookmark.archived = True
                bookmark.save()
                return Response({
                    "detail": "Your bookmark was deleted.",
                })
            else:
                return Response({
                    "detail": "That cannot delete that bookmark.",
                }, status=status.HTTP_403_FORBIDDEN)
        except Bookmark.DoesNotExist:
            return Response({
                "detail": "That bookmark was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

