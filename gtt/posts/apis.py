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
from .forms import (
    PostForm, RatingForm, CommentForm, ReplyForm,
)
from .serializers import (
    CategorySerializer, TagSerializer, CommentSerializer, ReplySerializer,
    PostPreviewSerializer, PostSerializer, BookmarkSerializer,
)
from .models import (
    Category, Tag, Post, Comment, Reply, Rating, Bookmark,
)
from .recommender import PostRecommender
from .helpers import *

User = get_user_model()
recommender = PostRecommender()

class ViewTags(APIView):
    permission_classes = []
    def get(self, request):
        tags = Tag.objects.all().order_by('-date_added')
        paginator = LimitOffsetPaginationWithDefault()
        context = paginator.paginate_queryset(tags, request)
        serializer = TagSerializer(context, many=True)
        return paginator.get_paginated_response(serializer.data)

class ViewCategories(APIView):
    permission_classes = []
    def get(self, request):
        categories = Category.objects.all().order_by('-date_added')
        paginator = LimitOffsetPaginationWithDefault()
        context = paginator.paginate_queryset(categories, request)
        serializer = CategorySerializer(context, many=True)
        return paginator.get_paginated_response(serializer.data)

class ViewPost(APIView):
    permission_classes = []
    def get(self, request, username, slug):
        try:
            post = Post.objects.get(slug=slug, post_author__username=username)
            if request.user.is_authenticated:
                user = User.objects.get(username=request.user.username)
                try:
                    Rating.objects.get(rated_post__pk=post.id, user_that_rated__pk=user.id)
                except Rating.DoesNotExist:
                    Rating.objects.create(rated_post=post, user_that_rated=user)
            serializer = PostSerializer(instance=post)
            return Response(serializer.data)
        except Post.DoesNotExist:
            return Response({
                "detail": "That post was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class ViewUserPosts(APIView):
    permission_classes = []
    def get(self, request, username):
        try:
            user = User.objects.get(username=username)
            paginator = LimitOffsetPaginationWithDefault()
            context = paginator.paginate_queryset(user.posts.order_by('-date_published'), request)
            serializer = PostPreviewSerializer(context, many=True)
            return paginator.get_paginated_response(serializer.data)
        except User.DoesNotExist:
            return Response({
                "detail": "That user was not found.",
            }, status=status.HTTP_404_NOT_FOUND)


class ViewRatedPosts(APIView):
    def get(self, request):
        user = User.objects.get(username=request.user.username)
        user_rated_posts = Post.objects.filter(ratings__user_that_rated__pk=user.id, ratings__rating=True).order_by('-date_published')
        paginator = LimitOffsetPaginationWithDefault()
        context = paginator.paginate_queryset(user_rated_posts, request)
        serializer = PostPreviewSerializer(context, many=True)
        return paginator.get_paginated_response(serializer.data)

class ViewTagPosts(APIView):
    permission_classes = []
    def get(self, request, tag_slug):
        try:
            tag = Tag.objects.get(slug=tag_slug)
            tag_posts = tag.posts.all().order_by('-date_published')
            paginator = LimitOffsetPaginationWithDefault()
            context = paginator.paginate_queryset(tag_posts, request)
            serializer = PostPreviewSerializer(context, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Tag.DoesNotExist:
            return Response({
                "detail": "That tag was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class ViewCategoryPosts(APIView):
    permission_classes = []
    def get(self, request, category_slug):
        try:
            category = Category.objects.get(slug=category_slug)
            category_posts = category.posts.all().order_by('-date_published')
            paginator = LimitOffsetPaginationWithDefault()
            context = paginator.paginate_queryset(category_posts, request)
            serializer = PostPreviewSerializer(context, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Category.DoesNotExist:
            return Response({
                "detail": "That category was not found.",
            }, status=status.HTTP_404_NOT_FOUND)

class ViewPopularPosts(APIView):
    permission_classes = []
    def get(self, request):
        top_n = request.GET.get('top_n', 10)
        if recommender.checksetUp():
            recommender.setUp()
            popular_posts = recommender.get_popular_posts(topn=int(top_n))
            if popular_posts.exists():
                paginator = LimitOffsetPaginationWithDefault()
                context = paginator.paginate_queryset(popular_posts.order_by('-date_published'), request)
                serializer = PostPreviewSerializer(context, many=True)
                return paginator.get_paginated_response(serializer.data)
            else:
                return Response({
                    "detail": "Sorry. No popular posts available for you yet.",
                }, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({
                "detail": "Sorry. No popular posts available for you yet.",
            }, status=status.HTTP_204_NO_CONTENT)

class ViewRecommendedPosts(APIView):
    def get(self, request):
        top_n = request.GET.get('top_n', 10)
        user = User.objects.get(username=request.user.username)
        if recommender.checksetUp():
            recommender.setUp()
            try:
                recommended_posts = recommender.get_recommended_posts(user_id=user.id, topn=int(top_n))
                if recommended_posts.exists():
                    paginator = LimitOffsetPaginationWithDefault()
                    context = paginator.paginate_queryset(recommended_posts.order_by('-date_published'), request)
                    serializer = PostPreviewSerializer(context, many=True)
                    return paginator.get_paginated_response(serializer.data)
                else:
                    return Response({
                        "detail": "Sorry. No recommendations available for you yet.",
                    }, status=status.HTTP_204_NO_CONTENT)
            except KeyError:
                return Response({
                    "detail": "Sorry. No recommendations available for you yet.",
                }, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({
                "detail": "Sorry. No recommendations available for you yet.",
            }, status=status.HTTP_204_NO_CONTENT)

class SearchPosts(generics.ListCreateAPIView):
    permission_classes = []
    search_fields = ['category__category_name', 'tags__tag_name', 'post_author__first_name', 'post_author__last_name', 'post_author__username', 'post_heading', 'post_body']
    filter_backends = (filters.SearchFilter,)
    queryset = Post.objects.all().order_by('-date_published')
    serializer_class = PostPreviewSerializer

class CreatePost(APIView):
    def post(self, request):
        post_heading = request.data.get('post_heading')
        post_body = request.data.get('post_body')
        read_duration = request.data.get("read_duration")
        category = request.data.get('category', False)
        tags = request.data.getlist('tag')
        user = User.objects.get(username=request.user.username)
        if category:
            if 'post_heading_image' in request.FILES:
                if user.has_perm('posts.add_post'):
                    post_form = PostForm({
                        'post_heading': post_heading, 
                        'post_body': post_body, 
                        'read_duration': str(read_duration) + " min",
                        }, request.FILES)
                    if post_form.is_valid():
                        try:
                            category_obj = Category.objects.get(category_name=category)
                            post = post_form.save()
                            post.post_author = user
                            post.category = category_obj
                            post.save()
                            tag_instance_list = []
                            for tag in tags:
                                try:
                                    tag = Tag.objects.get(tag_name__iexact=tag)
                                    tag_instance_list.append(tag)
                                except Tag.DoesNotExist:
                                    tag = Tag.objects.create(tag_name=tag.capitalize())
                                    tag_instance_list.append(tag)

                            post.tags.add(*tag_instance_list)
                            assign_perm('posts.change_post', user, post)
                            assign_perm('posts.delete_post', user, post)
                            serializer = PostSerializer(instance=post)
                            return Response({
                                "detail": "That post was created.",
                                "post": serializer.data,
                            })
                        except Category.DoesNotExist:
                            return Response({
                                "detail": "That category was not found.",
                            }, status=status.HTTP_404_NOT_FOUND)
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
        else:
            return Response({
                        "detail": {
                            "category": [
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
        category = request.data.get('category', False)
        tags = request.data.getlist('tag')
        user = User.objects.get(username=request.user.username)
        if category:
            try:
                post = Post.objects.get(slug=slug)
                if user.has_perm('posts.change_post', post):
                    post_form = PostForm({
                        'post_heading': post_heading, 
                        'post_body': post_body, 
                        'read_duration': str(read_duration) + " min",
                    }, request.FILES, instance=post)
                    tag_instance_list = []
                    if post_form.is_valid():
                        try:
                            category_obj = Category.objects.get(category_name=category)
                            updated_post = post_form.save()
                            for tag in tags:
                                try:
                                    tag = Tag.objects.get(tag_name__iexact=tag)
                                    tag_instance_list.append(tag)
                                except Tag.DoesNotExist:
                                    tag = Tag.objects.create(tag_name=tag.capitalize())
                                    tag_instance_list.append(tag)

                            updated_post.category = None
                            updated_post.save()
                            updated_post.tags.clear()
                            updated_post.category = category_obj
                            updated_post.save()
                            updated_post.tags.add(*tag_instance_list)
                            serializer = PostSerializer(instance=updated_post)
                            return Response({
                                "detail": "That post was updated.",
                                "post": serializer.data,
                            })
                        except Category.DoesNotExist:
                            return Response({
                                "detail": "That category was not found.",
                            }, status=status.HTTP_404_NOT_FOUND)
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
        else:
            return Response({
                        "detail": {
                            "category": [
                                {
                                    "message": "This field is required.",
                                    "code": "required",
                                }
                            ]
                        },
                    }, status=status.HTTP_400_BAD_REQUEST)

class DeletePost(APIView):
    def post(self, request, slug):
        user = User.objects.get(username=request.user.username)
        try:
            post = Post.objects.get(slug=slug)
            if user.has_perm('posts.delete_post', post):
                post.delete()
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
        user = User.objects.get(username=request.user.username)
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
        comments = Comment.objects.filter(commented_post__slug=slug).order_by('-date_commented')
        paginator = LimitOffsetPaginationWithDefault()
        context = paginator.paginate_queryset(comments, request)
        serializer = CommentSerializer(context, many=True)
        return paginator.get_paginated_response(serializer.data)

class CreateComment(APIView):
    def post(self, request, slug):
        comment = request.data.get('comment')
        user = User.objects.get(username=request.user.username)
        try:
            post = Post.objects.get(slug=slug)
            comment_form = CommentForm({
                'comment': comment,
            })
            if comment_form.is_valid():
                comment = comment_form.save()
                comment.commented_post = post
                comment.user_that_commented = user
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
        user = User.objects.get(username=request.user.username)
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
        user = User.objects.get(username=request.user.username)
        try:
            comment = Comment.objects.get(resource_key=resource_key)
            if user.has_perm('posts.delete_comment', comment):
                comment.delete()
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
        replies = Reply.objects.filter(replied_comment__resource_key=resource_key).order_by('-date_replied')
        paginator = LimitOffsetPaginationWithDefault()
        context = paginator.paginate_queryset(replies, request)
        serializer = ReplySerializer(context, many=True)
        return paginator.get_paginated_response(serializer.data)

class CreateReply(APIView):
    def post(self, request, resource_key):
        reply = request.data.get('reply')
        user = User.objects.get(username=request.user.username)
        try:
            comment = Comment.objects.get(resource_key=resource_key)
            reply_form = ReplyForm({
                'reply': reply,
            })
            if reply_form.is_valid():
                reply = reply_form.save()
                reply.replied_comment = comment
                reply.user_that_replied = user
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
        user = User.objects.get(username=request.user.username)
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
        user = User.objects.get(username=request.user.username)
        try:
            reply = Reply.objects.get(resource_key=resource_key)
            if user.has_perm('posts.delete_reply', reply):
                reply.delete()
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
        user = User.objects.get(username=request.user.username)
        bookmarks = Bookmark.objects.filter(user_that_bookmarked__pk=user.id).order_by('-date_bookmarked')
        paginator = LimitOffsetPaginationWithDefault()
        context = paginator.paginate_queryset(bookmarks, request)
        serializer = BookmarkSerializer(context, many=True)
        return paginator.get_paginated_response(serializer.data)
        

class CreateBookmark(APIView):
    def post(self, request, slug):
        user = User.objects.get(username=request.user.username)
        try:
            post = Post.objects.get(slug=slug)
            bookmark = Bookmark.objects.create(user_that_bookmarked=user, bookmarked_post=post)
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
        user = User.objects.get(username=request.user.username)
        try:
            bookmark = Bookmark.objects.get(resource_key=resource_key)
            if user.has_perm('posts.delete_bookmark', bookmark):
                bookmark.delete()
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

