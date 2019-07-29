from rest_framework import status
from rest_framework.views import APIView
from django.db.models import Q
from notifications.models import Notification
from notifications.utils import slug2id

class AllNotifications(APIView):
    def get(self, request):
        user = User.objects.get(email=request.user)
        if 'offset' in request.data and 'limit' in request.data:
            offset = int(request.data.get('offset'))
            limit = int(request.data.get('limit'))
            notifications = Notification.objects.filter(Q(actor__pk=user.id)|Q(recipient__pk=user.id))[offset:offset+limit]
        else:
            notifications =Notification.objects.filter(Q(actor__pk=user.id)|Q(recipient__pk=user.id))

class UnreadNotifications(APIView):
    def get(self, request):
        user = User.objects.get(email=request.user)
        if 'offset' in request.data and 'limit' in request.data:
            offset = int(request.data.get('offset'))
            limit = int(request.data.get('limit'))
            notifications = Notification.objects.filter(Q(actor__pk=user.id)|Q(recipient__pk=user.id)).unread()[offset:offset+limit]
        else:
            notifications = Notification.objects.filter(Q(actor__pk=user.id)|Q(recipient__pk=user.id)).unread()

class MarkAllAsRead(APIView):
    def post(self, request):
        user = User.objects.get(email=request.user)
        notifications = Notification.objects.filter(Q(actor__pk=user.id)|Q(recipient__pk=user.id)).mark_all_as_read()

class MarkAllAsUnread(APIView):
    def post(self, request):
        user = User.objects.get(email=request.user)
        notifications = Notification.objects.filter(Q(actor__pk=user.id)|Q(recipient__pk=user.id)).mark_all_as_unread()

class MarkAllAsDeleted(APIView):
    def post(self, request):
        user = User.objects.get(email=request.user)
        notifications = Notification.objects..filter(Q(actor__pk=user.id)|Q(recipient__pk=user.id))
        notifications.delete()

class Delete(APIView):
    def post(self, request, slug):
        user = User.objects.get(email=request.user)
        notification_id = slug2id(slug)
        notification = Notification.objects.filter(pk=notification_id, Q(actor__pk=user.id)|Q(recipient__pk=user.id))
        notification.delete()

class UnreadCount(APIView):
    def get(self, request):
        user = User.objects.get(email=request.user)
        unread_count = Notification.objects.filter(Q(actor__pk=user.id)|Q(recipient__pk=user.id)).unread().count()

class AllCount(APIView):
    def get(self, request):
        user = User.objects.get(email=request.user)
        all_count = Notification.objects.filter()Q(actor__pk=user.id)|Q(recipient__pk=user.id).count()



