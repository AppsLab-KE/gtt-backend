from django import forms
from cloudinary.forms import CloudinaryFileField
from .models import (
    Category, Post, Rating, Comment, Reply, Bookmark,
)

class PostForm(forms.ModelForm):
    post_heading_image = CloudinaryFileField(
        options = {
            'folder': 'post_photos'
       }
    )
    class Meta:
        model = Post
        fields = (
            'post_heading',
            'post_heading_image',
            'post_body',
            'read_duration',
        )

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = (
            'category_name',
        )

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = (
           'rating',
        )

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = (
             'comment',
        )

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = (
            'reply',
        )