from django.shortcuts import render, redirect, get_object_or_404
from .models import Post
from .forms import PostForm
import pypandoc
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

def post_list(request):
    posts = Post.objects.select_related('author').order_by('-created_at')
    return render(request, 'blog/post_list.html', {'posts': posts})

def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = user.posts.order_by('-created_at')
    return render(request, 'blog/user_profile.html', {'profile_user': user, 'posts': posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.views += 1
    post.save(update_fields=['views'])
    # Compile LaTeX to HTML using pypandoc
    try:
        html_content = pypandoc.convert_text(post.content, 'html', format='latex')
    except Exception:
        html_content = '<pre>' + post.content + '</pre>'
    # Lấy danh sách ảnh trong thư mục uploads/post_{id}
    img_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', f'post_{post.id}')
    images = []
    if os.path.exists(img_dir):
        for f in os.listdir(img_dir):
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                images.append(os.path.join('uploads', f'post_{post.id}', f))
    return render(request, 'blog/post_detail.html', {'post': post, 'html_content': html_content, 'images': images})

def post_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        if title:
            # Không dùng %s trong chuỗi có ký tự % (LaTeX comment), dùng f-string thay thế
            default_content = (
                "\\documentclass{article}\n"
                "\\usepackage{graphicx} % Required for inserting images\n\n"
                f"\\title{{{title}}}\n"
                "\\author{}\n\n"
                "\\begin{document}\n\n"
                "\\maketitle\n\n"
                "\\section{Introduction}\n\n"
                "\\end{document}\n"
            )
            post = Post.objects.create(
                title=title,
                content=default_content,
                author=request.user if request.user.is_authenticated else None
            )
            return redirect('post_edit', pk=post.id)
    return render(request, 'blog/post_create.html')

def latex_editor(request):
    # Lấy danh sách file .tex, .png, .jpg trong thư mục latex
    latex_dir = os.path.join(settings.BASE_DIR, 'latex')
    files = []
    for f in os.listdir(latex_dir):
        if f.lower().endswith(('.tex', '.png', '.jpg', '.jpeg', '.gif')):
            files.append(f)
    files.sort()
    return render(request, 'blog/latex_editor.html', {'files': files})

@csrf_exempt
def latex_render_html(request):
    # AJAX: nhận nội dung latex, trả về html kèm CSS mặc định của pandoc
    if request.method == 'POST':
        latex = request.POST.get('latex', '')
        import pypandoc
        try:
            html_body = pypandoc.convert_text(latex, 'html', format='latex')
            # Thêm CSS mặc định của pandoc
            pandoc_css = '''
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
<style>
  body { font-family: 'Segoe UI', Arial, sans-serif; padding: 20px; }
  .center, .text-center { text-align: center !important; }
  .flushright, .text-end { text-align: right !important; }
  .flushleft, .text-start { text-align: left !important; }
  div.figure { text-align: center !important; }
  table { border-collapse: collapse; width: 100%; }
  td, th { border: 1px solid #ccc; padding: 4px 8px; }
  pre, code { background: #f8f8f8; border-radius: 4px; padding: 2px 6px; }
</style>
'''
            html = pandoc_css + html_body
        except Exception:
            html = '<pre>' + latex + '</pre>'
        return JsonResponse({'html': html})
    return JsonResponse({'error': 'Invalid request'}, status=400)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('post_list')
    else:
        form = UserCreationForm()
    return render(request, 'blog/register.html', {'form': form})

def project_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            # Nội dung mặc định
            default_content = r"""\\documentclass{article}
\\usepackage{graphicx} % Required for inserting images

\\title{%s}
\\author{%%(author)s}

\\begin{document}

\\maketitle

\\section{Introduction}

\\end{document}
""" % name
            # Tạo post mới với nội dung mặc định
            post = Post.objects.create(
                title=name,
                content=default_content,
                author=request.user if request.user.is_authenticated else None
            )
            return redirect('post_edit', pk=post.id)
    return render(request, 'blog/project_create.html')
