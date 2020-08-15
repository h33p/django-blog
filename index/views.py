from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from .models import *

class MarkdownPageView(generic.DetailView):
    model = MarkdownPage
    template_name = 'index/markdown_page.html'
    context_object_name = 'page'
