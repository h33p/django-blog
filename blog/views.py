from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from .models import *
from django.core.paginator import Paginator

POSTS_PER_PAGE = 20

class IndexView(generic.TemplateView):
    template_name = 'blog/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = BlogPost.objects.order_by('-pub_date')

        paginator = Paginator(posts, POSTS_PER_PAGE)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['paginator'] = paginator
        context['page_obj'] = page_obj

        context['categories'] = Category.objects.order_by('name')
        return context

class BlogPostView(generic.DetailView):
    model = BlogPost
    template_name = 'blog/post.html'
    context_object_name = 'post'

class CategoryView(generic.DetailView):
    model = Category
    template_name = 'blog/index.html'
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        object = self.get_object()
        posts = BlogPost.objects.filter(categories__id=object.id).order_by('-pub_date')

        paginator = Paginator(posts, POSTS_PER_PAGE)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['paginator'] = paginator
        context['page_obj'] = page_obj

        context['categories'] = Category.objects.order_by('name')
        return context

class NewPostView(generic.TemplateView):
    template_name = 'blog/new_post.html'
