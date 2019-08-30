import json
from django.conf import settings
from oauth2_provider.models import AccessToken
from django.forms.models import model_to_dict
from django.utils.deprecation import MiddlewareMixin
from posts.helpers import get_avatar_url


class GetUserMiddleware(MiddlewareMixin):

    def __init__(self, *args, **kwargs):
            """Constructor method."""
            super().__init__(*args, **kwargs)

    def process_response(self, request, response):
        if response.status_code == 200:
            relative_path = request.path
            if relative_path in ['/api/v1/auth/bitbucket', '/api/v1/auth/github', '/api/v1/auth/gitlab', '/api/v1/auth/oauth2/token']:
                try:
                    access_token = AccessToken.objects.get(token=response.data['access_token'])
                    current_user = model_to_dict(access_token.user, fields=['first_name', 'last_name', 'username', 'email'])
                    if 'https' in access_token.user.profile.avatar.url:
                        current_user.update({'user_avatar': get_avatar_url('https://', access_token.user.profile.avatar.url)})
                        response.data.update({'user': current_user})
                        response.content = json.dumps(response.data)
                    elif 'http' in access_token.user.profile.avatar.url:
                        current_user.update({'user_avatar': get_avatar_url('http://', access_token.user.profile.avatar.url)})
                        response.data.update({'user': current_user})
                        response.content = json.dumps(response.data)
                    else:
                        current_user.update({'user_avatar': settings.DOMAIN_URL + access_token.user.profile.avatar.url})
                        response.data.update({'user': current_user})
                        response.content = json.dumps(response.data)
                except AccessToken.DoesNotExist:
                    return response
        return response