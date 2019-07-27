from rest_framework import status
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
            group, created = Group.objects.get_or_create(name='Writers')
            assign_perm('posts.add_post', group)
            user.groups.add(group)
            return Response({
                'details': 'That user was made a writer.',
            })
        except User.DoesNotExist:
            print(request.user)
            return Response({
                'details': 'That user was not found.',
            })


