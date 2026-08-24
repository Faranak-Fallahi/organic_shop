from .models import Post
from .permissions import IsAdminOrReadOnly
from .serializers import PostListSerializer, PostDetailSerializer
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.viewsets import ModelViewSet
from django.shortcuts import render, get_object_or_404
from .models import Post


class PostViewSet(ModelViewSet):
    lookup_field = 'slug'
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['published']
    search_fields = ['title',]
    ordering_fields = ['updated_at',]
    ordering = ['-updated_at'] 

    def get_queryset(self):
        return Post.objects.annotate(
            comments_count=Count('Post_Comment')
        ).all()


    def get_serializer_class(self):
        if self.action == 'list':
            return PostListSerializer
        return PostDetailSerializer
    
   

def post_list_view(request):
    posts = Post.objects.filter(
        published=True
    ).order_by("-created_at")

    return render(
        request,
        "blog/post_list.html",
        {
            "posts": posts,
        }
    )


def post_detail_view(request, slug):
    post = get_object_or_404(
        Post,
        slug=slug,
        published=True
    )

    return render(
        request,
        "blog/post_detail.html",
        {
            "post": post,
        }
    )
