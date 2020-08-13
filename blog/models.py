from django.db import models

class BlogPost(models.Model):
    title = models.CharField(max_length = 256)
    pub_date = models.DateTimeField('date published')
    md_data = models.TextField()

    def __str__(self):
        return self.title
