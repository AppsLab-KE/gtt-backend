import os
import re
import random
import datetime
import urllib
from django.db import models
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth.models import AbstractUser
from cloudinary.models import CloudinaryField
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

def send_email(subject, recepient, message):
    status = send_mail(
        subject,
        '',
        settings.EMAIL_HOST_USER,
        recepient,
        fail_silently=False,
        html_message=message,
        )
    return bool(status)

def prepare_message(template, **kwargs):
    message = render_to_string(template, kwargs)
    return message

def get_avatar_url(scheme, quoted_url):
    m = re.match(r'^\/media\/https?%3A\/(.*)', quoted_url)
    matched_url = m.groups()[0]
    return scheme + urllib.parse.unquote(matched_url)

def get_user_avatar(obj):
    if 'https' in obj.profile.avatar.url:
        return get_avatar_url('https://', obj.profile.avatar.url)
    elif 'http' in obj.profile.avatar.url:
        return get_avatar_url('http://', obj.profile.avatar.url)
    else:
        return settings.DOMAIN_URL + obj.profile.avatar.url

def unique_photo_path(instance, filename):
    basefilename, file_extension= os.path.splitext(filename)
    chars= 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'
    randomstr= ''.join((random.choice(chars)) for x in range(10))
    return 'profile_avatars/{id}/{basename}{randomstring}{ext}'.format(id=instance.user.id, basename=basefilename, randomstring=randomstr, ext=file_extension)

class User(AbstractUser):
    confirmation_token = models.CharField(max_length=255, null=True)
    bio = models.TextField(blank=True, default='')

    def __str__(self):
        return self.email

class Profile(models.Model):
    user = models.OneToOneField("User", on_delete=models.CASCADE)
    avatar = CloudinaryField('avatar')

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('view_user', kwargs={'pk': self.user})

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

@receiver(m2m_changed, sender=User.groups.through)
def user_group_changed(sender, **kwargs):
    instance = kwargs.pop('instance', None)
    action = kwargs.pop('action', None)    
    if action == "post_add":
        subject = "You've received a notification"
        recepient = [instance.email]
        message = prepare_message(
                template="granted_writership.html",
                username=instance.username,
                user_id=instance.id,
                user_avatar= get_user_avatar(instance),
                domain_url=settings.DOMAIN_URL)
        success = send_email(subject, recepient, message)
        if success:
            instance.save()          
    elif action == "post_remove":
        subject = "You've received a notification"
        recepient = [instance.email]
        message = prepare_message(
                template="revoke_writership.html",
                username=instance.username,
                user_id=instance.id,
                user_avatar= get_user_avatar(instance),
                domain_url=settings.DOMAIN_URL)
        success = send_email(subject, recepient, message)
        if success:
            instance.save()
