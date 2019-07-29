from django.conf import settings
from django.urls import path
from .apis import RequestWritership, MakeWriter, TestMakeWriter, TestAccessToken, UpdateAvatar

urlpatterns = [
    path(settings.API + 'users/request_writership', RequestWritership.as_view(), name='request_writership'),
    path(settings.API + 'users/<username>/make_writer', MakeWriter.as_view(), name='make_writer'),
    path(settings.API + 'users/<username>/test_make_writer', TestMakeWriter.as_view(), name='test_make_writer'),
    path(settings.API + 'users/access_token/test', TestAccessToken.as_view(), name='test_access_token'),
    path(settings.API + 'users/profile/avatar/update', UpdateAvatar.as_view(), name='update_avatar'),
]