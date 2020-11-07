import hashlib
import cloudinary
from rest_framework.response import Response

def save_avatar(strategy, details, user=None, *args, **kwargs):
    """Get user avatar from social provider."""
    is_new = kwargs.get('is_new')
    if is_new:
        if user:
            backend_name = kwargs['backend'].__class__.__name__.lower()
            response = kwargs.get('response', {})
            social_thumb = None
            if 'github' in backend_name and response.get('avatar_url'):
                social_thumb = response['avatar_url']
            elif 'bitbucket' in backend_name and response.get('links', {}).get('avatar', {}).get('href'):
                social_thumb = response['links']['avatar']['href']
            elif 'google' in backend_name and response.get('picture'):
                social_thumb = response['picture']
            else:
                social_thumb = 'http://www.gravatar.com/avatar/'
                social_thumb += hashlib.md5(user.email.lower().encode('utf8')).hexdigest()
                social_thumb += '?size=100'
            if social_thumb and user.profile.avatar != social_thumb:
                user.profile.avatar = cloudinary.uploader.upload_resource(social_thumb)
                strategy.storage.user.changed(user)
    else:
        if user:
            if not user.profile.avatar.url:
                backend_name = kwargs['backend'].__class__.__name__.lower()
                response = kwargs.get('response', {})
                social_thumb = None
                if 'github' in backend_name and response.get('avatar_url'):
                    social_thumb = response['avatar_url']
                elif 'bitbucket' in backend_name and response.get('links', {}).get('avatar', {}).get('href'):
                    social_thumb = response['links']['avatar']['href']
                elif 'google' in backend_name and response.get('picture'):
                    social_thumb = response['picture']
                else:
                    social_thumb = 'http://www.gravatar.com/avatar/'
                    social_thumb += hashlib.md5(user.email.lower().encode('utf8')).hexdigest()
                    social_thumb += '?size=100'
                if social_thumb and user.profile.avatar != social_thumb:
                    user.profile.avatar = cloudinary.uploader.upload_resource(social_thumb)
                    strategy.storage.user.changed(user)



def check_for_email(backend, uid, user=None, *args, **kwargs):
    if not kwargs['details'].get('email'):
        return Response({'error': "Email wasn't provided by oauth provider"}, status=400)