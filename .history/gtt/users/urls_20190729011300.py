from django.conf import settings
from django.urls import path
from .apis import MakeWriter, TestMakeWriter

urlpatterns = [
    path(settings.API + 'users/<username>/make_writer', MakeWriter.as_view(), name='make_writer'),
    path(settings.API + 'users/<username>/test_make_writer', TestMakeWriter.as_view(), name='test_make_writer'),
]