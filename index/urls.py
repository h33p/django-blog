from django.urls import path

from . import views
from .models import MarkdownPage
from django.conf.urls import url

app_name = 'index'
urlpatterns = [
    path('', views.MarkdownPageView.as_view(), kwargs = {'pk': 'index'}, name = 'page_index'),
    path('<str:pk>.html', views.MarkdownPageView.as_view(), name = 'page_html'),
    path('<str:pk>/', views.MarkdownPageView.as_view(), name = 'page'),
]
