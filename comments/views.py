from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import PostComment, ProductComment
from .serializers import PostCommentSerializer, ProductCommentSerializer
from .permissions import IsAdminOrOwnerOrReadOnly

class PostCommentViewSet(ModelViewSet):
    serializer_class = PostCommentSerializer
    permission_classes = [IsAdminOrOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['post', 'user', 'is_active']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        # فقط کامنت‌های اصلی (بدون والد) را برمی‌گردانیم چون ریپلای‌ها داخل خود کامنت لود می‌شوند
        return PostComment.objects.filter(parent=None).select_related('user')

    def perform_create(self, serializer):
        # کاربر لاگین شده را به‌صورت خودکار ذخیره می‌کنیم
        serializer.save(user=self.request.user)


class ProductCommentViewSet(ModelViewSet):
    serializer_class = ProductCommentSerializer
    permission_classes = [IsAdminOrOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['product', 'user', 'is_active']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return ProductComment.objects.filter(parent=None).select_related('user')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
