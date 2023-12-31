from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import (
    DetailView, CreateView, ListView, UpdateView, DeleteView
)

from .forms import ProfileForm, CommentForm, PostForm
from .models import Post, Comment, User, Category
from .utils import posts_filtered

POSTS_PER_PAGE = 10


class PostListView(ListView):
    template_name = 'blog/index.html'
    paginate_by = POSTS_PER_PAGE

    def get_queryset(self):
        return posts_filtered(Post.objects.all())


class PostDetailView(DetailView):
    template_name = 'blog/detail.html'
    model = Post
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if (
            not self.object.is_published
            and (self.object.author != request.user)
        ):
            raise Http404('This page was not found')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return dict(**super().get_context_data(**kwargs),
                    form=CommentForm(),
                    comments=self.object.comments.all())


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile',
                       args=[self.request.user.get_username()])


class PostMixin(LoginRequiredMixin):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if instance.author != request.user:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class PostUpdateView(PostMixin, UpdateView):

    def get_success_url(self):
        return reverse('blog:post_detail',
                       args=[self.kwargs['post_id']])


class PostDeleteView(PostMixin, DeleteView):

    def get_success_url(self):
        return reverse('blog:profile',
                       args=[self.request.user.get_username()])


class CategoryPosts(ListView):
    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'page_obj'
    paginate_by = POSTS_PER_PAGE

    def get_object(self):
        return get_object_or_404(
            Category,
            slug=self.kwargs['slug'],
            is_published=True)

    def get_queryset(self):
        return posts_filtered(self.get_object().posts)

    def get_context_data(self, **kwargs):
        return dict(
            **super().get_context_data(**kwargs),
            category=self.get_object()
        )


class ProfileLoginView(LoginView):
    def get_success_url(self):
        return reverse(
            'blog:profile',
            args=(self.request.user.get_username(),)
        )


class ProfileListView(ListView):
    model = User
    template_name = 'blog/profile.html'
    paginate_by = POSTS_PER_PAGE

    def get_object(self):
        return get_object_or_404(User,
                                 username=self.kwargs['slug'])

    def get_queryset(self):
        return self.get_object().posts.all()

    def get_context_data(self, **kwargs):
        return dict(
            **super().get_context_data(**kwargs),
            profile=self.get_object(),
        )


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'blog/user.html'
    slug_field = 'username'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse('blog:profile', args=[self.request.user.get_username()])


class CommentMixin(LoginRequiredMixin):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=self.kwargs['comment_id'])
        if comment.author != request.user:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       args=[self.kwargs['post_id']])


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            args=[self.kwargs['post_id']])


class CommentUpdateView(CommentMixin, UpdateView):
    form_class = CommentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class CommentDeleteView(CommentMixin, DeleteView):
    template_name = 'blog/comment.html'
