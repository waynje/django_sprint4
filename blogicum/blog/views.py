from typing import Any
from django import http
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http.response import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.urls import reverse
from django.views.generic import DetailView, CreateView

from blog.models import Post, Category, Comments
from blog.forms import ProfileForm, CommentsForm

User = get_user_model()


def posts_filtered(posts):
    return posts.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    )


def post_detail(request, post_id):
    return render(request, 'blog/detail.html',
                  {'post': get_object_or_404(
                   posts_filtered(Post.objects.all()),
                   id=post_id)
                   })


def index(request):
    posts = Post.objects.order_by('id')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/index.html', {'page_obj': page_obj})


def category_posts(request, slug):
    category = get_object_or_404(Category,
                                 slug=slug,
                                 is_published=True)
    posts = posts_filtered(Post.objects.all()).filter(category=category)
    return render(request, 'blog/category.html',
                  {'category': category,
                   'post_list': posts
                   })


class ProfileDetailView(DetailView):
    model = User
    form = ProfileForm
    slug_field = 'username'
    template_name = 'blog/profile.html'
    context_object_name = 'profile'


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentsForm(request.POST)
    if form.is_valid():
        comment = form.save()
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('blog:post_detail', id=post_id)
    return render(request, 'blog/detail.html', {'post': post, 'form': form})

class CommentCreateView(LoginRequiredMixin, CreateView):
    post = None
    model = Comments
    form_class = CommentsForm

    def dispatch(self, request, *args: Any, **kwargs: Any) -> HttpResponse:
        self.post = get_object_or_404(Post,pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)
    

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post
        return super().form_valid(form)
    

    ##def get_success_url(self) -> str:
        ##return reverse('blog:post_detail', kwargs = {'pk' = self.post.pk})
     

