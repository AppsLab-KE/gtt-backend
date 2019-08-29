import json
import secrets
import string
import datetime
import logging
from django.conf import settings
from rest_framework import status
from braces.views import CsrfExemptMixin
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils import timezone, timesince
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.forms.models import model_to_dict
from guardian.shortcuts import assign_perm
from oauth2_provider.models import Application, AccessToken
from oauth2_provider.settings import oauth2_settings
from oauth2_provider.views.mixins import OAuthLibMixin
from rest_framework_social_oauth2.oauth2_backends import KeepRequestCore
from rest_framework_social_oauth2.oauth2_endpoints import SocialTokenServer
from notifications.signals import notify
from posts.helpers import (
    get_random_token, get_bitbucket_access_token, get_github_access_token, get_gitlab_access_token,
    user_confirmation_token, send_email, prepare_message,
)
from .forms import AvatarForm, UserForm

User = get_user_model()

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

class RequestWritership(APIView):
    def post(self, request):
        user = User.objects.get(email=request.user)
        superusers = User.objects.filter(is_superuser=True)
        if superusers.exists():
            notify.send(sender=user, recipient=superusers, verb='make_writer', description="{} wants to become a writer.".format(user.username))
            return Response({
                    'details': 'Your request was sent.',
                })
        else:
            return Response({
                    'details': 'Not admins were found.',
                }, status=status.HTTP_404_NOT_FOUND)

class MakeWriter(APIView):
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

