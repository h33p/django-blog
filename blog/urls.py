from django.urls import path

from . import views

app_name = 'blog'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('post/id/<int:pk>/', views.BlogPostView.as_view(), name = 'blog_post'),
    path('post/<str:slug>/', views.BlogPostView.as_view(), name = 'blog_post'),
    path('cat/<str:slug>/', views.CategoryView.as_view(), name = 'category_name'),
]
