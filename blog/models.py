from django.db import models
import os
from django.conf import settings
from django.contrib.auth.models import User

# Create your models here.

class Topic(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.CharField(max_length=300, blank=True, default="")

    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=5000)
    content = models.TextField(help_text="Soạn thảo bằng LaTeX")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0)
    public = models.BooleanField(default=False)
    thumbnail = models.ImageField(upload_to='thumbnails/', null=True, blank=True, default=None, help_text="Ảnh đại diện bài viết")
    excerpt = models.CharField(max_length=300, blank=True, default="", help_text="Mô tả ngắn gọn bài viết")
    topics = models.ManyToManyField(Topic, related_name='posts', blank=True, help_text="Các chủ đề liên quan")

    def __str__(self):
        return self.title

    def get_upload_dir(self):
        # Thư mục lưu ảnh theo id bài viết
        return os.path.join('uploads', f'post_{self.id}')

    @property
    def thumbnail_url(self):
        if self.thumbnail:
            return self.thumbnail.url
        return None

    def get_thumbnail_display_url(self):
        if self.thumbnail:
            return self.thumbnail.url
        return None