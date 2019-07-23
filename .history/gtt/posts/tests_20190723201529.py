from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from .models import (
    Tag, Post, Comment, Reply, Rating, Bookmark, Archive)

User = get_user_model()

class PostTest(TestCase):

    def test_tag_model(self):
        Tag.objects.create(tag_name="UX")
        Tag.objects.create(tag_name="UI")
        tag1 = Tag.objects.get(tag_name="UX")
        tag2 = Tag.objects.get(tag_name="UI")
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

    def test_post_model(self):
        article = """Adam West was born William West Anderson on September 19, 1928, 
        in Walla Walla, Washington. His father, Otto Anderson (1903–1984) was a farmer; 
        and his mother, Audrey Volenne (née Speer; 1906–1969) was an opera singer and concert pianist who left her Hollywood dreams to care for her family.
        Following her example, West told his father as a young man that he intended to go to Hollywood after completing school. 
        He moved to Seattle with his mother when he was 15, following his parents' divorce. 
        West attended Walla Walla High School during his freshman and sophomore years, and later enrolled in Lakeside School in Seattle.
        He attended Whitman College but studied at University of Puget Sound during the fall semester of 1949. 
        He graduated with a bachelor's degree in literature and a minor in psychology from Whitman College in Walla Walla, 
        where he was a member of the Gamma Zeta Chapter of the Beta Theta Pi fraternity. He also participated on the speech and debate team. 
        Drafted into the United States Army, he served as an announcer on American Forces Network television. 
        After his discharge, he worked as a milkman before moving to Hawaii to pursue a career in television."""
        tag = Tag.objects.create(tag_name="UX")
        user = User(first_name="John", last_name="Doe", email="johndoe@mail.com", username="johndoe")
        user.save()
        post = Post(
            post_heading="Adam West",
            post_body=article,
        )
        post.post_author = user
        post.save()
        post.tags.add(tag)
        post1 = Post.objects.get(post_heading="Adam West")
        posts = Post.objects.all()
        self.assertEquals(post1.post_heading,"Adam West")
        print(post1.get_absolute_url())
        print(posts)
        post1.delete()
        tag.delete()
        user.delete()
        self.assertNotEquals(post1.post_heading,"Adam West")

