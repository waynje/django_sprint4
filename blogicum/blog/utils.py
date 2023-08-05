from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Post, User, Comment, Category


def get_posts_data():
    return Post.objects.filter(is_published=True,
                               category__is_published=True,
                               pub_date__lte=timezone.now())


def get_post_by_id(self):
    return get_object_or_404(Post, pk=self.kwargs['post_id'])


def get_user_by_slug(self):
    return get_object_or_404(User,
                             username=self.kwargs['slug'])


def get_comment_by_comment_id(self):
    return get_object_or_404(Comment, pk=self.kwargs['comment_id'])


def get_category_by_slug(self):
    return get_object_or_404(Category,
                             is_published=True,
                             slug=self.kwargs.get('slug'))
