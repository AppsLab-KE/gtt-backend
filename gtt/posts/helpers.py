import os
import random
import re
import shlex
import requests
import string
import secrets
import urllib
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from oauth2_provider.models import Application
from django.http import Http404
from django.http.request import QueryDict
from django.utils.text import slugify

User = get_user_model()
START = '#'

def get_first_user():
    users = User.objects.all()
    return users[0]

def get_app():
    try:
        gtt_app = Application.objects.get(name='Geeks Talk Thursday')
        return gtt_app
    except Application.DoesNotExist:
        gtt_app = Application.objects.create(
            name = 'Geeks Talk Thursday',
            redirect_uris = settings.FRONTEND_DOMAIN_URL,
            user = get_first_user(),
            client_type = Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type = Application.GRANT_PASSWORD,
        )
        return gtt_app

def get_color_from_letter(word):
    l = word[0].lower()
    if l in ['a', 'n', '1']:
        return '#468990'
    elif l in ['b', 'o', '2']:
        return '#FADB56'
    elif l in ['c', 'p', '3']:
        return '#E14C38'
    elif l in ['d', 'q', '4']:
        return '#3399ff'
    elif l in ['e', 'r', '5']:
        return '#99cc00'
    elif l in ['f', 's', '6']:
        return '#6600ff'
    elif l in ['g', 't', '7']:
        return '#996600'
    elif l in ['h', 'u', '8']:
        return '#666699'
    elif l in ['i', 'v', '9']:
        return '#999966'
    elif l in ['j', 'w', '0']:
        return '#ccffff'
    elif l in ['k', 'x']:
        return '#cc0000'
    elif l in ['l', 'y']:
        return '#00ccff'
    else:
        return '#e6e6e6'

def start_colour(name):
    #random_colour = random.randint(0, 0xffffff) # inclusive range
    #return f'{START}{random_colour:06X}'
    return get_color_from_letter(name)

def contrast_colour(colour):
    rgb = int(colour.lstrip(START), 16)
    complementary_colour = 0xffffff-rgb
    return [
        colour.lstrip(START),
        f'{complementary_colour:06X}'
    ]

def default_photo(name):
    name_list = shlex.split(name)
    concatenated_name = str()
    for n in name_list:
        concatenated_name += "{}+".format(n)
    cn = concatenated_name.strip('+')
    return "https://ui-avatars.com/api/?name={}&background={}&color={}&size=180".format(cn, *contrast_colour(start_colour(name)))

def is_writer(user):
        if user.has_perm('posts.add_post'):
            return  True
        else:
            return False

def remove_html_tags(text):
    """Remove html tags from a string"""
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text).rstrip('...')

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

def get_tag_slug(instance):
    return slugify(instance.tag_name[:249].capitalize())

def get_category_slug(instance):
    return slugify(instance.category_name[:249].capitalize())

def get_slug_key(instance, model, slug=None):
    slug = slugify(instance.post_heading[:249])
    slug_token = str()
    while True:
        slug_token = slug + "-" + get_random_token(20)
        try:
            get_object_or_404(model, slug=slug_token)
            continue
        except Http404:
            break
    return slug_token
    

def get_avatar_url(scheme, quoted_url):
    try:
        m = re.match(r'^\/media\/https?%3A\/(.*)', quoted_url)
        matched_url = m.groups()[0]
        return scheme + urllib.parse.unquote(matched_url)
    except:
        return "https://api.adorable.io/avatars/285/default-avatar@mail.png"

def get_bitbucket_access_token(code, redirect_uri):
    gtt_app = get_app()
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
    gtt_app = get_app()
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

def get_google_access_token(code):
    gtt_app = get_app()
    client_id = settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
    client_secret = settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': code.replace("%2F", "/"),
        'redirect_uri': "{}/oauth/complete/google/".format(gtt_app.redirect_uris),
        'grant_type': 'authorization_code',
        }
    headers = {'Accept': 'application/json'}
    response =  requests.post('https://oauth2.googleapis.com/token', data=data, headers=headers)
    google_access_token = response.json()
    return QueryDict('grant_type=convert_token&client_id=' + gtt_app.client_id + '&client_secret=' + gtt_app.client_secret + '&backend=google-oauth2&token=' + google_access_token['access_token'])

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

def get_password_querydict(username, password):
    gtt_app = get_app()
    return QueryDict('grant_type=password&client_id=' + gtt_app.client_id + '&client_secret=' + gtt_app.client_secret + '&username=' + username + '&password=' + password)

def get_token_querydict(refresh_token):
    gtt_app = get_app()
    return QueryDict('grant_type=refresh_token&client_id=' + gtt_app.client_id + '&client_secret=' + gtt_app.client_secret + '&refresh_token=' + refresh_token)

def get_revoke_token_querydict(token):
    gtt_app = get_app()
    return QueryDict('client_id=' + gtt_app.client_id + '&client_secret=' + gtt_app.client_secret + '&token=' + token)

def user_confirmation_token():
    token = str()
    while True:
        token = get_random_token(60)
        try:
            User.objects.get(confirmation_token=token)
            continue
        except User.DoesNotExist:
            break
    return token

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