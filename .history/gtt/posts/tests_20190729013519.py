import os
import base64
import json
import requests
import datetime
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from oauth2_provider.models import Application, AccessToken
from django.test import tag
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import (
    Tag, Post, Comment, Reply, Rating, Bookmark,
    )

User = get_user_model()

class PostsTest(APITestCase):
    create_post_data = dict()
    update_post_data = dict()

    def setUp(self):
        self.client = APIClient()
        self.test_user = User.objects.create_user(
            first_name='test',
            last_name='user',
            username='testuser',
            email='test@example.com',
            password='testpassword',
            )
        self.application = Application(
            name = "Test Application",
            redirect_uris = "http://localhost:8000",
            user = self.test_user,
            client_type = Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type = Application.GRANT_AUTHORIZATION_CODE,
        )
        self.application.save()
        
    def tearDown(self):
        self.application.delete()
        self.test_user.delete()
        self.create_post_data = dict()
        self.update_post_data = dict()

    @tag('posts')
    def test_posts(self):
        tok = AccessToken.objects.create(
            user = self.test_user,
            token = '1234567890',
            application = self.application,
            scope = 'read write',
            expires = timezone.now() + datetime.timedelta(days=1)
        )
        auth_headers = {
            'HTTP_AUTHORIZATION': 'Bearer ' + tok.token,
        }
        make_writer_response = self.client.post(reverse('users:test_make_writer', kwargs={'username': self.test_user.username}), **auth_headers)
        self.assertEquals(make_writer_response.status_code, status.HTTP_200_OK)
        with open(os.path.join(os.path.dirname(__file__), 'test_images/create_post.png'), 'rb') as create_post_image:
            self.create_post_data = {
                'post_heading': 'This is a test heading',
                'post_heading_image': create_post_image,
                'post_body': 'This is a test body.',
                'read_duration': '1',
                'tag': 'UX',
            }
            create_post_response = self.client.post(reverse('posts:create_post'), data=self.create_post_data, **auth_headers)
            self.assertEquals(create_post_response.status_code, status.HTTP_200_OK)
        tag_posts_response = self.client.get(reverse('posts:view_tag_posts', kwargs={'tag_name': 'UX'}), **auth_headers)
        self.assertEquals(tag_posts_response.status_code, status.HTTP_200_OK)
        with open(os.path.join(os.path.dirname(__file__), 'test_images/update_post.png'), 'rb') as update_post_image:
            self.update_post_data = {
                'post_heading': 'This is an update of test heading',
                'post_heading_image': update_post_image,
                'post_body': 'This is an update of test body.',
                'read_duration': '1.5',
                'tag': 'Machine learning',
            }
            update_post_response = self.client.post(reverse('posts:update_post', kwargs={'slug': tag_posts_response.json()[0]['slug']}), data=self.update_post_data, **auth_headers)
            self.assertEquals(update_post_response.status_code, status.HTTP_200_OK)
        delete_post_response = self.client.post(reverse('posts:delete_post', kwargs={'slug': tag_posts_response.json()[0]['slug']}), **auth_headers)
        self.assertEquals(delete_post_response.status_code, status.HTTP_200_OK)

    @tag('ratings')
    def test_ratings(self):
        tok = AccessToken.objects.create(
            user = self.test_user,
            token = '1234567890',
            application = self.application,
            scope = 'read write',
            expires = timezone.now() + datetime.timedelta(days=1)
        )
        auth_headers = {
            'HTTP_AUTHORIZATION': 'Bearer ' + tok.token,
        }
        make_writer_response = self.client.post(reverse('users:test_make_writer', kwargs={'username': self.test_user.username}), **auth_headers)
        self.assertEquals(make_writer_response.status_code, status.HTTP_200_OK)
        with open(os.path.join(os.path.dirname(__file__), 'test_images/create_post.png'), 'rb') as create_post_image:
            self.create_post_data = {
                'post_heading': 'This is a test heading',
                'post_heading_image': create_post_image,
                'post_body': 'This is a test body.',
                'read_duration': '1',
                'tag': 'UX',
            }
            create_post_response = self.client.post(reverse('posts:create_post'), data=self.create_post_data, **auth_headers)
            self.assertEquals(create_post_response.status_code, status.HTTP_200_OK)
        tag_posts_response = self.client.get(reverse('posts:view_tag_posts', kwargs={'tag_name': 'UX'}))
        self.assertEquals(tag_posts_response.status_code, status.HTTP_200_OK)
        view_post_response = self.client.get(reverse('posts:view_post', kwargs={'username': tag_posts_response.json()[0]['post_author']['username'], 'slug': tag_posts_response.json()[0]['slug']}))
        self.assertEquals(view_post_response.status_code, status.HTTP_200_OK)
        like_post_response = self.client.post(reverse('posts:rate_post', kwargs={'slug': tag_posts_response.json()[0]['slug']}), data={'rating': 1})
        self.assertEquals(like_post_response.status_code, status.HTTP_200_OK)
        rated_posts_response = self.client.post(reverse('posts:view_rated_posts'))
        self.assertEquals(rated_posts_response.status_code, status.HTTP_200_OK)
        dislike_post_response = self.client.post(reverse('posts:rate_post', kwargs={'slug': tag_posts_response.json()[0]['slug']}), data={'rating': 0})
        self.assertEquals(dislike_post_response.status_code, status.HTTP_200_OK)
        delete_post_response = self.client.post(reverse('posts:delete_post', kwargs={'slug': tag_posts_response.json()[0]['slug']}))
        self.assertEquals(delete_post_response.status_code, status.HTTP_200_OK)

    @tag('comments')
    def test_comments(self):
        tok = AccessToken.objects.create(
            user = self.test_user,
            token = '1234567890',
            application = self.application,
            scope = 'read write',
            expires = timezone.now() + datetime.timedelta(days=1)
        )
        auth_headers = {
            'HTTP_AUTHORIZATION': 'Bearer ' + tok.token,
        }
        make_writer_response = self.client.post(reverse('users:test_make_writer', kwargs={'username': self.test_user.username}), **auth_headers)
        self.assertEquals(make_writer_response.status_code, status.HTTP_200_OK)
        with open(os.path.join(os.path.dirname(__file__), 'test_images/create_post.png'), 'rb') as create_post_image:
            self.create_post_data = {
                'post_heading': 'This is a test heading',
                'post_heading_image': create_post_image,
                'post_body': 'This is a test body.',
                'read_duration': '1',
                'tag': 'UX',
            }
            create_post_response = self.client.post(reverse('posts:create_post'), data=self.create_post_data, **auth_headers)
            self.assertEquals(create_post_response.status_code, status.HTTP_200_OK)
        tag_posts_response = self.client.get(reverse('posts:view_tag_posts', kwargs={'tag_name': 'UX'}), **auth_headers)
        self.assertEquals(tag_posts_response.status_code, status.HTTP_200_OK)
        create_comment_response = self.client.post(reverse('posts:create_comment', kwargs={'slug': tag_posts_response.json()[0]['slug']}), data={'comment': 'This is a test comment.'}, **auth_headers)
        self.assertEquals(create_comment_response.status_code, status.HTTP_200_OK)
        view_post_comments_response = self.client.post(reverse('posts:view_comments', kwargs={'slug': tag_posts_response.json()[0]['slug']}), **auth_headers)
        self.assertEquals(view_post_comments_response.status_code, status.HTTP_200_OK)
        update_post_comment_response = self.client.post(reverse('posts:update_comment', kwargs={'resource_key': view_post_comments_response.json()[0]['resource_key']}), data={'comment': 'This is an updated test comment.'}, **auth_headers)
        self.assertEquals(update_post_comment_response.status_code, status.HTTP_200_OK)
        delete_post_comment_response = self.client.post(reverse('posts:delete_comment', kwargs={'resource_key': view_post_comments_response.json()[0]['resource_key']}), **auth_headers)
        self.assertEquals(delete_post_comment_response.status_code, status.HTTP_200_OK)
        delete_post_response = self.client.post(reverse('posts:delete_post', kwargs={'slug': tag_posts_response.json()[0]['slug']}), **auth_headers)
        self.assertEquals(delete_post_response.status_code, status.HTTP_200_OK)

    @tag('replies')
    def test_replies(self):
        tok = AccessToken.objects.create(
            user = self.test_user,
            token = '1234567890',
            application = self.application,
            scope = 'read write',
            expires = timezone.now() + datetime.timedelta(days=1)
        )
        auth_headers = {
            'HTTP_AUTHORIZATION': 'Bearer ' + tok.token,
        }
        make_writer_response = self.client.post(reverse('users:test_make_writer', kwargs={'username': self.test_user.username}), **auth_headers)
        self.assertEquals(make_writer_response.status_code, status.HTTP_200_OK)
        with open(os.path.join(os.path.dirname(__file__), 'test_images/create_post.png'), 'rb') as create_post_image:
            self.create_post_data = {
                'post_heading': 'This is a test heading',
                'post_heading_image': create_post_image,
                'post_body': 'This is a test body.',
                'read_duration': '1',
                'tag': 'UX',
            }
            create_post_response = self.client.post(reverse('posts:create_post'), data=self.create_post_data, **auth_headers)
            self.assertEquals(create_post_response.status_code, status.HTTP_200_OK)
        tag_posts_response = self.client.get(reverse('posts:view_tag_posts', kwargs={'tag_name': 'UX'}), **auth_headers)
        self.assertEquals(tag_posts_response.status_code, status.HTTP_200_OK)
        create_comment_response = self.client.post(reverse('posts:create_comment', kwargs={'slug': tag_posts_response.json()[0]['slug']}), data={'comment': 'This is a test comment.'}, **auth_headers)
        self.assertEquals(create_comment_response.status_code, status.HTTP_200_OK)
        view_post_comments_response = self.client.post(reverse('posts:view_comments', kwargs={'slug': tag_posts_response.json()[0]['slug']}), **auth_headers)
        self.assertEquals(view_post_comments_response.status_code, status.HTTP_200_OK)
        create_reply_response = self.client.post(reverse('posts:create_reply', kwargs={'resource_key': view_post_comments_response.json()[0]['resource_key']}), data={'reply': 'This is a test reply.'}, **auth_headers)
        self.assertEquals(create_reply_response.status_code, status.HTTP_200_OK)
        update_reply_response = self.client.post(reverse('posts:update_reply', kwargs={'resource_key': view_post_comments_response.json()[0]['resource_key']}), data={'reply': 'This is an updated test reply.'}, **auth_headers)
        self.assertEquals(update_reply_response.status_code, status.HTTP_200_OK)
        delete_reply_response = self.client.post(reverse('posts:delete_reply', kwargs={'resource_key': view_post_comments_response.json()[0]['resource_key']}), **auth_headers)
        self.assertEquals(delete_reply_response.status_code, status.HTTP_200_OK)
        delete_post_response = self.client.post(reverse('posts:delete_post', kwargs={'slug': tag_posts_response.json()[0]['slug']}), **auth_headers)
        self.assertEquals(delete_post_response.status_code, status.HTTP_200_OK)

    @tag('bookmarks')
    def test_bookmarks(self):
        tok = AccessToken.objects.create(
            user = self.test_user,
            token = '1234567890',
            application = self.application,
            scope = 'read write',
            expires = timezone.now() + datetime.timedelta(days=1)
        )
        auth_headers = {
            'HTTP_AUTHORIZATION': 'Bearer ' + tok.token,
        }
        make_writer_response = self.client.post(reverse('users:test_make_writer', kwargs={'username': self.test_user.username}), **auth_headers)
        self.assertEquals(make_writer_response.status_code, status.HTTP_200_OK)
        with open(os.path.join(os.path.dirname(__file__), 'test_images/create_post.png'), 'rb') as create_post_image:
            self.create_post_data = {
                'post_heading': 'This is a test heading',
                'post_heading_image': create_post_image,
                'post_body': 'This is a test body.',
                'read_duration': '1',
                'tag': 'UX',
            }
            create_post_response = self.client.post(reverse('posts:create_post'), data=self.create_post_data, **auth_headers)
            self.assertEquals(create_post_response.status_code, status.HTTP_200_OK)
        tag_posts_response = self.client.get(reverse('posts:view_tag_posts', kwargs={'tag_name': 'UX'}), **auth_headers)
        self.assertEquals(tag_posts_response.status_code, status.HTTP_200_OK)
        create_bookmark_response = self.client.post(reverse('posts:create_bookmark', kwargs={'slug': tag_posts_response.json()[0]['slug']}), **auth_headers)
        self.assertEquals(create_bookmark_response.status_code, status.HTTP_200_OK)
        view_bookmarks_response = self.client.get(reverse('posts:view_bookmarks'), **auth_headers)
        self.assertEquals(view_bookmarks_response.status_code, status.HTTP_200_OK)
        delete_bookmark_response = self.client.post(reverse('posts:delete_bookmark', kwargs={'resource_key': view_bookmarks_response.json()[0]['resource_key']}), **auth_headers)
        self.assertEquals(delete_bookmark_response.status_code, status.HTTP_200_OK)
        delete_post_response = self.client.post(reverse('posts:delete_post', kwargs={'slug': tag_posts_response.json()[0]['slug']}), **auth_headers)
        self.assertEquals(delete_post_response.status_code, status.HTTP_200_OK)

