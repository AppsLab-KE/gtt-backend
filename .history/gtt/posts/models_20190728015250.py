import os
import random
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

def unique_photo_path(instance, filename):
    basefilename, file_extension= os.path.splitext(filename)
    chars= 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'
    randomstr= ''.join((random.choice(chars)) for x in range(10))
    return 'post_photos/{id}/{basename}{randomstring}{ext}'.format(id=instance.id, basename=basefilename, randomstring=randomstr, ext=file_extension)

class ArchivedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(archived=False)

class Tag(models.Model):
    tag_name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=150)
    resource_key = models.CharField(max_length=50, unique=True)
    archived = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)
    objects = ArchivedManager()

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('view_tag', kwargs={'resource_key': self.resource_key})

class Post(models.Model):
    post_heading = models.CharField(max_length=100)
    post_heading_image = models.ImageField(upload_to=unique_photo_path, null=True, blank=True)
    post_body = models.TextField()
    post_author = models.ForeignKey(User, related_name='posts', null=True, on_delete=models.SET_NULL)
    slug = models.SlugField(max_length=150)
    tags = models.ManyToManyField("Tag", related_name='posts')
    read_duration = models.CharField(max_length=10, default="0 min")
    resource_key = models.CharField(max_length=50, unique=True)
    archived = models.BooleanField(default=False)
    date_published = models.DateTimeField(auto_now_add=True)
    objects = ArchivedManager()

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('view_post', kwargs={'slug': self.slug})

class Comment(models.Model):
    commented_post = models.ForeignKey("Post", related_name='comments', null=True, on_delete=models.SET_NULL)
    user_that_commented = models.ForeignKey(User, related_name='comments', null=True, on_delete=models.SET_NULL)
    comment = models.TextField()
    resource_key = models.CharField(max_length=50, unique=True)
    archived = models.BooleanField(default=False)
    date_commented = models.DateTimeField(auto_now_add=True)
    objects = ArchivedManager()

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('view_comment', kwargs={'resource_key': self.resource_key})

class Reply(models.Model):
    replied_comment = models.ForeignKey("Comment", related_name='replies', null=True, on_delete=models.SET_NULL)
    user_that_replied = models.ForeignKey(User, related_name='replies', null=True, on_delete=models.SET_NULL)
    reply = models.TextField()
    resource_key = models.CharField(max_length=50, unique=True)
    archived = models.BooleanField(default=False)
    date_replied = models.DateTimeField(auto_now_add=True)
    objects = ArchivedManager()

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('view_reply', kwargs={'resource_key': self.resource_key})

class Rating(models.Model):
    rated_post = models.ForeignKey("Post", related_name='ratings',null=True, on_delete=models.SET_NULL)
    user_that_rated = models.ForeignKey(User, related_name='ratings', null=True, on_delete=models.SET_NULL)
    rating = models.BooleanField(default=False)
    resource_key = models.CharField(max_length=50, unique=True)
    archived = models.BooleanField(default=False)
    date_rated = models.DateTimeField(auto_now_add=True)
    objects = ArchivedManager()

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('view_rating', kwargs={'resource_key': self.resource_key})

class Bookmark(models.Model):
    bookmarked_post = models.ForeignKey("Post", related_name='bookmarks', null=True, on_delete=models.SET_NULL)
    user_that_bookmarked = models.ForeignKey(User, related_name='bookmarks', null=True, on_delete=models.SET_NULL)
    resource_key = models.CharField(max_length=50, unique=True)
    archived = models.BooleanField(default=False)
    date_bookmarked = models.DateTimeField(auto_now_add=True)
    objects = ArchivedManager()

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('view_bookmark', kwargs={'resource_key': self.resource_key})