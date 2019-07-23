from django.test import TestCase, Client
from .models import (
    Tag, Post, Comment, Reply, Rating, Bookmark, Archive)

class PostTest(TestCase):
    tag = 
    tags = 
    post = 
    posts = 
    comment = 
    comments = 
    reply = 
    replies = 
    rating = 
    ratings = 
    bookmark = 
    bookmarks = 
    archive = 
    archives = 

    #def setUp(self):

    #def tearDown(self):

    def test_tag_model(self):
        Tags.objects.create(tag_name="UX")
        Tags.objects.create(tag_name="UI")
        tag1 = tag.objects.get(tag_name="UX")
        tag2 = tag.objects.get(tag_name="UI")
        tags = Tag.objects.all()
        self.assertEquals(tag1.tag_name, "UX")
        self.assertEquals(tag2.tag_name, "UI")
        print(tag1.get_absolute_url())
        print(tag2.get_absolute_url())
        print(tags)
        tag1.delete()
        tag2.delete()
        self.assertNotEquals(tag1.tag_name, "UX")
        self.assertNotEquals(tag2.tag_name, "UI")

