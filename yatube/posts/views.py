from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.csrf import csrf_exempt

from .forms import PostForm, CommentForm
from .models import Post, Group, User, Comment, Follow
from .utils import paginator


def index(request):
    post_list = Post.objects.select_related(
        'group'
    ).all().order_by('-pub_date')
    page_obj = paginator(request, post_list)
    index = True
    context = {
        'page_obj': page_obj,
        'index': index
    }
    return render(request, 'posts/index.html', context)


def group(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group).order_by('-pub_date')
    page_obj = paginator(request, post_list)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=author).order_by('-pub_date')
    page_obj = paginator(request, post_list)
    following = (
        request.user.is_authenticated
        and Follow.objects.filter(user=request.user, author=author).exists()
    )
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    user = request.user
    post = get_object_or_404(Post, pk=post_id)
    author = post.author
    post_count = Post.objects.filter(author=author).count()
    comments = Comment.objects.filter(post_id=post_id)
    form = CommentForm(request.POST)
    context = {
        'post': post,
        'author': author,
        'post_count': post_count,
        'post_id': post_id,
        'user': user,
        'comments': comments,
        'form': form
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
@csrf_exempt
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        form = form.save(False)
        form.author = request.user
        form.save()
        return redirect('posts:profile', username=form.author)
    return render(
        request,
        'posts/create_post.html',
        {'form': form}
    )


@login_required
@csrf_exempt
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    is_edit = True
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post.pk)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post.pk)
    return render(
        request,
        'posts/create_post.html',
        {'form': form, 'post': post, 'is_edit': is_edit}
    )


@login_required
@csrf_exempt
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(
        author__following__user=request.user
    ).order_by('-pub_date')
    page_obj = paginator(request, post_list)
    follow = True
    context = {
        'page_obj': page_obj,
        'follow': follow
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user == author:
        return redirect('posts:profile', username=username)
    Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    following = get_object_or_404(User, username=username)
    follower = get_object_or_404(Follow, author=following, user=request.user)
    follower.delete()
    return redirect('posts:profile', username=username)
