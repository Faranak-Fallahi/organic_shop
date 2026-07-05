from rest_framework import generics
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from django.db.models import Count

# ویوهای مربوط به دسته‌بندی
class CategoryList(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.annotate(
        num_of_products=Count('products')
        ).prefetch_related('products')
    
    
class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.annotate(
        num_of_products=Count('products')
        ).prefetch_related('products')
    lookup_field = 'slug'  # اگر می‌خواهید با اسلاگ جستجو شود


# ویوهای مربوط به محصولات
class ProductList(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.select_related('category').all()

    def get_serializer_context(self):
        return {'request':self.request}
    
    
class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.select_related('category').all()
    lookup_field = 'slug'  # چون در مدل محصول اسلاگ دارید
