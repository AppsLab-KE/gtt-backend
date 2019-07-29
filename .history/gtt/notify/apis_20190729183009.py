from rest_framework import status
from rest_framework.views import APIView
from notifications.models import Notification
from notifications.utils import slug2id

class AllNotifications(APIView):
    def get(self, request):
        if 'offset' in request.data and 'limit' in request.data:
            offset = int(request.data.get('offset'))
            limit = int(request.data.get('limit'))
            replies = Reply.objects.filter(replied_comment__resource_key=resource_key)[offset:offset+limit]
        else:
            replies = Reply.objects.filter(replied_comment__resource_key=resource_key)
class UnreadNotifications(APIView):
    def get(self, request):

class MarkAllAsRead(APIView):
    def post(self, request):

class MarkAsUnread(APIView):
    def post(self, request):

class Delete(APIView):
    def post(self, request):

class UnreadCount(APIView):
    def get(self, request):

class AllCount(APIView):
    def get(self, request):



