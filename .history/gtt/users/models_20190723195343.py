import os
import random
import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

def unique_photo_path(instance, filename):
    basefilename, file_extension= os.path.splitext(filename)
    chars= 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'
    randomstr= ''.join((random.choice(chars)) for x in range(10))
    return 'profile_photos/{id}/{basename}{randomstring}{ext}'.format(id=instance.user.id, basename=basefilename, randomstring=randomstr, ext=file_extension)

class User(AbstractUser):
    def __str__(self):
        return self.email

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to=unique_photo_path, default='profile_avatars/user_avatar.png')

    def def get_absolute_url(self):
        from django.urls import reverse
        return reverse('view_user', kwargs={'pk': self.user.pk})

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
