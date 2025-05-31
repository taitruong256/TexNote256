from django.db import models
import os
from django.conf import settings

# Create your models here.

class Post(models.Model):
    title = models.CharField(max_length=5000)
    content = models.TextField(help_text="Soạn thảo bằng LaTeX")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_upload_dir(self):
        # Thư mục lưu ảnh theo id bài viết
        return os.path.join('uploads', f'post_{self.id}')
