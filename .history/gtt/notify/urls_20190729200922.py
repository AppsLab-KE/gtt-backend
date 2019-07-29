from django.conf import settings
from django.urls import path
from .apis import (
    AllNotifications, UnreadNotifications, MarkAllAsRead, MarkAsRead, MarkAllAsUnread, MarkAsUnRead, DeleteAll, Delete, UnreadCount, AllCount
)

urlpatterns = [
    path(settings.API + 'notifications', AllNotifications.as_view(), name='all_notifications'),
    path(settings.API + 'notifications/unread', UnreadNotifications.as_view(), name='unread_notifications'),
    path(settings.API + 'notifications/mark_all_as_read', MarkAllAsRead.as_view(), name='mark_all_as_read'),
    path(settings.API + 'notifications/<slug:notification_slug>/mark_as_read', MarkAsRead.as_view(), name='mark_as_read'),
    path(settings.API + 'notifications/mark_all_as_unread', MarkAllAsUnread.as_view(), name='mark_all_as_unread'),
    path(settings.API + 'notifications/<slug:notification_slug>/mark_as_unread', MarkAsUnread.as_view(), name='mark_as_unread'),
    path(settings.API + 'notifications/delete_all', DeleteAll.as_view(), name='delete_all'),
    path(settings.API + 'notifications/<slug:notification_slug>/delete', Delete.as_view(), name='delete'),
    path(settings.API + 'notifications/unread_count', UnreadCount.as_view(), name='update_count'),
    path(settings.API + 'notifications/all_count', AllCount.as_view(), name='all_count'),
]