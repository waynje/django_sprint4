from django.utils import timezone


def posts_filtered(posts):
    return posts.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    )
