from django import forms
from django.contrib.auth.models import User
from .models import Post, Comment


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('title', 'text', 'pub_date', 'category', 'location', 'image')
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'})
        }


class UpdatePostModelForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('title', 'text', 'pub_date', 'category', 'location', 'image')
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'datetime'})
        }


class UpdateProfileModelForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email',)
        widgets = {'username': forms.TextInput(
            attrs={'class': 'form-control form-input form__input'}),
            'first_name': forms.TextInput(
                attrs={'class': 'form-control form-input form__input'}),
            'last_name': forms.TextInput(
                attrs={'class': 'form-control form-input form__input'})
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)


class UpdateCommentModelForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
