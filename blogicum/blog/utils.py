from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import User, Category


def posts_filtered(posts):
    return posts.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    )


def category_filtered(category):
    return get_object_or_404(
        Category,
        is_published=True,
        slug=category.kwargs['slug']
    )


def get_user_by_slug(user):
    return get_object_or_404(User, username=user.kwargs['slug'])
