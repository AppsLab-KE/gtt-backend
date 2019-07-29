from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from django.contrib.auth import get_user_model
from django.forms.models import model_to_dict
from notifications.models import Notification
from notifications.utils import slug2id

User = get_user_model()

class AllNotifications(APIView):
    def get(self, request):
        user = User.objects.get(email=request.user)
        print(request.data)
        if 'offset' in request.data and 'limit' in request.data:
            offset = int(request.data.get('offset'))
            limit = int(request.data.get('limit'))
            notifications = Notification.objects.filter(recipient__pk=user.id)[offset:offset+limit]
        else:
            notifications =Notification.objects.filter(recipient__pk=user.id)
        response_list = list()
        recipient = model_to_dict(user, fields=['first_name', 'last_name', 'username', 'email'])
        recipient.update({'user_avatar': settings.DOMAIN_URL + user.profile.avatar.url})
        for notification in notifications:
            actor = model_to_dict(notification.actor, fields=['first_name', 'last_name', 'username', 'email'])
            actor.update({'user_avatar': settings.DOMAIN_URL + notification.actor.profile.avatar.url})
            notification = {
                "slug": notification.slug,
                "sender": actor,
                "recipient": recipient,
                "code": notification.verb,
                "description": notification.description,
                "timestamp": notification.timestamp,
                "unread": notification.unread,
            }
            response_list.append(notification)
        return Response(response_list)

class UnreadNotifications(APIView):
    def get(self, request):
        user = User.objects.get(email=request.user)
        if 'offset' in request.data and 'limit' in request.data:
            offset = int(request.data.get('offset'))
            limit = int(request.data.get('limit'))
            notifications = Notification.objects.filter(recipient__pk=user.id).unread()[offset:offset+limit]
        else:
            notifications = Notification.objects.filter(recipient__pk=user.id).unread()
        response_list = list()
        recipient = model_to_dict(user, fields=['first_name', 'last_name', 'username', 'email'])
        recipient.update({'user_avatar': settings.DOMAIN_URL + user.profile.avatar.url})
        for notification in notifications:
            actor = model_to_dict(notification.actor, fields=['first_name', 'last_name', 'username', 'email'])
            actor.update({'user_avatar': settings.DOMAIN_URL + notification.actor.profile.avatar.url})
            notification = {
                "slug": notification.slug,
                "sender": actor,
                "recipient": recipient,
                "code": notification.verb,
                "description": notification.description,
                "timestamp": notification.timestamp,
                "unread": notification.unread,
            }
            response_list.append(notification)
        return Response(response_list)

class MarkAllAsRead(APIView):
    def post(self, request):
        user = User.objects.get(email=request.user)
        notifications = Notification.objects.filter(recipient__pk=user.id)
        marked = bool(int(notifications.mark_all_as_read()))
        if marked:
            return Response({
                "detail": "All notifications marked as read.",
            })
        else:
            return Response({
                "detail": "Could not mark all as read.",
            }, status=status.HTTP_400_BAD_REQUEST)

class MarkAsRead(APIView):
    def post(self, request, notification_slug):
        user = User.objects.get(email=request.user)
        notification_id = slug2id(notification_slug)
        notification = Notification.objects.filter(recipient__pk=user.id, pk=notification_id)
        marked = bool(int(notifications.mark_all_as_read()))
        if marked:
            return Response({
                "detail": "Notification marked as read.",
            })
        else:
            return Response({
                "detail": "Could not mark as read.",
            }, status=status.HTTP_400_BAD_REQUEST)

class MarkAllAsUnread(APIView):
    def post(self, request):
        user = User.objects.get(email=request.user)
        notifications = Notification.objects.filter(recipient__pk=user.id)
        marked = bool(int(notifications.mark_all_as_unread()))
        if marked:
            return Response({
                "detail": "All notifications marked as unread.",
            })
        else:
            return Response({
                "detail": "Could not mark all as unread.",
            }, status=status.HTTP_400_BAD_REQUEST)

class MarkAsUnRead(APIView):
    def post(self, request, notification_slug):
        user = User.objects.get(email=request.user)
        notification_id = slug2id(notification_slug)
        notification = Notification.objects.filter(recipient__pk=user.id, pk=notification_id)
        marked = bool(int(notifications.mark_all_as_unread()))
        if marked:
            return Response({
                "detail": "Notification marked as unread.",
            })
        else:
            return Response({
                "detail": "Could not mark as unread.",
            }, status=status.HTTP_400_BAD_REQUEST)

class DeleteAll(APIView):
    def post(self, request):
        user = User.objects.get(email=request.user)
        notifications = Notification.objects.filter(recipient__pk=user.id)
        deleted_rows, deleted_row_dict = notifications.delete()
        if bool(int(deleted_rows)):
            return Response({
                "detail": "All notifications deleted.",
            })
        else:
            return Response({
                "detail": "Could not delete all.",
            }, status=status.HTTP_400_BAD_REQUEST)

class Delete(APIView):
    def post(self, request, notification_slug):
        user = User.objects.get(email=request.user)
        notification_id = slug2id(notification_slug)
        notification = Notification.objects.filter(recipient__pk=user.id, pk=notification_id)
        deleted_row, deleted_row_dict = notification.delete()
        if bool(int(deleted_row)):
            return Response({
                "detail": "Notification was deleted.",
            })
        else:
            return Response({
                "detail": "Could not delete that notofication.",
            }, status=status.HTTP_400_BAD_REQUEST)

class UnreadCount(APIView):
    def get(self, request):
        user = User.objects.get(email=request.user)
        unread_count = Notification.objects.filter(recipient__pk=user.id).unread().count()
        return Response({
            "detail": unread_count,
        })

class AllCount(APIView):
    def get(self, request):
        user = User.objects.get(email=request.user)
        all_count = Notification.objects.filter(recipient__pk=user.id).count()
        return Response({
            "detail": all_count,
        })



