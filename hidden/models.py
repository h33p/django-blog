from django.db import models
from django.dispatch import receiver
import os
from djblog.settings import MEDIA_ROOT

class MarkdownPage(models.Model):
    slug = models.SlugField(max_length = 256, primary_key=True, unique=True)
    title = models.CharField(max_length = 256)
    body = models.TextField()

    def __str__(self):
        return str(self.title)


class StaticData(models.Model):
    file = models.FileField()

    def __str__(self):
        return str(os.path.relpath(self.file.path, start = MEDIA_ROOT))

@receiver(models.signals.post_delete, sender=StaticData)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.file:
        instance.file.delete(save=False)

@receiver(models.signals.pre_save, sender=StaticData)
def auto_delete_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = StaticData.objects.get(pk=instance.pk).file
    except StaticData.DoesNotExist:
        return False

    new_file = instance.file
    if not old_file == new_file:
        old_file.delete(save=False)
