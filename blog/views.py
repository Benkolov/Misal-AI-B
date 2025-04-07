from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db.models import Q

from .forms import PostForm, CommentForm, TagForm, CategoryForm
from .models import Post, Category
from django.shortcuts import get_object_or_404

from .utils import render_markdown


def post_list(request):
    posts = Post.objects.filter(status='published').order_by('-published_at')
    context = {
        'posts': posts
    }
    return render(request, 'blog/post_list.html', context)


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')
    comments = post.comments.filter(active=True)
    new_comment = None

    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            if request.user.is_authenticated:
                new_comment.author_user = request.user
            new_comment.save()
    else:
        comment_form = CommentForm()

    post.content = render_markdown(post.content)

    context = {
        'post': post,
        'comments': comments,
        'new_comment': new_comment,
        'comment_form': comment_form,
    }

    return render(request, 'blog/post_detail.html', context)


def is_staff_user(user):
    return user.is_staff

@login_required
@user_passes_test(is_staff_user, login_url='post list')
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)

        if form.is_valid():
            post = form.save(commit=False)
            if not post.author:  # Ако не е зададен автор, използваме текущия потребител
                post.author = request.user.username
            post.author_user = request.user
            post.save()
            form.save_m2m()  # Запазваме many-to-many връзките (тагове)
            return redirect('post list')
    else:
        form = PostForm()

    context = {
        'form': form
    }

    return render(request, 'blog/post_form.html', context)


@login_required
@user_passes_test(is_staff_user, login_url='post list')
def post_edit(request, slug):
    post = get_object_or_404(Post, slug=slug)

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            form.save_m2m()  # Запазваме many-to-many връзките (тагове)
            return redirect('post detail', slug=post.slug)  # Пренасочване след редакция
    else:
        form = PostForm(instance=post)  # Зареждаме формата с текущите данни

    return render(request, 'blog/post_form.html', {'form': form, 'post': post})


@login_required
@user_passes_test(is_staff_user, login_url='post list')
def tag_create(request):
    if request.method == "POST":
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('post create'))
    else:
        form = TagForm()

    context = {
        'form': form
    }

    return render(request, 'blog/tag_form.html', context)


@login_required
@user_passes_test(is_staff_user, login_url='post list')
def category_create(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('post create')
    else:
        form = CategoryForm()

    context = {
        'form': form
    }

    return render(request, 'blog/category_create.html', context)


def categories_context(request):
    categories = Category.objects.all()
    return {'categories': categories}


def category_list(request):
    categories = Category.objects.all()
    return render(request, 'blog/category_list.html', {'categories': categories})


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(category=category, status='published')
    return render(request, 'blog/category_detail.html', {'category': category, 'posts': posts})


def author_posts(request, author_name):
    # Търсим по потребителско име, имейл или полето author
    posts = Post.objects.filter(
        Q(author_user__username__iexact=author_name) |
        Q(author_user__email__iexact=author_name) |
        Q(author__iexact=author_name),
        status='published'
    ).order_by('-published_at')

    return render(request, 'blog/author_posts.html', {'author_name': author_name, 'posts': posts})


def search_posts(request):
    query = request.GET.get('q', '')
    if query:
        posts = Post.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(excerpt__icontains=query) |
            Q(author_user__username__icontains=query) |
            Q(author_user__email__icontains=query) |
            Q(author__icontains=query),
            status='published'
        ).order_by('-published_at')
    else:
        posts = Post.objects.none()

    context = {
        'posts': posts,
        'query': query,
    }
    return render(request, 'blog/search_results.html', context)
