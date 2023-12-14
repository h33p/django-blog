from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import *
from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from pygments import highlight
from pygments.lexers import get_lexer_by_name, _iter_lexerclasses
from pygments.formatters import NullFormatter
from .models import *
from django.core.paginator import Paginator
import mistune as md
import util

class CustomizedRenderer(md.HTMLRenderer):
    def block_code(self, code, info=None):
        if info:
            if info == 'asciirend':
                code = util.ascii_render(code)[1]
        return super(CustomizedRenderer, self).block_code(code, info)

    def link(self, text, url, title = None):
        if url.startswith("#") and not url[1:] in self.lt:
            self.lt[text] = url[1:]
        return super(CustomizedRenderer, self).link(text, url, title)

class RssFeed(Feed):
    title = "blaz.is"
    description = "h33p's blog on random topics"
    link = "/blog/"
    model = BlogPost
    template_name = 'blog/post.html'
    context_object_name = 'post'
    feed_type = Rss201rev2Feed

    def items(self):
        return BlogPost.objects.order_by('-pub_date')[:10]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        renderer = CustomizedRenderer()
        md_rend = md.create_markdown(renderer=renderer, plugins=['strikethrough'])
        return md_rend(item.md_data)

    def item_link(self, item):
        return f'/blog/post/{item.slug}'

    def item_pubdate(self, item):
        return item.pub_date

    def item_updateddate(self, item):
        return item.last_updated

    def item_author_name(self, item):
        return item.posted_by

    def item_categories(self, item):
        return [f.name for f in item.categories.iterator()]

class AtomFeed(RssFeed):
    feed_type = Atom1Feed
    subtitle = RssFeed.description
