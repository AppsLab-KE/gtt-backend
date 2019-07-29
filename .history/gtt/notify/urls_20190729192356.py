from django.conf import settings
from django.urls import path
from .apis import (
    AllNotifications, UnreadNotifications, MarkAllAsRead, MarkAllAsUnread, DeleteAll, Delete, UnreadCount, AllCount
)

urlpatterns = [
    path(settings.API + 'notifications/request_writership', RequestWritership.as_view(), name='request_writership'),
    path(settings.API + 'notifications/<username>/make_writer', MakeWriter.as_view(), name='make_writer'),
    path(settings.API + 'notifications/<username>/test_make_writer', TestMakeWriter.as_view(), name='test_make_writer'),
    path(settings.API + 'notifications/access_token/test', TestAccessToken.as_view(), name='test_access_token'),
    path(settings.API + 'notifications/profile/avatar/update', UpdateAvatar.as_view(), name='update_avatar'),
]