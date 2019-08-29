import os
import random
import re
import requests
import string
import secrets
import urllib
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from oauth2_provider.models import Application
from django.http import Http404
from django.http.request import QueryDict
from .models import (
    Post, Comment, Rating, Reply, Bookmark,
)

User = get_user_model()

gtt_app = Application.objects.get(name='Geeks Talk Thursday')

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

def get_avatar_url(scheme, quoted_url):
    m = re.match(r'^\/media\/https?%3A\/(.*)', quoted_url)
    matched_url = m.groups()[0]
    return scheme + urllib.parse.unquote(matched_url)

def get_bitbucket_access_token(code, redirect_uri):
    client_id = settings.SOCIAL_AUTH_BITBUCKET_OAUTH2_KEY
    client_secret = settings.SOCIAL_AUTH_BITBUCKET_OAUTH2_SECRET
    data = {
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri,
        }
    headers = {'Accept': 'application/json'}
    response =  requests.post('https://bitbucket.org/site/oauth2/access_token', data=data, auth=(client_id, client_secret), headers=headers)
    bitbucket_access_token = response.json()
    return QueryDict('grant_type=convert_token&client_id=' + gtt_app.client_id + '&client_secret=' + gtt_app.client_secret + '&backend=bitbucket-oauth2&token=' + bitbucket_access_token['access_token'])
    #print(convert_token_data)
    #print(settings.DOMAIN_URL + '/' + settings.API + 'oauth2/convert-token')
    #convert_response =  requests.post(settings.DOMAIN_URL + '/' + settings.API + 'oauth2/convert-token', data=convert_token_data)
    #print(convert_response)

def get_github_access_token(code):
    client_id = settings.SOCIAL_AUTH_GITHUB_KEY
    client_secret = settings.SOCIAL_AUTH_GITHUB_SECRET
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': code,
        }
    headers = {'Accept': 'application/json'}
    response =  requests.post('https://github.com/login/oauth/access_token', data=data, headers=headers)
    github_access_token = response.json()
    return QueryDict('grant_type=convert_token&client_id=' + gtt_app.client_id + '&client_secret=' + gtt_app.client_secret + '&backend=github&token=' + github_access_token['access_token'])
    #convert_response =  requests.post(settings.DOMAIN_URL + '/' + settings.API + 'oauth2/convert-token', data=convert_token_data)
    #return convert_response.json()

def get_gitlab_access_token(code):
    client_id=settings.SOCIAL_AUTH_GITLAB_KEY
    client_secret=settings.SOCIAL_AUTH_GITLAB_SECRET
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': code,
        'grant_type': 'authorization_code',
        }
    headers = {'Accept': 'application/json'}
    response =  requests.post('http://gitlab.com/oauth/token', data=data, headers=headers)
    return response.json()