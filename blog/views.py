from django.shortcuts import render, redirect, get_object_or_404
from .models import Post
from .forms import PostForm
import pypandoc
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

def post_list(request):
    posts = Post.objects.order_by('-created_at')
    return render(request, 'blog/post_list.html', {'posts': posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
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
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save()
            # Tạo thư mục theo id bài viết
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', f'post_{post.id}')
            os.makedirs(upload_dir, exist_ok=True)
            # Lưu ảnh nếu có
            image = form.cleaned_data.get('image')
            if image:
                img_path = os.path.join(upload_dir, image.name)
                with default_storage.open(img_path, 'wb+') as destination:
                    for chunk in image.chunks():
                        destination.write(chunk)
            return redirect('post_detail', pk=post.id)
    else:
        form = PostForm()
    return render(request, 'blog/post_form.html', {'form': form})

def latex_editor(request):
    # Lấy danh sách file .tex, .png, .jpg trong thư mục latex
    latex_dir = os.path.join(settings.BASE_DIR, 'latex')
    files = []
    for f in os.listdir(latex_dir):
        if f.lower().endswith(('.tex', '.png', '.jpg', '.jpeg', '.gif')):
            files.append(f)
    files.sort()
    return render(request, 'blog/latex_editor.html', {'files': files})

def latex_load_file(request):
    # AJAX: trả về nội dung file
    filename = request.GET.get('filename')
    latex_dir = os.path.join(settings.BASE_DIR, 'latex')
    file_path = os.path.join(latex_dir, filename)
    if not os.path.exists(file_path):
        return JsonResponse({'error': 'File not found'}, status=404)
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return JsonResponse({'content': content})

def latex_save_file(request):
    # AJAX: lưu nội dung file
    if request.method == 'POST':
        filename = request.POST.get('filename')
        content = request.POST.get('content')
        latex_dir = os.path.join(settings.BASE_DIR, 'latex')
        file_path = os.path.join(latex_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def latex_upload_image(request):
    # AJAX: upload ảnh vào thư mục latex
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        latex_dir = os.path.join(settings.BASE_DIR, 'latex')
        img_path = os.path.join(latex_dir, image.name)
        with open(img_path, 'wb+') as destination:
            for chunk in image.chunks():
                destination.write(chunk)
        return JsonResponse({'success': True, 'filename': image.name})
    return JsonResponse({'error': 'No image uploaded'}, status=400)

@csrf_exempt
def latex_render_html(request):
    # AJAX: nhận nội dung latex, trả về html
    if request.method == 'POST':
        latex = request.POST.get('latex', '')
        import pypandoc
        try:
            html = pypandoc.convert_text(latex, 'html', format='latex')
        except Exception:
            html = '<pre>' + latex + '</pre>'
        return JsonResponse({'html': html})
    return JsonResponse({'error': 'Invalid request'}, status=400)
