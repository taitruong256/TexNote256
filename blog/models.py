from django.db import models
import os
from django.conf import settings
from django.contrib.auth.models import User

# Create your models here.

class Post(models.Model):
    title = models.CharField(max_length=5000)
    content = models.TextField(help_text="Soạn thảo bằng LaTeX")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

    def get_upload_dir(self):
        # Thư mục lưu ảnh theo id bài viết
        return os.path.join('uploads', f'post_{self.id}')

    def image_url(self):
        # Trả về url ảnh đầu tiên trong thư mục uploads/post_{id} nếu có
        import os
        from django.conf import settings
        img_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', f'post_{self.id}')
        if os.path.exists(img_dir):
            for f in os.listdir(img_dir):
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    return settings.MEDIA_URL + f'uploads/post_{self.id}/' + f
        return None
