from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.urls import reverse
from django.views.generic import (
    DetailView, CreateView, ListView, UpdateView, DeleteView
)

from blog.models import Post, Category, Comment, User
from blog.forms import ProfileForm, CommentForm, PostForm

POSTS_PER_PAGE = 10


class PostListView(ListView):
    template_name = 'blog/index.html'
    model = Post
    paginate_by = POSTS_PER_PAGE

    def get_queryset(self):
        return (self.model.objects.select_related(
                'location', 'author', 'category').filter(
                is_published=True, category__is_published=True,
                pub_date__lte=timezone.now()))


class PostDetailView(DetailView):
    template_name = 'blog/detail.html'
    model = Post

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if (
            not self.object.is_published
            and (self.object.author != request.user)
        ):
            raise Http404('This page was not found')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comment_set.select_related('author')
        )
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'slug': self.request.user})


class PostMixin(LoginRequiredMixin):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if instance.author != request.user:
            return redirect('blog:post_detail', pk=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class PostUpdateView(PostMixin, UpdateView):

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'pk': self.kwargs['post_id']})


class PostDeleteView(PostMixin, DeleteView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'slug': self.request.user})


class CategoryPosts(ListView):
    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'page_obj'
    paginate_by = POSTS_PER_PAGE

    def get_queryset(self):
        current_time = timezone.now()
        category_slug = self.kwargs.get('slug')
        category = get_object_or_404(Category,
                                     is_published=True,
                                     slug=category_slug)
        return category.post_set.filter(
            pub_date__lte=current_time,
            is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = get_object_or_404(
            Category,
            is_published=True,
            slug=self.kwargs.get('slug'))
        context['category'] = category
        return context


class ProfileLoginView(LoginView):
    def get_success_url(self):
        url = reverse(
            'blog:profile',
            args=(self.request.user.get_username(),)
        )
        return url


class ProfileListView(ListView):
    model = User
    template_name = 'blog/profile.html'
    paginate_by = POSTS_PER_PAGE

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['slug'])
        posts = user.post_set.all()

        self.extra_context = {
            'profile': user,
        }
        return posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_number = self.request.GET.get('page')
        context['profile'] = get_object_or_404(User,
                                               username=self.kwargs['slug'])
        context['page_number'] = page_number
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


class CommentMixin(LoginRequiredMixin):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        self.p_id = kwargs['post_id']
        comment = get_object_or_404(Comment, pk=self.kwargs['comment_id'])
        if comment.author != request.user:
            return redirect('blog:post_detail', pk=self.p_id)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm(instance=self.object)
        return context

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'pk': self.kwargs['post_id']})


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = get_object_or_404(Post, pk=kwargs['post_id'])
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['post_id']})


class CommentUpdateView(CommentMixin, UpdateView):
    form_class = CommentForm


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Comment, pk=self.kwargs['comment_id'])
        if instance.author != request.user:
            return redirect('blog:post_detail', pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'pk': self.kwargs['post_id']})
