from django.conf import settings
from django.urls import path
from .apis import MakeWriter

urlpatterns = [
    path(settings.API + 'users/<username>/make_writer', MakeWriter.as_view(), name='make_writer'),
]