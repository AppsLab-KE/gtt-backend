import os
import random
import string
import secrets
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.http import Http404

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