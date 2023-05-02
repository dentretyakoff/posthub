from django import forms
from django.core.exceptions import ValidationError

from .models import Comment, Post


# Форма создания поста
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')

    def clean_text(self):
        data = self.cleaned_data['text']

        if len(data) < 5:
            raise ValidationError('Слишком короткий пост')
        return data


# Форма создания комментария
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
