from django.conf import settings
from django.urls import path
from .apis import (
    AllNotifications, UnreadNotifications, MarkAllAsRead, MarkAllAsUnread, DeleteAll, Delete, UnreadCount, AllCount
)

urlpatterns = [
    path(settings.API + 'notifications', RequestWritership.as_view(), name='request_writership'),
    path(settings.API + 'notifications/unread', MakeWriter.as_view(), name='make_writer'),
    path(settings.API + 'notifications/mark_all_as_read', TestMakeWriter.as_view(), name='test_make_writer'),
    path(settings.API + 'notifications/mark_all_as_unread', TestAccessToken.as_view(), name='test_access_token'),
    path(settings.API + 'notifications/delete_all', UpdateAvatar.as_view(), name='update_avatar'),
    path(settings.API + 'notifications/<slug:notification_slug>', UpdateAvatar.as_view(), name='update_avatar'),
    path(settings.API + 'notifications/unread_count', UpdateAvatar.as_view(), name='update_avatar'),
    path(settings.API + 'notifications/all_count', UpdateAvatar.as_view(), name='update_avatar'),
]