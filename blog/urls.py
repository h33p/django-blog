from django.urls import path

from . import views
from . import feeds

app_name = 'blog'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('new_post', views.NewPostView.as_view(), name = 'new_post'),
    path('feed/rss', feeds.RssFeed(), name = 'rss_feed'),
    path('feed/atom', feeds.AtomFeed(), name = 'atom_feed'),
    path('post/id/<int:pk>/', views.BlogPostView.as_view(), name = 'blog_post_id'),
    path('post/<str:slug>/', views.BlogPostView.as_view(), name = 'blog_post'),
    path('cat/<str:slug>/', views.CategoryView.as_view(), name = 'category_name'),
]
