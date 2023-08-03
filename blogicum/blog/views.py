from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    DetailView, CreateView, ListView, UpdateView, DeleteView
)

from blog.models import Post, Category, Comments
from blog.forms import ProfileForm, CommentsForm, PostForm
from .utils import get_post_data

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


class PostListView(ListView):
    template_name = 'blog/index.html'
    model = Post
    ordering = '-pub_date'
    paginate_by = 10


class PostDetailView(DetailView):
    template_name = 'blog/detail.html'
    model = Post
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentsForm()
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.kwargs['post_id']})


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    form_class = PostForm
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.kwargs['post_id']})


def category_posts(request, slug):
    category = get_object_or_404(Category,
                                 slug=slug,
                                 is_published=True)
    posts = Post.objects.order_by('id')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/category.html',
                  {'category': category,
                   'page_obj': page_obj
                   })


class ProfileDetailView(DetailView):
    model = User
    form = ProfileForm
    slug_field = 'username'
    template_name = 'blog/profile.html'
    context_object_name = 'profile'
    paginate_by = 10
    ordering = '-pub_date'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        context['page_obj'] = Post.objects.filter(author=user).order_by
        ('-pub_date')
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'blog/user.html'
    slug_field = 'username'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse('blog:profile', args=[self.request.user])


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comments
    form_class = CommentsForm
    template_name = 'blog/comment.html'
    post_obj = None


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = get_object_or_404(Post, pk=kwargs['pk'])
        self.post_obj = get_post_data(**kwargs)
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.form
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['pk']}
        )


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comments
    form_class = CommentsForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, kwargs):
        comment = get_object_or_404(Comments,
                                    pk=kwargs['comment_id'])
        if comment.author != request.user:
            return redirect('blog:post_detail', id=kwargs['post_id'])
        return super().dispatch(request, kwargs)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'id': self.kwargs['post_id']})


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comments
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, kwargs):
        comment = get_object_or_404(Comments,
                                    pk=kwargs['comment_id'])
        if comment.author != request.user:
            return redirect('blog:post_detail', id=kwargs['post_id'])
        return super().dispatch(request, kwargs)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'id': self.kwargs['post_id']})
