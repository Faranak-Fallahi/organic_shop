from .models import Category, Favorite, Product
from .permissions import IsAdminOrReadOnly
from .serializers import CategorySerializer, ProductSerializer

from cart.models import Cart
from datetime import timedelta

from django_filters.rest_framework import DjangoFilterBackend
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, DecimalField, ExpressionWrapper, F
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter


def home_view(request):
    one_week_ago = timezone.now() - timedelta(days=7)

    categories = (
        Category.objects
        .annotate(num_of_products=Count('products'))
        .prefetch_related('products')[:12]
    )

    latest_products = (
        Product.objects
        .select_related('category')
        .filter(created_at__gte=one_week_ago)
        .order_by('-created_at')[:8]
    )

    if not latest_products.exists():
        latest_products = (
            Product.objects
            .select_related('category')
            .order_by('-created_at')[:8]
        )

    amazing_products = (
        Product.objects
        .select_related('category')
        .filter(
            inventory__gt=0,
            discount__gte=20
        )
        .order_by('-discount')[:8]
    )

    discounted_products = (
        Product.objects
        .select_related('category')
        .filter(discount__gt=0)
        .order_by('-discount')[:8]
    )

    favorite_product_ids = []

    if request.user.is_authenticated:
        favorite_product_ids = list(
            Favorite.objects
            .filter(user=request.user)
            .values_list('product_id', flat=True)
        )

    context = {
        'categories': categories,
        'latest_products': latest_products,
        'amazing_products': amazing_products,
        'discounted_products': discounted_products,
        'favorite_product_ids': favorite_product_ids,
    }

    return render(request, 'home.html', context)


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

    lookup_field = 'slug'

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_fields = ['title']
    search_fields = ['title']

    def get_queryset(self):
        return (
            Category.objects
            .annotate(num_of_products=Count('products'))
            .prefetch_related('products')
        )


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]

    lookup_field = 'slug'

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_fields = ['category_id', 'is_active']
    search_fields = ['title']

    ordering_fields = ['price', 'updated_at']
    ordering = ['-updated_at']

    def get_queryset(self):
        return (
            Product.objects
            .select_related('category')
            .all()
        )


def product_list_view(request):

    category_slug = request.GET.get('category')
    q = request.GET.get('q', '').strip()
    sort = request.GET.get('sort', '').strip()

    selected_category = None

    products_queryset = (
        Product.objects
        .select_related('category')
        .all()
    )

    # جستجوی محصول
    if q:
        products_queryset = products_queryset.filter(
            title__icontains=q
        )

    # فیلتر دسته‌بندی
    if category_slug:
        selected_category = get_object_or_404(
            Category,
            slug=category_slug
        )

        products_queryset = products_queryset.filter(
            category=selected_category
        )

    # مرتب‌سازی بر اساس قیمت نهایی (پس از تخفیف)
    products_queryset = products_queryset.annotate(
        _final_price=ExpressionWrapper(
            F('price') * (100 - F('discount')) / 100,
            output_field=DecimalField(max_digits=10, decimal_places=2),
        )
    )

    sort_options = {
        'newest': '-created_at',
        'cheapest': '_final_price',
        'expensive': '-_final_price',
        'discount': '-discount',
    }

    if sort in sort_options:
        products_queryset = products_queryset.order_by(sort_options[sort])

    paginator = Paginator(products_queryset, 9)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = (
        Category.objects
        .annotate(num_of_products=Count('products'))
        .prefetch_related('products')
    )

    favorite_product_ids = []

    if request.user.is_authenticated:
        favorite_product_ids = list(
            Favorite.objects
            .filter(user=request.user)
            .values_list('product_id', flat=True)
        )

    cart_quantities = {}

    try:
        cart = Cart(request)

        for item in cart:
            product = item.get('product')

            product_id = (
                getattr(product, 'id', None)
                or item.get('product_id')
            )

            if product_id:
                cart_quantities[int(product_id)] = item.get(
                    'quantity',
                    1
                )

    except Exception:
        session_cart = request.session.get('cart', {})

        for product_id, value in session_cart.items():

            try:
                quantity = (
                    value.get('quantity', 1)
                    if isinstance(value, dict)
                    else int(value)
                )

                cart_quantities[int(product_id)] = quantity

            except (ValueError, TypeError):
                continue

    context = {
        'products': page_obj,
        'page_obj': page_obj,
        'paginator': paginator,
        'categories': categories,
        'selected_category': selected_category,
        'selected_category_slug': category_slug,
        'favorite_product_ids': favorite_product_ids,
        'cart_quantities': cart_quantities,
        'q': q,
        'sort': sort,
    }

    return render(
        request,
        'store/product_list.html',
        context
    )


