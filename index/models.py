from django.db import models

class MarkdownPage(models.Model):
    name = models.CharField(max_length = 256, primary_key=True, unique=True)
    title = models.CharField(max_length = 256)
    body = models.TextField()

    def __str__(self):
        return str(self.title)
