from django.conf import settings
from django.urls import path
from .apis import (
    ViewPost, ViewRatedPosts, ViewTagPosts, ViewPopularPosts, ViewRecommendedPosts, SearchPosts, CreatePost, UpdatePost, 
    DeletePost, RatePost, ViewComments, CreateComment, UpdateComment, DeleteComment,
    ViewReplies, CreateReply, UpdateReply, DeleteReply,
    ViewBookmarks, CreateBookmark, DeleteBookmark,
)

urlpatterns = [
    path(settings.API + "posts/@<username>/<slug:slug>", ViewPost.as_view(), name='view_post'),
    path(settings.API + "posts/rated", ViewRatedPosts.as_view(), name='view_rated_posts'),
    path(settings.API + "posts/tags/<slug:tag_name>", ViewTagPosts.as_view(), name='view_tag_posts'),
    path(settings.API + "posts/popular", ViewPopularPosts.as_view(), name='view_popular_posts'),
    path(settings.API + "posts/recommended", ViewRecommendedPosts.as_view(), name='view_recommended_posts'),
    path(settings.API + "posts/", SearchPosts.as_view(), name='search_posts'),
    path(settings.API + "posts/create", CreatePost.as_view(), name='create_post'),
    path(settings.API + "posts/<slug:slug>/update", UpdatePost.as_view(), name='update_post'),
    path(settings.API + "posts/<slug:slug>/delete", DeletePost.as_view(), name='delete_post'),
    path(settings.API + "posts/<slug:slug>/rate", RatePost.as_view(), name='rate_post'),
    path(settings.API + "posts/<slug:slug>/comments", ViewComments.as_view(), name='view_comments'),
    path(settings.API + "posts/<slug:slug>/comments/create", CreateComment.as_view(), name='create_comment'),
    path(settings.API + "comments/<resource_key>/update", UpdateComment.as_view(), name='update_comment'),
    path(settings.API + "comments/<resource_key>/delete", DeleteComment.as_view(), name='delete_comment'),
    path(settings.API + "comments/<resource_key>/replies", ViewReplies.as_view(), name='view_replies'),
    path(settings.API + "comments/<resource_key>/replies/create", CreateReply.as_view(), name='create_reply'),
    path(settings.API + "replies/<resource_key>/update", UpdateReply.as_view(), name='update_reply'),
    path(settings.API + "replies/<resource_key>/delete", DeleteReply.as_view(), name='delete_reply'),
    path(settings.API + "bookmarks", ViewBookmarks.as_view(), name='view_bookmarks'),
    path(settings.API + "posts/<slug:slug>/bookmark/create", CreateBookmark.as_view(), name='create_bookmark'),
    path(settings.API + "bookmarks/<resource_key>/delete", DeleteBookmark.as_view(), name='delete_bookmark'),
]