from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    DetailView, CreateView, ListView, UpdateView, DeleteView
)

from blog.models import Post, Category, Comment
from blog.forms import ProfileForm, CommentForm, PostForm

User = get_user_model()
POSTS_PER_PAGE = 10


class PostListView(ListView):
    template_name = 'blog/index.html'
    model = Post
    paginate_by = POSTS_PER_PAGE

    def get_queryset(self):
        return(self.model.objects.select_related('location','author','category')
               .filter(is_published=True,category__is_published=True,
                       pub_date__lte=timezone.now()).order_by('-pub_date'))
    

class PostDetailView(DetailView):
    template_name = 'blog/detail.html'
    model = Post

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
        return reverse_lazy('blog:profile',
                            kwargs={'slug': self.request.user})


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'pk': self.kwargs['pk']})


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    form = PostForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'slug': self.request.user})


class CategoryPosts(ListView):
    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'page_obj'
    paginate_by = POSTS_PER_PAGE

    def get_queryset(self):
        current_time = timezone.now()
        category_slug = self.kwargs.get('slug')
        category = get_object_or_404(
                                     Category,
                                     is_published=True,
                                     slug=category_slug)
        return category.post_set.filter(pub_date__lte=current_time,
                                        is_published=True).order_by(
                                        '-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs.get('slug')
        category = get_object_or_404(
            Category,
            is_published=True,
            slug=category_slug)
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
    context_object_name = 'profile'
    paginate_by = POSTS_PER_PAGE

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['slug'])
        posts = user.post_set.all().order_by('-pub_date')

        self.extra_context = {
            'profile': user,
            'user': user,
        }
        return posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_list = context['profile']
        page_number = self.request.GET.get('page')
        context['profile'] = profile_list
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm(instance=self.object)
        return context

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'pk': self.kwargs['pk']})


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    form = CommentForm
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = get_object_or_404(Post, pk=kwargs['pk'])
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['pk']})


class CommentUpdateView(CommentMixin, UpdateView):
    form_class = CommentForm


class CommentDeleteView(CommentMixin, DeleteView):
    ...
