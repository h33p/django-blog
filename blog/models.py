from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)

    def __str__(self):
        return self.name

class BlogPost(models.Model):
    title = models.CharField(max_length = 256)
    slug = models.SlugField()
    pub_date = models.DateTimeField('date published')
    last_updated = models.DateTimeField('last updated')
    md_data = models.TextField()
    categories = models.ManyToManyField(Category, blank=True)
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