@login_required
def add_to_favorite_view(request, product_id):

    if request.method != 'POST':
        return redirect('store:home')

    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True
    )

    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        product=product
    )

    if created:
        messages.success(
            request,
            'محصول به علاقه‌مندی‌ها اضافه شد.'
        )
    else:
        messages.info(
            request,
            'این محصول از قبل در علاقه‌مندی‌های شما قرار دارد.'
        )

    return redirect(
        request.POST.get('next', 'store:home')
    )


@login_required
def remove_from_favorite_view(request, product_id):

    if request.method != 'POST':
        return redirect('store:home')

    Favorite.objects.filter(
        user=request.user,
        product_id=product_id
    ).delete()

    messages.success(
        request,
        'محصول از علاقه‌مندی‌ها حذف شد.'
    )

    return redirect(
        request.POST.get('next', 'store:home')
    )


@login_required
def favorite_list_view(request):

    favorites = (
        Favorite.objects
        .filter(user=request.user)
        .select_related(
            'product',
            'product__category'
        )
    )

    favorite_product_ids = (
        favorites.values_list('product_id', flat=True)
    )

    return render(
        request,
        'store/favorite_list.html',
        {
            'favorites': favorites,
            'favorite_product_ids': favorite_product_ids,
        }
    )


@login_required
def favorite_remove_view(request, item_id):

    if request.method == 'POST':

        favorite_item = get_object_or_404(
            Favorite,
            id=item_id,
            user=request.user
        )

        favorite_item.delete()

    return redirect('store:favorite-list')


def product_detail(request, slug):

    product = get_object_or_404(
        Product,
        slug=slug
    )

    related_products = (
        Product.objects
        .select_related('category')
        .filter(category=product.category)
        .exclude(id=product.id)
        .order_by('-created_at')[:6]
    )

    if not related_products.exists():
        related_products = (
            Product.objects
            .select_related('category')
            .exclude(id=product.id)
            .order_by('-created_at')[:6]
        )

    comments = (
        product.comments
        .filter(is_active=True, parent=None)
        .select_related('user')
        .prefetch_related('replies')
        .order_by('-created_at')
    )

    favorite_product_ids = []

    if request.user.is_authenticated:
        favorite_product_ids = list(
            Favorite.objects
            .filter(user=request.user)
            .values_list('product_id', flat=True)
        )

    context = {
        'product': product,
        'related_products': related_products,
        'comments': comments,
        'favorite_product_ids': favorite_product_ids,
    }

    return render(
        request,
        'store/product_detail.html',
        context
    )


def product_page(request):

    q = request.GET.get('q', '').strip()

    products = (
        Product.objects
        .select_related('category')
        .all()
    )

    if q:
        products = products.filter(
            title__icontains=q
        )

    paginator = Paginator(products, 9)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = (
        Category.objects
        .annotate(num_of_products=Count('products'))
        .prefetch_related('products')
    )

    favorite_product_ids = []

    if request.user.is_authenticated:
        favorite_product_ids = list(
            Favorite.objects
            .filter(user=request.user)
            .values_list('product_id', flat=True)
        )

    cart_quantities = {}

    try:
        cart = Cart(request)

        for item in cart:
            product = item.get('product')

            product_id = (
                getattr(product, 'id', None)
                or item.get('product_id')
            )

            if product_id:
                cart_quantities[int(product_id)] = item.get(
                    'quantity',
                    1
                )

    except Exception:
        session_cart = request.session.get('cart', {})

        for product_id, value in session_cart.items():

            try:
                quantity = (
                    value.get('quantity', 1)
                    if isinstance(value, dict)
                    else int(value)
                )

                cart_quantities[int(product_id)] = quantity

            except (ValueError, TypeError):
                continue

    context = {
        'products': page_obj,
        'page_obj': page_obj,
        'paginator': paginator,
        'categories': categories,
        'favorite_product_ids': favorite_product_ids,
        'cart_quantities': cart_quantities,
        'q': q,
    }

    return render(
        request,
        'store/product_list.html',
        context
    )