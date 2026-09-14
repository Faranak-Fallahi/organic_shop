from .models import PostComment, ProductComment
from .permissions import IsAdminOrOwnerOrReadOnly
from .serializers import PostCommentSerializer, ProductCommentSerializer
from blog.models import Post
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet
from store.models import Product


class PostCommentViewSet(ModelViewSet):
    serializer_class = PostCommentSerializer
    permission_classes = [IsAdminOrOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['post', 'user', 'is_active']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = PostComment.objects.filter(parent=None).select_related('user')
        if not (self.request.user.is_authenticated and self.request.user.is_staff):
            qs = qs.filter(is_active=True)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProductCommentViewSet(ModelViewSet):
    serializer_class = ProductCommentSerializer
    permission_classes = [IsAdminOrOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['product', 'user', 'is_active']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = ProductComment.objects.filter(parent=None).select_related('user')
        if not (self.request.user.is_authenticated and self.request.user.is_staff):
            qs = qs.filter(is_active=True)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
        
@login_required
def add_post_comment(request, slug):
    post = get_object_or_404(
        Post,
        slug=slug,
        published=True
    )

    if request.method == "POST":
        body = request.POST.get("body", "").strip()

        if body:
            PostComment.objects.create(
                user=request.user,
                post=post,
                body=body,
                parent=None,
                is_active=False
            )

        return redirect(
            "blog:post-detail",
            slug=post.slug
        )

    return redirect(
        "blog:post-detail",
        slug=post.slug
    )


@login_required
def add_product_comment(request, slug):
    product = get_object_or_404(
        Product,
        slug=slug
    )

    if request.method == "POST":
        body = request.POST.get("body", "").strip()
        parent_id = request.POST.get("parent")

        parent = None

        if parent_id:
            parent = ProductComment.objects.filter(
                id=parent_id,
                product=product
            ).first()

        if body:
            ProductComment.objects.create(
                user=request.user,
                product=product,
                body=body,
                parent=parent,
                is_active=False
            )

        return redirect(
            "store:product_detail",
            slug=product.slug
        )

    return redirect(
        "store:product_detail",
        slug=product.slug
    )