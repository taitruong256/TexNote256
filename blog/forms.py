from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    image = forms.ImageField(required=False, help_text="Tải ảnh lên (nếu có)")
    class Meta:
        model = Post
        fields = ['title', 'content', 'excerpt', 'thumbnail']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'latex-editor', 'rows': 15}),
            'excerpt': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Mô tả ngắn gọn về bài viết...'}),
        }
