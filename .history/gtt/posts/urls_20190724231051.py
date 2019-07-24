from django.conf import settings
from django.urls import path
from .apis import (
    ViewPost, ViewRatedPosts, ViewTagPosts, ViewRecommendedPosts, CreatePost, UpdatePost, DeletePost, RatePost,
    ViewComments, CreateComment, UpdateComment, DeleteComment,
    ViewReplies, CreateReply, UpdateReply, DeleteReply,
    ViewBookmarks, CreateBookmark, DeleteBookmark,
)

urlpatterns = [
    path(settings.API + "posts/<slug>", ViewPost.as_view(), name='view_post'),
    path(settings.API + "posts/rated", ViewRatedPosts.as_view(), name='view_rated_posts'),
    path(settings.API + "posts/tags/<tag_name>", ViewRatedPosts.as_view(), name='view_tag_posts'),
    path(settings.API + "posts/recommendations", ViewRecommendedPosts.as_view(), name='view_recommended_posts'),
    path(settings.API + "posts/create", CreatePost.as_view(), name='create_post'),
    path(settings.API + "posts/<slug>/update", UpdatePost.as_view(), name='update_post'),
    path(settings.API + "posts/<slug>/delete", DeletePost.as_view(), name='delete_post'),
    path(settings.API + "posts/<slug>/rate", RatePost.as_view(), name='rate_post'),
    path(settings.API + "posts/<slug>/comments", ViewComments.as_view(), name='view_comments'),
    path(settings.API + "posts/<slug>/comments/create", CreateComment.as_view(), name='create_comment'),
    path(settings.API + "comments/<resource_key>/update", UpdateComment.as_view(), name='update_comment'),
    path(settings.API + "comments/<resource_key>/delete", DeleteComment.as_view(), name='delete_comment'),
    path(settings.API + "comments/<resource_key>/replies", ViewReplies.as_view(), name='view_replies'),
    path(settings.API + "comments/<resource_key>/replies/create", CreateReply.as_view(), name='create_reply'),
    path(settings.API + "replies/<resource_key>/update", UpdateReply.as_view(), name='update_reply'),
    path(settings.API + "replies/<resource_key>/delete", DeleteReply.as_view(), name='delete_reply'),
    path(settings.API + "bookmarks", ViewBookmarks.as_view(), name='view_bookmarks'),
    path(settings.API + "bookmarks/create", CreateBookmark.as_view(), name='create_bookmark'),
    path(settings.API + "bookmarks/<resource_key>/delete", DeleteBookmark.as_view(), name='delete_bookmark'),
]