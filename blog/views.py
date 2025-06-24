from django.shortcuts import render, redirect, get_object_or_404
from .models import Post
from .forms import PostForm
import pypandoc
import os
import re
from django.conf import settings
from django.core.files.storage import default_storage
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.http import HttpResponseForbidden
from django.views.decorators.http import require_GET

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
    # Thay thế đường dẫn ảnh trong content trước khi render
    content = post.content
    def replace_img(match):
        fname = match.group(1)
        if fname.startswith('http://') or fname.startswith('https://') or fname.startswith('/'):
            return match.group(0)
        return f'\\includegraphics[width=0.9\\linewidth]{{http://127.0.0.1:8000/media/uploads/post_{post.id}/' + fname + '}'
    content = re.sub(r'\\includegraphics\[.*?\]\{([^\}]+)\}', replace_img, content)
    try:
        html_content = pypandoc.convert_text(content, 'html', format='latex')
    except Exception:
        html_content = '<pre>' + content + '</pre>'
    img_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', f'post_{post.id}')
    images = []
    if os.path.exists(img_dir):
        for f in os.listdir(img_dir):
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                images.append(f'http://127.0.0.1:8000/uploads/post_{post.id}/{f}')
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
        post_id = request.POST.get('post_id')
        if post_id:
            def replace_img(match):
                fname = match.group(1)
                # Nếu đã là URL thì giữ nguyên
                if fname.startswith('http://') or fname.startswith('https://') or fname.startswith('/'):
                    return match.group(0)
                # Thay thế thành đường dẫn tuyệt đối
                return f'\\includegraphics[width=0.9\\linewidth]{{http://127.0.0.1:8000/media/uploads/post_{post_id}/' + fname + '}'
            latex = re.sub(r'\\includegraphics\[.*?\]\{([^\}]+)\}', replace_img, latex)
        try:
            html_body = pypandoc.convert_text(latex, 'html', format='latex')
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

def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user != post.author:
        return HttpResponseForbidden("Bạn không có quyền sửa bài này.")
    main_tex_path = os.path.join(settings.MEDIA_ROOT, 'uploads', f'post_{post.id}', 'main.tex')
    main_tex_content = None
    if os.path.exists(main_tex_path):
        with open(main_tex_path, 'r', encoding='utf-8') as f:
            main_tex_content = f.read()
    else:
        main_tex_content = post.content
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save()
            os.makedirs(os.path.dirname(main_tex_path), exist_ok=True)
            with open(main_tex_path, 'w', encoding='utf-8') as f:
                f.write(post.content)
            if 'save_continue' in request.POST:
                # Lưu và tiếp tục chỉnh sửa
                form = PostForm(instance=post, initial={'content': post.content})
                # Lấy lại danh sách file liên quan
                related_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', f'post_{post.id}')
                related_files = []
                if os.path.exists(related_dir):
                    related_files = os.listdir(related_dir)
                return render(request, 'blog/post_form.html', {'form': form, 'edit_mode': True, 'post': post, 'related_files': related_files, 'message': 'Đã lưu thành công!'})
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post, initial={'content': main_tex_content})
    related_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', f'post_{post.id}')
    related_files = []
    if os.path.exists(related_dir):
        related_files = os.listdir(related_dir)
    return render(request, 'blog/post_form.html', {'form': form, 'edit_mode': True, 'post': post, 'related_files': related_files})

@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user != post.author:
        return HttpResponseForbidden("Bạn không có quyền xóa bài này.")
    if request.method == 'POST':
        post.delete()
        return redirect('post_list')
    return render(request, 'blog/post_confirm_delete.html', {'post': post})

@csrf_exempt
@login_required
def latex_upload_image(request):
    post_id = request.POST.get('post_id')
    if request.method == 'POST' and request.FILES.get('image') and post_id:
        image = request.FILES['image']
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', f'post_{post_id}')
        os.makedirs(upload_dir, exist_ok=True)
        img_path = os.path.join(upload_dir, image.name)
        with open(img_path, 'wb+') as destination:
            for chunk in image.chunks():
                destination.write(chunk)
        # Luôn trả về JSON, không redirect nữa
        return JsonResponse({'success': True, 'filename': image.name})
    return JsonResponse({'error': 'No image uploaded'}, status=400)

@login_required
def api_post_files(request, pk):
    post = get_object_or_404(Post, pk=pk)
    related_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', f'post_{post.id}')
    files = []
    if os.path.exists(related_dir):
        files = os.listdir(related_dir)
    return JsonResponse({'files': files})

@require_GET
@login_required
def api_post_file_content(request, pk):
    post = get_object_or_404(Post, pk=pk)
    filename = request.GET.get('filename')
    if not filename:
        return JsonResponse({'error': 'Missing filename'}, status=400)
    related_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', f'post_{post.id}')
    file_path = os.path.join(related_dir, filename)
    if not os.path.exists(file_path):
        return JsonResponse({'error': 'File not found'}, status=404)
    # Chỉ cho phép đọc file .tex
    if not filename.lower().endswith('.tex'):
        return JsonResponse({'error': 'Not allowed'}, status=403)
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return JsonResponse({'content': content})
