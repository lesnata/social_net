from datetime import datetime

from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import pre_save
from django.utils.text import slugify
from django.dispatch import receiver

# Create your models here.


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, null=False, blank=False)
    post = models.TextField(null=False, blank=False)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-date_published']


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    liked = models.BooleanField(default=False)

    def __str__(self):
        return self.liked

    def like_unlike(self):
        self.liked = not self.liked
        self.date = datetime.now()
        return self.liked


def pre_save_post_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.author.username + "-" + instance.title)


pre_save.connect(pre_save_post_receiver, sender=Post)

