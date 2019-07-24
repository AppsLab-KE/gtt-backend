from django.db import models

class Tag(models.Model):
    tag_name = models.CharField(max_length=50)
    resource_key = models.CharField(max_length=50, unique=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('view_tag', kwargs={'pk': self.pk})

class Post(models.Model):
    post_heading = models.CharField(max_length=100)
    post_body = models.TextField()
    post_author = models.ForeignKey("User", nullable=True, on_delete=models.SET_NULL)
    slug = models.SlugField()
    tags = models.ManyToManyField("Tag", related_name="tags")
    date_published = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('view_post', kwargs={'slug': self.slug})

class Comment(models.Model):
    commented_post = models.ForeignKey("Post", nullable=True, on_delete=models.SET_NULL)
    user_that_commented = models.ForeignKey("User", nullable=True, on_delete=models.SET_NULL)
    comment = models.TextField()
    resource_key = models.CharField(max_length=50, unique=True)
    date_commented = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('view_comment', kwargs={'pk': self.pk})

class Reply(models.Model):
    replied_comment = models.ForeignKey("Comment", nullable=True, on_delete=models.SET_NULL)
    user_that_replied = models.ForeignKey("User", nullable=True, on_delete=models.SET_NULL)
    reply = models.TextField()
    resource_key = models.CharField(max_length=50, unique=True)
    date_replied = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('view_reply', kwargs={'pk': self.pk})

class Rating(models.Model):
    rated_post = models.ForeignKey("Post", nullable=True, on_delete=models.SET_NULL)
    user_that_rated = models.ForeignKey("User", nullable=True, on_delete=models.SET_NULL)
    rating = models.BooleanField(default=False)
    resource_key = models.CharField(max_length=50, unique=True)
    date_rated = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('view_rating', kwargs={'pk': self.pk})

class Bookmark(models.Model):
    user_that_bookmarked = models.ForeignKey("User", nullable=True, on_delete=models.SET_NULL)
    bookmarked_post = models.ForeignKey("Post", nullable=True, on_delete=models.SET_NULL)
    resource_key = models.CharField(max_length=50, unique=True)
    date_bookmarked = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('view_bookmark', kwargs={'pk': self.pk})

class Archive(models.Model):
    user_that_archived = models.ForeignKey("User", nullable=True, on_delete=models.SET_NULL)
    archived_post = models.ForeignKey("Post", nullable=True, on_delete=models.SET_NULL)
    resource_key = models.CharField(max_length=50, unique=True)
    date_archived = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('view_archive', kwargs={'pk': self.pk})