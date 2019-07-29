from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from .models import (
    Tag, Post, Comment, Reply, Rating, Bookmark,
    )

User = get_user_model()

class PostModelTest(TestCase):

    def test_tags(self):
        pass

    def test_posts(self):
        pass

    def test_comments(self):
        pass

    def test_replies(self):
        pass

    def test_bookmarks(self):
        pass

