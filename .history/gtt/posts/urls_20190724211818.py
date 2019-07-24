from django.conf import settings
from django.urls import path
from .apis import (
    ViewPost, ViewRatedPosts, ViewRecommendedPosts, CreatePost, UpdatePost, DeletePost, RatePost,
    ViewComments, CreateComment, UpdateComment, DeleteComment,
    ViewReplies, CreateReply, UpdateReply, DeleteReply,
    ViewBookmarks, CreateBookmark, DeleteBookmark,
)

urlpatterns = [
    path()
]