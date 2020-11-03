from django import forms
from cloudinary.forms import CloudinaryFileField
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()

class AvatarForm(forms.ModelForm):
    avatar = CloudinaryFileField(
        options = {
            'crop': 'thumb',
            'width': 200,
            'height': 200,
            'folder': 'profile_avatars'
       }
    )
 
    class Meta:
        model = Profile
        fields = (
            'avatar',
        )

class UserForm(forms.ModelForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'bio',
        )