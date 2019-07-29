import base64
from django.conf import settings
from django.test import TestCase, Client
from rest_framework.test import RequestsClient
from django.contrib.auth import get_user_model
from requests.auth import HTTPBasicAuth
from .models import (
    Tag, Post, Comment, Reply, Rating, Bookmark,
    )

User = get_user_model()

class PostsTest(TestCase):
    def setUp(self):
        self.client = RequestsClient()
        self.client.auth = HTTPBasicAuth(settings.SOCIAL_AUTH_BITBUCKET_OAUTH2_KEY, settings.SOCIAL_AUTH_BITBUCKET_OAUTH2_SECRET)
        response = self.client.post('https://bitbucket.org/site/oauth2/access_token', {'grant_type': 'client_credentials'})
        print(response.status_code)

    def test_posts(self):
        pass

    def test_tags(self):
        pass

    def test_comments(self):
        pass

    def test_replies(self):
        pass

    def test_bookmarks(self):
        pass

