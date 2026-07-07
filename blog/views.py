from .models import Post
from rest_framework.viewsets import ModelViewSet
from .serializers import PostListSerializer, PostDetailSerializer
from django.db.models import Count
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


class PostViewSet(ModelViewSet):
    lookup_field = 'slug'
    
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