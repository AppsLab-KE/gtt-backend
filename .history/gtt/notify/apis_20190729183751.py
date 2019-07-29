from rest_framework import status
from rest_framework.views import APIView
from notifications.models import Notification
from notifications.utils import slug2id

class AllNotifications(APIView):
    def get(self, request):
        if 'offset' in request.data and 'limit' in request.data:
            offset = int(request.data.get('offset'))
            limit = int(request.data.get('limit'))
            notifications = Notification.objects.all()[offset:offset+limit]
        else:
            notifications =Notification.objects.all()

class UnreadNotifications(APIView):
    def get(self, request):
        if 'offset' in request.data and 'limit' in request.data:
            offset = int(request.data.get('offset'))
            limit = int(request.data.get('limit'))
            notifications = Notification.objects.all().unread()[offset:offset+limit]
        else:
            notifications = Notification.objects.all().unread()

class MarkAllAsRead(APIView):
    def post(self, request):
        notifications = Notification.objects.all().mark_all_as_read()

class MarkAllAsUnread(APIView):
    def post(self, request):
        notifications = Notification.objects.all().mark_all_as_unread()

class MarkAllAsDeleted(APIView):
    def post(self, request):
        notifications = Notification.objects..all().delete()

class Delete(APIView):
    def post(self, request):

class UnreadCount(APIView):
    def get(self, request):
        notifications = Notification.objects.all().unread().count()

class AllCount(APIView):
    def get(self, request):
        notifications = Notification.objects.all().count()



