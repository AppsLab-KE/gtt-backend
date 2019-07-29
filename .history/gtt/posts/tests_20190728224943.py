import base64
import json
import requests
from django.conf import settings
from django.test import TestCase
from rest_framework.test import APIClient
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
        self.client = APIClient()
        self.client.credentials(Authorization='Bearer ' + access_token})

    def test_posts(self):
        create_post_response = self.client.post(settings.DOMAIN_URL + reverse('posts:create_post'), data=self.create_post_data)
        self.assertEquals(create_post_response.status_code, '200')
        tag_posts_response = self.client.get(settings.DOMAIN_URL + reverse('posts:view_tag_posts', kwargs={'tag_name': 'UX'}))
        self.assertEquals(tag_posts_response.status_code, '200')
        update_post_response = self.client.post(settings.DOMAIN_URL + reverse('posts:update_post', kwargs={'slug': tag_posts_response.json()[0]['slug']}), data=self.update_post_data)
        self.assertEquals(update_post_response.status_code, '200')
        delete_post_response = self.client.post(settings.DOMAIN_URL + reverse('posts:delete_post', kwargs={'slug': tag_posts_response.json()[0]['slug']}))
        self.assertEquals(delete_post_response.status_code, '200')

    def test_ratings(self):
        create_post_response = self.client.post(settings.DOMAIN_URL + reverse('posts:create_post'), data=self.create_post_data)
        self.assertEquals(create_post_response.status_code, '200')
        tag_posts_response = self.client.get(settings.DOMAIN_URL + reverse('posts:view_tag_posts', kwargs={'tag_name': 'UX'}))
        self.assertEquals(tag_posts_response.status_code, '200')
        view_post_response = self.client.get(settings.DOMAIN_URL + reverse('posts:view_post', kwargs={'username': tag_posts_response.json()[0]['post_author']['username'], 'slug': tag_posts_response.json()[0]['slug']}))
        self.assertEquals(view_post_response.status_code, '200')
        like_post_response = self.client.post(settings.DOMAIN_URL + reverse('posts:rate_post', kwargs={'slug': tag_posts_response.json()[0]['slug']}), data={'rating': 1})
        self.assertEquals(like_post_response.status_code, '200')
        rated_posts_response = self.client.post(settings.DOMAIN_URL + reverse('posts:view_rated_posts'))
        self.assertEquals(rated_posts_response.status_code, '200')
        dislike_post_response = self.client.post(settings.DOMAIN_URL + reverse('posts:rate_post', kwargs={'slug': tag_posts_response.json()[0]['slug']}), data={'rating': 0})
        self.assertEquals(dislike_post_response.status_code, '200')
        delete_post_response = self.client.post(settings.DOMAIN_URL + reverse('posts:delete_post', kwargs={'slug': tag_posts_response.json()[0]['slug']}))
        self.assertEquals(delete_post_response.status_code, '200')

    def test_comments(self):
        create_post_response = self.client.post(settings.DOMAIN_URL + reverse('posts:create_post'), data=self.create_post_data)
        self.assertEquals(create_post_response.status_code, '200')
        tag_posts_response = self.client.get(settings.DOMAIN_URL + reverse('posts:view_tag_posts', kwargs={'tag_name': 'UX'}))
        self.assertEquals(tag_posts_response.status_code, '200')
        create_comment_response = self.client.post(settings.DOMAIN_URL + reverse('posts:create_comment', kwargs={'slug': tag_posts_response.json()[0]['slug']}), data={'comment': 'This is a test comment.'})
        self.assertEquals(create_comment_response.status_code, '200')
        view_post_comments_response = self.client.post(settings.DOMAIN_URL + reverse('posts:view_comments', kwargs={'slug': tag_posts_response.json()[0]['slug']}))
        self.assertEquals(view_post_comments_response.status_code, '200')
        update_post_comment_response = self.client.post(settings.DOMAIN_URL + reverse('posts:update_comment', kwargs={'resource_key': view_post_comments_response.json()[0]['resource_key']}), data={'comment': 'This is an updated test comment.'})
        self.assertEquals(update_post_comment_response.status_code, '200')
        delete_post_comment_response = self.client.post(settings.DOMAIN_URL + reverse('posts:delete_comment', kwargs={'resource_key': view_post_comments_response.json()[0]['resource_key']}))
        self.assertEquals(delete_post_comment_response.status_code, '200')
        delete_post_response = self.client.post(settings.DOMAIN_URL + reverse('posts:delete_post', kwargs={'slug': tag_posts_response.json()[0]['slug']}))
        self.assertEquals(delete_post_response.status_code, '200')

    def test_replies(self):
        create_post_response = self.client.post(settings.DOMAIN_URL + reverse('posts:create_post'), data=self.create_post_data)
        self.assertEquals(create_post_response.status_code, '200')
        tag_posts_response = self.client.get(settings.DOMAIN_URL + reverse('posts:view_tag_posts', kwargs={'tag_name': 'UX'}))
        self.assertEquals(tag_posts_response.status_code, '200')
        create_comment_response = self.client.post(settings.DOMAIN_URL + reverse('posts:create_comment', kwargs={'slug': tag_posts_response.json()[0]['slug']}), data={'comment': 'This is a test comment.'})
        self.assertEquals(create_comment_response.status_code, '200')
        view_post_comments_response = self.client.post(settings.DOMAIN_URL + reverse('posts:view_comments', kwargs={'slug': tag_posts_response.json()[0]['slug']}))
        self.assertEquals(view_post_comments_response.status_code, '200')
        create_reply_response = self.client.post(settings.DOMAIN_URL + reverse('posts:create_reply', kwargs={'resource_key': view_post_comments_response.json()[0]['resource_key']}), data={'reply': 'This is a test reply.'})
        self.assertEquals(create_reply_response.status_code, '200')
        update_reply_response = self.client.post(settings.DOMAIN_URL + reverse('posts:update_reply', kwargs={'resource_key': view_post_comments_response.json()[0]['resource_key']}), data={'reply': 'This is an updated test reply.'})
        self.assertEquals(update_reply_response.status_code, '200')
        delete_reply_response = self.client.post(settings.DOMAIN_URL + reverse('posts:delete_reply', kwargs={'resource_key': view_post_comments_response.json()[0]['resource_key']}))
        self.assertEquals(delete_reply_response.status_code, '200')
        delete_post_response = self.client.post(settings.DOMAIN_URL + reverse('posts:delete_post', kwargs={'slug': tag_posts_response.json()[0]['slug']}))
        self.assertEquals(delete_post_response.status_code, '200')

    def test_bookmarks(self):
        create_post_response = self.client.post(settings.DOMAIN_URL + reverse('posts:create_post'), data=self.create_post_data)
        self.assertEquals(create_post_response.status_code, '200')
        tag_posts_response = self.client.get(settings.DOMAIN_URL + reverse('posts:view_tag_posts', kwargs={'tag_name': 'UX'}))
        self.assertEquals(tag_posts_response.status_code, '200')
        create_bookmark_response = self.client.post(settings.DOMAIN_URL + reverse('posts:create_bookmark', kwargs={'slug': tag_posts_response.json()[0]['slug']}))
        self.assertEquals(create_bookmark_response.status_code, '200')
        view_bookmarks_response = self.client.get(settings.DOMAIN_URL + reverse('view_bookmarks'))
        self.assertEquals(view_bookmarks_response.status_code, '200')
        delete_bookmark_response = self.client.post(settings.DOMAIN_URL + reverse('posts:delete_bookmark', kwargs={'resource_key': view_bookmarks_response.json()[0]['resource_key']}))
        self.assertEquals(delete_bookmark_response.status_code, '200')
        delete_post_response = self.client.post(settings.DOMAIN_URL + reverse('posts:delete_post', kwargs={'slug': tag_posts_response.json()[0]['slug']}))
        self.assertEquals(delete_post_response.status_code, '200')
