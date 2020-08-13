from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from .models import *

class IndexView(generic.ListView):
    template_name = 'blog/index.html'
    context_object_name = 'latest_blog_list'

    def get_queryset(self):
        return BlogPost.objects.order_by('-pub_date')[:20]

class BlogPostView(generic.DetailView):
    model = BlogPost
    template_name = 'blog/post.html'
    context_object_name = 'post'

