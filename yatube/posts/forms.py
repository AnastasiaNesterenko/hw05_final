"""
Приложение posts отвечает за работу сайта.
В forms.py описаны формы для заполнения
для создания поста или комментария.
"""
from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    """Форма для создания/редактирования поста."""
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        help_texts = {
            'group': 'Группа, к которой будет относиться пост'
        }


class CommentForm(forms.ModelForm):
    """Форма для создания комментария."""
    class Meta:
        model = Comment
        fields = ('text',)
