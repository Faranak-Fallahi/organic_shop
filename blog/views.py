from django.shortcuts import render,get_object_or_404
from .models import Post
from comments.models import PostComment


def post_list(request):
    posts = Post.objects.filter(published=True)

    return render(request, 'blog/post_list.html', {
        'posts': posts
    })

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    comments = PostComment.objects.filter(post = post, is_active=True, parent=None,)

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
    })
