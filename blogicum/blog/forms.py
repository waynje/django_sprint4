from django import forms

from django.contrib.auth import get_user_model

from .models import Comments, Post

User = get_user_model()


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email'
        )


class CommentsForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ('text',)


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('author', 'created_at')
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'datetime-local'})
        }
