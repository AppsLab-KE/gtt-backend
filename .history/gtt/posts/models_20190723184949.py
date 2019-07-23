from django.db import models

class Post(models.Model):
    article_heading = models.CharField(max_length=100)
    article_body = models.TextField()
    article_author = models.ForeignKey("User", nullable=True, on_delete=models.SET_NULL)
    article_category = models.CharField(max_length=50)
    date_published = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('view_post', kwargs={'pk': self.pk})

class Rating(models.Model):
    rated_article
    user_that_rated
    rating 
    date_rated

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('view_rating', kwargs={'pk': self.pk})
