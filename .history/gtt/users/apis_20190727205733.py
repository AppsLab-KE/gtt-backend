from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from guardian.shortcuts import assign_perm
from .permissions import IsSuperuser

User = get_user_model()

class MakeWriter(APIView):
    permission_classes = [IsAuthenticated|IsSuperuser]
    def post(self, request, username):
        try:
            user = User.objects.get(username=username)
            group, created = Group.objects.get_or_create(name='Writer')
            assign_perm('add_post', group)
            user.groups.add(group)
            return 
        except User.DoesNotExist:



