import secrets
import string
import datetime
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone, timesince
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from guardian.shortcuts import assign_perm
from oauth2_provider.models import Application, AccessToken

User = get_user_model()

def get_random_token(length):
    token = str()
    alphabet = string.ascii_letters + string.digits 
    while True: 
        random_token = ''.join(secrets.choice(alphabet) for i in range(length)) 
        if (any(c.islower() for c in random_token) and any(c.isupper()  
            for c in random_token) and sum(c.isdigit() for c in random_token) >= 3): 
            token = random_token
            break
    return token

def get_access_token():
    access_token = str()
    while True:
        access_token = get_random_token(20)
        try:
            AccessToken.objects.get(token=access_token)
            continue
        except AccessToken.DoesNotExist:
            break
    return access_token

class MakeWriter(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, username):
        if request.user.is_superuser:
            try:
                user = User.objects.get(username=username)
                group, created = Group.objects.get_or_create(name='Writers')
                assign_perm('posts.add_post', group)
                user.groups.add(group)
                return Response({
                    'details': 'That user was made a writer.',
                })
            except User.DoesNotExist:
                return Response({
                    'details': 'That user was not found.',
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({
                'details': 'That action could not be performed.',
            }, status=status.HTTP_403_FORBIDDEN)


class TestMakeWriter(APIView):
    permission_classes = [IsAuthenticated]
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
            return Response({
                'details': 'That user was not found.',
            }, status=status.HTTP_404_NOT_FOUND)

class TestAccessToken(APIView):
    def get(self, request):
        try:
            user = User.objects.get(username='testuser')
            try:
                access_token = AccessToken.objects.get(user__pk=user.id)
                return Response({
                    "access_token": access_token.token,
                    "expires_in": timesince.timesince(timezone.now(), access_token.expires).encode('utf8').replace(b'\xc2\xa0', b' ').decode('utf8'),
                    "token_type": "Bearer",
                    "scope": access_token.scope,
                })
            except AccessToken.DoesNotExist:
                application, created = Application.objects.get_or_create(
                    name = "Test Application",
                    redirect_uris = "http://localhost:8000",
                    user = user,
                    client_type = Application.CLIENT_CONFIDENTIAL,
                    authorization_grant_type = Application.GRANT_AUTHORIZATION_CODE,
                )
                if created:
                    access_token = AccessToken.objects.create(
                        user = user,
                        token = get_access_token(),
                        application = application,
                        scope = 'read write',
                        expires = timezone.now() + datetime.timedelta(days=365),
                    )
                else:
                    access_token = AccessToken.objects.get(user__pk=user.id)
                return Response({
                    "access_token": access_token.token,
                    "expires_in": timesince.timesince(timezone.now(), access_token.expires).encode('utf8').replace(b'\xc2\xa0', b' ').decode('utf8'),
                    "token_type": "Bearer",
                    "scope": access_token.scope,
                })
        except User.DoesNotExist:
            user = User.objects.create_user(
                first_name='test',
                last_name='user',
                username='testuser',
                email='test@example.com',
                password='testpassword',
            )
            application, created = Application.objects.get_or_create(
                name = "Test Application",
                redirect_uris = "http://localhost:8000",
                user = user,
                client_type = Application.CLIENT_CONFIDENTIAL,
                authorization_grant_type = Application.GRANT_AUTHORIZATION_CODE,
            )
            if created:
                access_token = AccessToken.objects.create(
                    user = user,
                    token = get_access_token(),
                    application = application,
                    scope = 'read write',
                    expires = timezone.now() + datetime.timedelta(days=365),
                )
            else:
                access_token = AccessToken.objects.get(user__pk=user.id)
            return Response({
                "access_token": access_token.token,
                "expires_in": timesince.timesince(timezone.now(), access_token.expires).encode('utf8').replace(b'\xc2\xa0', b' ').decode('utf8'),
                "token_type": "Bearer",
                "scope": access_token.scope,
            })

class ResetPassword(APIView):
    def post(self, request):
        pass

class ConfirmResetPassword(APIView):
    def get(self, request):
        pass
        
class UpdateProfile(APIView):
    def post(self, request):
        pass

class UpdateAvatar(APIView):
    def post(self, request):
        pass