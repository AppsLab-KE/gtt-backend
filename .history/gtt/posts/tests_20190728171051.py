from django.conf import settings
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from .models import (
    Tag, Post, Comment, Reply, Rating, Bookmark,
    )

User = get_user_model()

class PostsTest(TestCase):
    def setUp(self):
        self.client = Client()
        response = self.client.post('https://bitbucket.org/site/oauth2/access_token',
        {
            'user': settings.SOCIAL_AUTH_BITBUCKET_OAUTH2_KEY, 
            'password': SOCIAL_AUTH_BITBUCKET_OAUTH2_SECRET,
            'grant_type': 'client_credentials',
        })
    def test_posts(self):
        pass

    def test_tags(self):

    def test_comments(self):
        pass

    def test_replies(self):
        pass

    def test_bookmarks(self):
        pass

