from .models import Post
from rest_framework.viewsets import ModelViewSet
from .serializers import PostListSerializer, PostDetailSerializer
from django.db.models import Count

class PostViewSet(ModelViewSet):
    queryset = Post.objects.all().annotate(comments_count=Count('Post_Comment'))
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'list':
            return PostListSerializer
        return PostDetailSerializer