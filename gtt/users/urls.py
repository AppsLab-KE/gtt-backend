from django.conf import settings
from django.urls import path
from .apis import (
    RequestWritership, MakeWriter, TestMakeWriter, BackendAccessToken,TestAccessToken, UpdateAvatar,
    UpdateProfile, RequestResetPassword, CheckResetParams, ResetPassword,
)

urlpatterns = [
    path(settings.API + 'users/request_writership', RequestWritership.as_view(), name='request_writership'),
    path(settings.API + 'users/<username>/make_writer', MakeWriter.as_view(), name='make_writer'),
    path(settings.API + 'users/<username>/test_make_writer', TestMakeWriter.as_view(), name='test_make_writer'),
    path(settings.API + 'auth/<backend_name>', BackendAccessToken.as_view(), name='backend_access_token'),
    path(settings.API + 'users/access_token/test', TestAccessToken.as_view(), name='test_access_token'),
    path(settings.API + 'users/profile/avatar/update', UpdateAvatar.as_view(), name='update_avatar'),
    path(settings.API + 'users/profile/update', UpdateProfile.as_view(), name='update_profile'),
    path(settings.API + 'users/password/reset/request', RequestResetPassword.as_view(), name='request_reset_password'),
    path(settings.API + 'users/password/reset/check', CheckResetParams.as_view(), name='check_reset_params'),
    path(settings.API + 'users/password/reset', ResetPassword.as_view(), name='reset_password'),
]