from django.conf import settings
from django.urls import path
from .apis import (
    RequestWritership, MakeWriter, TestMakeWriter, BackendAccessToken, Oauth2TokenView, RevokeOauth2TokenView,
    InvalidateSessions, TestAccessToken, UpdateAvatar, UpdateProfile, RequestResetPassword, CheckResetParams, ResetPassword,
)

urlpatterns = [
    path(settings.API + 'users/request_writership', RequestWritership.as_view(), name='request_writership'),
    path(settings.API + 'users/<username>/make_writer', MakeWriter.as_view(), name='make_writer'),
    path(settings.API + 'users/<username>/test_make_writer', TestMakeWriter.as_view(), name='test_make_writer'),
    path(settings.API + 'auth/<backend_name>', BackendAccessToken.as_view(), name='backend_access_token'),
    path(settings.API + 'auth/oauth2/token', Oauth2TokenView.as_view(), name='oauth2_token_api'),
    path(settings.API + 'auth/oauth2/invalidate-sessions', InvalidateSessions.as_view(), name='invalidate_oauth2_sessions'),
    path(settings.API + 'auth/oauth2/revoke-token', RevokeOauth2TokenView.as_view(), name='revoke_oauth2_token_api'),
    path(settings.API + 'users/access_token/test', TestAccessToken.as_view(), name='test_access_token'),
    path(settings.API + 'users/profile/avatar/update', UpdateAvatar.as_view(), name='update_avatar'),
    path(settings.API + 'users/profile/update', UpdateProfile.as_view(), name='update_profile'),
    path(settings.API + 'users/password/reset/request', RequestResetPassword.as_view(), name='request_reset_password'),
    path(settings.API + 'users/password/reset/check', CheckResetParams.as_view(), name='check_reset_params'),
    path(settings.API + 'users/password/reset', ResetPassword.as_view(), name='reset_password'),
]