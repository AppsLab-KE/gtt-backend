from django.db import models

class Post(models.Model):
    article_heading = models.CharField(max_length=100)
    article_body = models.TextField()
    article_author = models.ForeignKey("User", nullable=True, on_delete=models.SET_NULL)
    article_category = models.CharField(max_length=50)
    date_published = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('', kwargs={'pk': self.pk})
