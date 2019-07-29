from rest_framework import status
from rest_framework.views import APIView
from notifications.models import Notification
from notifications.utils import slug2id

class AllNotifications(APIView):
    def get(self, request):

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



