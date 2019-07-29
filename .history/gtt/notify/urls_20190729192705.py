from django.conf import settings
from django.urls import path
from .apis import (
    AllNotifications, UnreadNotifications, MarkAllAsRead, MarkAllAsUnread, DeleteAll, Delete, UnreadCount, AllCount
)

urlpatterns = [
    path(settings.API + 'notifications', AllNotifications.as_view(), name='request_writership'),
    path(settings.API + 'notifications/unread', UnreadNotifications.as_view(), name='make_writer'),
    path(settings.API + 'notifications/mark_all_as_read', MarkAllAsRead.as_view(), name='test_make_writer'),
    path(settings.API + 'notifications/mark_all_as_unread', MarkAllAsUnread.as_view(), name='test_access_token'),
    path(settings.API + 'notifications/delete_all', DeleteAll.as_view(), name='update_avatar'),
    path(settings.API + 'notifications/<slug:notification_slug>/delete', Delete.as_view(), name='update_avatar'),
    path(settings.API + 'notifications/unread_count', UnreadCount.as_view(), name='update_avatar'),
    path(settings.API + 'notifications/all_count', AllCount.as_view(), name='update_avatar'),
]