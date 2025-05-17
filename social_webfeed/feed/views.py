from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import Post, Like, Comment
from .forms import PostForm, CommentForm

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'feed/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('feed')  # Ensure no leading space
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'feed/login.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def feed(request):
    posts = Post.objects.all().order_by('-created_at')
    post_form = PostForm()
    comment_form = CommentForm()
    return render(request, 'feed/feed.html', {
        'posts': posts,
        'post_form': post_form,
        'comment_form': comment_form,
    })

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('feed')
    return redirect('feed')

@login_required
def like_post(request, post_id):
    post = Post.objects.get(id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
    return redirect('feed')

@login_required
def add_comment(request, post_id):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = Post.objects.get(id=post_id)
            comment.save()
    return redirect('feed')