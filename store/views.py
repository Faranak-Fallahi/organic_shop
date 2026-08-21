from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from .permissions import IsAdminOrReadOnly

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    permission_classes = [IsAdminOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    filterset_fields = ['title']
    search_fields = ['title']
    
    
    def get_queryset(self):
        return Category.objects.annotate(
            num_of_products=Count('products')
        ).prefetch_related('products')


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
                
    filterset_fields = ['category_id', 'is_active']
    search_fields = ['title']
    ordering_fields = ['price', 'updated_at']

    ordering = ['-updated_at']

    def get_queryset(self):
        return Product.objects.select_related('category').all()
    from django.db.models import Count
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from .permissions import IsAdminOrReadOnly


def home_view(request):
    categories = Category.objects.annotate(
        num_of_products=Count('products')
    ).prefetch_related('products')[:12]

    featured_products = Product.objects.select_related('category').filter(
        is_active=True
    ).order_by('-updated_at')[:10]

    latest_products = Product.objects.select_related('category').filter(
        is_active=True
    ).order_by('-created_at')[:8]

    context = {
        'categories': categories,
        'featured_products': featured_products,
        'latest_products': latest_products,
    }
    return render(request, 'home.html', context)


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    permission_classes = [IsAdminOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['title']
    search_fields = ['title']

    def get_queryset(self):
        return Category.objects.annotate(
            num_of_products=Count('products')
        ).prefetch_related('products')


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category_id', 'is_active']
    search_fields = ['title']
    ordering_fields = ['price', 'updated_at']
    ordering = ['-updated_at']

    def get_queryset(self):
        return Product.objects.select_related('category').all()
