from .models import Post ,Comment, Category, Profile
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'body', 'image','category']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Give your thoughts a name...'}),
            'body': forms.Textarea(attrs={'placeholder': 'Begin the conversation...'}),
            'category': forms.Select(attrs={'class': 'dropdown'}),
        }

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ['username', 'email']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={'placeholder': 'Write a comment...', 'rows': 3, 'class': 'comment-input'}),
        }

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    clear_image = forms.BooleanField(required=False, label="Remove current profile image")
    class Meta:
        model = Profile
        fields = ['image', 'bio', 'location', 'twitter', 'linkedin', 'website']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }
