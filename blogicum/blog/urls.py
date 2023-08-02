from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('category/<slug:slug>/', views.category_posts,
         name='category_posts'),
    path('profile/<slug:slug>', views.ProfileDetailView.as_view(),
         name='profile'),
    path('posts/<int:post_id>/', views.add_comment, name='add_comment')
]
