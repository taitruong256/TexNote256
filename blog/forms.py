from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    image = forms.ImageField(required=False, help_text="Tải ảnh lên (nếu có)")
    class Meta:
        model = Post
        fields = ['title', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'latex-editor', 'rows': 15}),
        }
