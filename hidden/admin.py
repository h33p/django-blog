from django.contrib import admin

from .models import MarkdownPage, StaticData

admin.site.register(MarkdownPage)
admin.site.register(StaticData)
