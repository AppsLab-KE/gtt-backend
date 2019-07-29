import base64
import requests
from django.conf import settings
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from .models import (
    Tag, Post, Comment, Reply, Rating, Bookmark,
    )

User = get_user_model()

client = BackendApplicationClient(client_id=settings.SOCIAL_AUTH_BITBUCKET_OAUTH2_KEY)
oauth = OAuth2Session(client=client)
token = oauth.fetch_token(token_url='https://bitbucket.org/site/oauth2/access_token', client_id=settings.SOCIAL_AUTH_BITBUCKET_OAUTH2_KEY, client_secret=settings.SOCIAL_AUTH_BITBUCKET_OAUTH2_SECRET)
data ={
    'grant_type': 'convert_token',
    'client_id': 'adILJTDm3ztpMZlvzHQGSlpLbLZ3zri16uhOFinG',
    'client_secret': 'wIdleeJuPkoQhv7hc1m52hXBv3HBtuHsP2JiL6f1RwPycc6vIAoDPPDvijOzaGFfJJT0wRhGHSXG7lboWxNIke0tVMRDChI8GUSN6qYwwpkdyaDKuD2osQ8LauDzbjT7',
    'backend': 'bitbucket-oauth2',
    'token': token['access_token'],
}
authorization_response = requests.post(settings.DOMAIN_URL + '/api/v1/oauth2/convert-token', data=data)

class PostsTest(TestCase):
    def setUp(self):
        self.client = Client()
        

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
