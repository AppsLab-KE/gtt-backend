import string
import secrets
from django.db import models
from django.http import Http404
from django.utils.text import slugify
from django.shortcuts import get_object_or_404

def get_random_token(length):
    token = str()
    alphabet = string.ascii_letters + string.digits 
    while True: 
        random_token = ''.join(secrets.choice(alphabet) for i in range(length)) 
        if (any(c.islower() for c in random_token) and any(c.isupper()  
            for c in random_token) and sum(c.isdigit() for c in random_token) >= 3): 
            token = random_token
            break
    return token

def get_resource_key(model):
    token = str()
    while True:
        token = get_random_token(50)
        try:
            get_object_or_404(model, resource_key=token)
            continue
        except Http404:
            break
    return token

def get_slug_key(slug):
    slug_token = str()
    while True:
        slug_token = slug + "-" + get_random_token(20)
        try:
            Post.objects.get(slug=slug_token)
            continue
        except Post.DoesNotExist:
            break
    return slug_token

class ArchivedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(archived=False)


class Tag(models.Model):
    tag_name = models.CharField(max_length=50)
    slug = models.SlugField()
    resource_key = models.CharField(max_length=50, unique=True)
    archived = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)
    objects = ArchivedManager()

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('view_tag', kwargs={'resource_key': self.resource_key})
    
    def save(self, *args, **kwargs):
        self.resource_key = get_resource_key(Tag)
        self.slug = slugify(self.tag_name)
        super(Tag, self).save(*args, **kwargs)

class Post(models.Model):
    post_heading = models.CharField(max_length=100)
    post_body = models.TextField()
    post_author = models.ForeignKey("User", related_name='posts', null=True, on_delete=models.SET_NULL)
    slug = models.SlugField()
    tags = models.ManyToManyField("Tag", related_name='tags')
    resource_key = models.CharField(max_length=50, unique=True)
    archived = models.BooleanField(default=False)
    date_published = models.DateTimeField(auto_now_add=True)
    objects = ArchivedManager()

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('view_post', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        self.resource_key = get_resource_key(Post)
        self.slug = get_slug_key(slugify(self.post_heading))
        super(Post, self).save(*args, **kwargs)

class Comment(models.Model):
    commented_post = models.ForeignKey("Post", related_name='comments', null=True, on_delete=models.SET_NULL)
    user_that_commented = models.ForeignKey("User", related_name='comments', null=True, on_delete=models.SET_NULL)
    comment = models.TextField()
    resource_key = models.CharField(max_length=50, unique=True)
    archived = models.BooleanField(default=False)
    date_commented = models.DateTimeField(auto_now_add=True)
    objects = ArchivedManager()

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('view_comment', kwargs={'resource_key': self.resource_key})

    def save(self, *args, **kwargs):
        self.resource_key = get_resource_key(Comment)
        super(Comment, self).save(*args, **kwargs)

class Reply(models.Model):
    replied_comment = models.ForeignKey("Comment", related_name='replies', null=True, on_delete=models.SET_NULL)
    user_that_replied = models.ForeignKey("User", related_name='replies', null=True, on_delete=models.SET_NULL)
    reply = models.TextField()
    resource_key = models.CharField(max_length=50, unique=True)
    archived = models.BooleanField(default=False)
    date_replied = models.DateTimeField(auto_now_add=True)
    objects = ArchivedManager()

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('view_reply', kwargs={'resource_key': self.resource_key})

    def save(self, *args, **kwargs):
        self.resource_key = get_resource_key(Reply)
        super(Reply, self).save(*args, **kwargs)

class Rating(models.Model):
    rated_post = models.ForeignKey("Post", related_name='ratings',null=True, on_delete=models.SET_NULL)
    user_that_rated = models.ForeignKey("User", related_name='ratings', null=True, on_delete=models.SET_NULL)
    rating = models.BooleanField(default=False)
    resource_key = models.CharField(max_length=50, unique=True)
    archived = models.BooleanField(default=False)
    date_rated = models.DateTimeField(auto_now_add=True)
    objects = ArchivedManager()

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('view_rating', kwargs={'resource_key': self.resource_key})

    def save(self, *args, **kwargs):
        self.resource_key = get_resource_key(Rating)
        super(Rating, self).save(*args, **kwargs)

class Bookmark(models.Model):
    user_that_bookmarked = models.ForeignKey("User", related_name='bookmarks', null=True, on_delete=models.SET_NULL)
    bookmarked_post = models.ForeignKey("Post", related_name='bookmarks', null=True, on_delete=models.SET_NULL)
    resource_key = models.CharField(max_length=50, unique=True)
    archived = models.BooleanField(default=False)
    date_bookmarked = models.DateTimeField(auto_now_add=True)
    objects = ArchivedManager()

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('view_bookmark', kwargs={'resource_key': self.resource_key})

    def save(self, *args, **kwargs):
        self.resource_key = get_resource_key(Bookmark)
        super(Bookmark, self).save(*args, **kwargs)