from django import forms
from .models import (
    Post, Rating, Comment, Reply, Bookmark,
)

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            'post_heading',
            'post_heading_image',
            'post_body',
            'read_duration'
        )

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = (
           
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
        fields = ()

class BookmarkForm(forms.ModelForm):
    class Meta:
        model = Bookmark
        fields = ()