class BackendAccessToken(CsrfExemptMixin, OAuthLibMixin, APIView):
    server_class = SocialTokenServer
    validator_class = oauth2_settings.OAUTH2_VALIDATOR_CLASS
    oauthlib_backend_class = KeepRequestCore
    permission_classes = (permissions.AllowAny,)
    authentication_classes = []

    def post(self, request, backend_name):
        if 'code' in request.data:
            code = request.data.get('code')
            if backend_name in ['bitbucket', 'github', 'gitlab']:
                try:
                    if backend_name == 'bitbucket':
                        redirect_uri = request.data.get('redirectUri')
                        access_response = get_bitbucket_access_token(code, redirect_uri)
                        mutable_data = access_response.copy()
                        request._request.POST = access_response.copy()
                        for key, value in mutable_data.items():
                            request._request.POST[key] = value
                        url, headers, body, resp_status = self.create_token_response(request._request)
                        response = Response(data=json.loads(body), status=resp_status)
                        for k, v in headers.items():
                            response[k] = v
                        return response
                    elif backend_name == 'github':
                        access_response = get_github_access_token(code)
                        mutable_data = access_response.copy()
                        request._request.POST = access_response.copy()
                        for key, value in mutable_data.items():
                            request._request.POST[key] = value
                        url, headers, body, resp_status = self.create_token_response(request._request)
                        response = Response(data=json.loads(body), status=resp_status)
                        for k, v in headers.items():
                            response[k] = v
                        return response
                    elif backend_name == 'gitlab':
                        access_response = get_gitlab_access_token(code)
                        mutable_data = access_response.copy()
                        request._request.POST = access_response.copy()
                        for key, value in mutable_data.items():
                            request._request.POST[key] = value
                        url, headers, body, resp_status = self.create_token_response(request._request)
                        response = Response(data=json.loads(body), status=resp_status)
                        for k, v in headers.items():
                            response[k] = v
                        return response
                except KeyError:
                    return Response({
                        "details": "The code you provided was invalid.",
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    "detail": "Social auth for " + backend_name + " does not exist.",
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({
                    "details": {
                        "code": [
                            {
                                "message": "This field is required.",
                                "code": "required",
                            }
                        ]
                    },
                }, status=status.HTTP_400_BAD_REQUEST)

class TestAccessToken(APIView):
    permission_classes = []
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

class RequestResetPassword(APIView):
    permission_classes = []
    def post(self, request):
        email = request.data.get('email', False)
        if email:
            try:
                user = User.objects.get(email=email)
                confirmation_token = user_confirmation_token()
                user.confirmation_token = confirmation_token
                subject = "Password reset request"
                recepient = [email]
                message = prepare_message(
                        template="reset_password.html",
                        username=user.username,
                        confirmation_token=confirmation_token,
                        url=settings.DOMAIN_URL)
                success = send_email(subject, recepient, message)
                if success:
                    user.save()
                    return Response({
                        "details": "A reset link was sent to the email.",
                    })
                else:
                    return Response({
                        "details": {
                            "email": [
                                {
                                    "message": "This field was incorrect.",
                                    "code": "incorrect",
                                }
                            ]
                        },
                    }, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({
                    'details': 'That user was not found.',
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({
                "details": {
                    "email": [
                        {
                            "message": "This field is required.",
                            "code": "required",
                        }
                    ]
                },
            }, status=status.HTTP_400_BAD_REQUEST)

class CheckResetParams(APIView):
    permission_classes = []
    def post(self, request):
        confirmation_token = request.data.get('confirmation_token', False)
        username = request.data.get('username', False)
        if confirmation_token and username:
            try:
                User.objects.get(confirmation_token=confirmation_token, username=username)
                return Response({
                    'detail': 'The reset parameters are valid.'
                })
            except User.DoesNotExist:
                return Response({
                    'detail': 'That user was not found.'
                }, status=status.HTTP_404_NOT_FOUND)
        elif username and not confirmation_token:
            return Response({
                "details": {
                    "confirmation_token": [
                        {
                            "message": "This field is required.",
                            "code": "required",
                        }
                    ]
                },
            }, status=status.HTTP_400_BAD_REQUEST)
        elif not username and confirmation_token:
            return Response({
                "details": {
                    "username": [
                        {
                            "message": "This field is required.",
                            "code": "required",
                        }
                    ]
                },
            }, status=status.HTTP_400_BAD_REQUEST)

class ResetPassword(APIView):
    permission_classes = []
    def get(self, request):
        confirmation_token = request.data.get('confirmation_token', False)
        username = request.data.get('username', False)
        password = request.data.get('password', False)
        if confirmation_token and username and password:
            try:
                user = User.objects.get(confirmation_token=confirmation_token, username=username)
                user.set_password(password)
                user.save()
                return Response({
                    'detail': 'Password was reset successfully.'
                })
            except User.DoesNotExist:
                return Response({
                    'detail': 'That user was not found.'
                }, status=status.HTTP_404_NOT_FOUND)
        elif not confirmation_token and username and password:
            return Response({
                "details": {
                    "confirmation_token": [
                        {
                            "message": "This field is required.",
                            "code": "required",
                        }
                    ]
                },
            }, status=status.HTTP_400_BAD_REQUEST)
        elif confirmation_token and not username and password:
            return Response({
                "details": {
                    "username": [
                        {
                            "message": "This field is required.",
                            "code": "required",
                        }
                    ]
                },
            }, status=status.HTTP_400_BAD_REQUEST)
        elif confirmation_token and username and not password:
            return Response({
                "details": {
                    "password": [
                        {
                            "message": "This field is required.",
                            "code": "required",
                        }
                    ]
                },
            }, status=status.HTTP_400_BAD_REQUEST)

class UpdateProfile(APIView):
    def post(self, request):
        try:
            user = User.objects.get(email=request.user)
            form = UserForm(request.data, instance=user)
            if form.is_valid():
                form_user = form.save()
                updated_user = model_to_dict(form_user, fields=['first_name', 'last_name', 'username', 'email'])
                updated_user.update({'user_avatar': settings.DOMAIN_URL + form_user.profile.avatar.url})
                return Response({
                    "details": "The user profile was updated.",
                    "user": updated_user,
                })
            else:
                return Response({
                        "details": json.loads(form.errors.as_json()),
                    }, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({
                    "details": "That user was not found.",
                }, status=status.HTTP_404_NOT_FOUND)

class UpdateAvatar(APIView):
    def post(self, request):
        logging.debug(request)
        if 'avatar' in request.FILES:
            user = User.objects.get(email=request.user)
            profile_form = AvatarForm({}, request.FILES, instance=user.profile)
            if profile_form.is_valid():
                profile = profile_form.save()
                updated_user = model_to_dict(user, fields=['first_name', 'last_name', 'username', 'email'])
                updated_user.update({'user_avatar': settings.DOMAIN_URL + profile.avatar.url})
                return Response({
                    "details": "The avatar was updated.",
                    "user": updated_user,
                })
            else:
                return Response({
                        "details": json.loads(profile_form.errors.as_json()),
                    }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                    "details": {
                        "avatar": [
                            {
                                "message": "This field is required.",
                                "code": "required",
                            }
                        ]
                    },
                }, status=status.HTTP_400_BAD_REQUEST)