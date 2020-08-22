from django.urls import path

from . import views
from .models import MarkdownPage
from django.conf.urls import url

app_name = 'hidden'
urlpatterns = [
    path('<str:slug>.html', views.MarkdownPageView.as_view(), name = 'page_html'),
    path('<str:slug>/', views.MarkdownPageView.as_view(), name = 'page'),
]
