from django import forms
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()

class AvatarForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = (
            'avatar',
        )

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
        )