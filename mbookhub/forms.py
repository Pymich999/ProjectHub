from django import forms
from .models import Profile, Post
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User 


class SignupForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required')
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'profile_pic']


class BookSearchForm(forms.Form):
    query = forms.CharField(max_length=255, label='Search For A Book')

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['book', 'caption', 'likes']