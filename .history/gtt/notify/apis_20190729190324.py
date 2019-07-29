from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from notifications.models import Notification
from notifications.utils import slug2id

User = get_user_model()

class AllNotifications(APIView):
    def get(self, request):
        user = User.objects.get(email=request.user)
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
            sender = model_to_dict(notification.sender, fields=['first_name', 'last_name', 'username', 'email'])
            sender.update({'user_avatar': settings.DOMAIN_URL + notification.sender.profile.avatar.url})
            notification = {
                "sender": sender,
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
        for notification in notifications:

class MarkAllAsRead(APIView):
    def post(self, request):
        user = User.objects.get(email=request.user)
        notifications = Notification.objects.filter(recipient__pk=user.id)
        notifications.mark_all_as_read()

class MarkAllAsUnread(APIView):
    def post(self, request):
        user = User.objects.get(email=request.user)
        notifications = Notification.objects.filter(recipient__pk=user.id)
        notifications.mark_all_as_unread()

class MarkAllAsDeleted(APIView):
    def post(self, request):
        user = User.objects.get(email=request.user)
        notifications = Notification.objects.filter(recipient__pk=user.id)
        notifications.delete()

class Delete(APIView):
    def post(self, request, slug):
        user = User.objects.get(email=request.user)
        notification_id = slug2id(slug)
        notification = Notification.objects.filter(recipient__pk=user.id, pk=notification_id)
        notification.delete()

class UnreadCount(APIView):
    def get(self, request):
        user = User.objects.get(email=request.user)
        unread_count = Notification.objects.filter(recipient__pk=user.id).unread().count()

class AllCount(APIView):
    def get(self, request):
        user = User.objects.get(email=request.user)
        all_count = Notification.objects.filter(recipient__pk=user.id).count()



