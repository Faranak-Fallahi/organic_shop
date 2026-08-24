from django.shortcuts import render
from django.db.models import Count
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.core.paginator import Paginator
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


def product_list_view(request):
    categories = Category.objects.annotate(
        num_of_products=Count("products")
    ).order_by("title")

    selected_category_slug = request.GET.get("category", "").strip()

    products = (
        Product.objects
        .select_related("category")
        .filter(is_active=True)
    )

    selected_category = None

    if selected_category_slug:
        selected_category = categories.filter(
            slug=selected_category_slug
        ).first()

        if selected_category:
            products = products.filter(category=selected_category)
        else:
            products = products.none()
    else:
        products = products.order_by("?")

    paginator = Paginator(products, 20)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "categories": categories,
        "products": page_obj.object_list,
        "page_obj": page_obj,
        "paginator": paginator,
        "selected_category": selected_category,
        "selected_category_slug": selected_category_slug,
    }

    return render(
        request,
        "store/product_list.html",
        context
    )
