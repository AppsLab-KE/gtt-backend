import base64
import json
import requests
from django.conf import settings
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
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
authorization_response_dict = json.loads(authorization_response.text)
access_token = authorization_response_dict['access_token']

class PostsTest(TestCase):
    create_post_data = {
        'post_heading': 'This is a test heading',
        'post_body': 'This is a test body.',
        'read_duration': '1',
        'tag': 'UX',
        'tag': 'UI',
        'tag': 'Test',
    }

    update_post_data = {
        'post_heading': 'This is an update of test heading',
        'post_body': 'This is an update of test body.',
        'read_duration': '1.5',
        'tag': 'Machine learning',
        'tag': 'DL',
        'tag': 'Reinforcement',
    }

    def setUp(self):
        self.client = Client()

    def test_posts(self):
        create_post_response = self.client.post(reverse('create_post'), data=self.create_post_data)
        get_tag_posts_response = self.client.get(reverse('view_tag_posts', kwargs={'tag_name': 'UX'}))
        get_post_response = self.client.get(reverse('view_post', kwargs={'username':, 'slug': }))
        update_post_response = self.client.post(reverse('update_post', kwargs={'slug':}), data=self.update_post_data)
        delete_post_response = self.client.post(reverse('delete_post', kwargs={'slug': }))

    def test_tags(self):
        get_tag_posts = self.client.get()

    def test_rating(self):
        pass

    def test_comments(self):
        pass

    def test_replies(self):
        pass

    def test_bookmarks(self):
        pass

