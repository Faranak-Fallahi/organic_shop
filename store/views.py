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
    lookup_field = 'slug'

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
                
    filterset_fields = ['category_id', 'is_active']
    search_fields = ['title']
    ordering_fields = ['price', 'updated_at']

    ordering = ['-updated_at']

    def get_queryset(self):
        return Product.objects.select_related('category').all()