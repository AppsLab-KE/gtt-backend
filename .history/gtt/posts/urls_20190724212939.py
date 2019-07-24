from django.conf import settings
from django.urls import path
from .apis import (
    ViewPost, ViewRatedPosts, ViewRecommendedPosts, CreatePost, UpdatePost, DeletePost, RatePost,
    ViewComments, CreateComment, UpdateComment, DeleteComment,
    ViewReplies, CreateReply, UpdateReply, DeleteReply,
    ViewBookmarks, CreateBookmark, DeleteBookmark,
)

urlpatterns = [
    path(settings.API + , ViewPost.as_view(), name='view_post'),
    path(settings.API + , ViewRatedPosts.as_view(), name='view_rated_post'),
    path(settings.API + , ViewRecommendedPosts.as_view(), name='view_recommended_post'),
    path(settings.API + , CreatePost.as_view(), name='create_post'),
    path(settings.API + , UpdatePost.as_view(), name='update_post'),
    path(settings.API + , DeletePost.as_view(), name='delete_post'),
    path(settings.API + , RatePost.as_view(), name='rate_post'),
    path(settings.API + , ViewComments.as_view(), name='view_comments'),
    path(settings.API + , CreateComment.as_view(), name='create_comment'),
    path(settings.API + , UpdateComment.as_view(), name='update_comment'),
    path(settings.API + , DeleteComment.as_view(), name='delete_comment'),
    path(settings.API + , ViewReplies.as_view(), name='view_replies'),
    path(settings.API + , CreateReply.as_view(), name='create_reply'),
    path(settings.API + , UpdateReply.as_view(), name='update_reply'),
    path(settings.API + , DeleteReply.as_view(), name='delete_reply'),
    path(settings.API + , ViewBookmarks.as_view(), name='view_bookmarks'),
    path(settings.API + , CreateBookmark.as_view(), name='create_bookmark'),
    path(settings.API + , DeleteBookmark.as_view(), name='delete_bookmark'),
]