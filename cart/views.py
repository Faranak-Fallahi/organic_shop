from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from store.models import Product
from .context_processors import get_or_create_cart
from .models import Cart, CartItem
from django.shortcuts import render
from .serializers import (
    CartSerializer,
    CartItemSerializer,
    AddCartItemSerializer,
    UpdateCartItemSerializer,
)


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [AllowAny]
    http_method_names = ['post', 'get', 'delete']
    lookup_value_regex = '[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'

    SESSION_CART_KEY = 'cart_id'

    def create(self, request, *args, **kwargs):
        user = request.user if request.user.is_authenticated else None

        cart = Cart.objects.create(user=user)

        request.session[self.SESSION_CART_KEY] = str(cart.id)
        request.session.modified = True

        serializer = self.get_serializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        queryset = Cart.objects.select_related('user').prefetch_related('items__product')

        if self.request.user.is_authenticated:
            return queryset.filter(user=self.request.user)
        cart_id = self.request.session.get(self.SESSION_CART_KEY)
        if cart_id:
            return queryset.filter(id=cart_id)
        return queryset.none()

    def destroy(self, request, *args, **kwargs):
        cart = self.get_object()

        if not request.user.is_authenticated:
            session_cart_id = request.session.get(self.SESSION_CART_KEY)
            if str(cart.id) != str(session_cart_id):
                return Response(
                    {'detail': 'شما اجازه حذف این سبد خرید را ندارید.'},
                    status=status.HTTP_403_FORBIDDEN,
                )

        if request.user.is_authenticated and cart.user != request.user:
            return Response(
                {'detail': 'شما اجازه حذف این سبد خرید را ندارید.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        response = super().destroy(request, *args, **kwargs)

        if request.session.get(self.SESSION_CART_KEY) == str(cart.id):
            del request.session[self.SESSION_CART_KEY]
            request.session.modified = True

        return response


class CartItemViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    http_method_names = ['get', 'patch', 'post', 'delete']
    SESSION_CART_KEY = 'cart_id'

    def _get_allowed_cart(self, cart_id):
        if self.request.user.is_authenticated:
            return Cart.objects.filter(
                id=cart_id,
                user=self.request.user,
            ).first()

        session_cart_id = self.request.session.get(self.SESSION_CART_KEY)

        if str(session_cart_id) != str(cart_id):
            return None

        return Cart.objects.filter(
            id=cart_id,
            user__isnull=True,
        ).first()

    def get_queryset(self):
        cart_pk = self.kwargs.get('cart_pk')
        cart = self._get_allowed_cart(cart_pk)

        if cart is None:
            return CartItem.objects.none()

        return CartItem.objects.filter(
            cart=cart
        ).select_related('cart', 'product')

    def get_serializer_class(self):
        if self.action == 'create':
            return AddCartItemSerializer
        if self.action in ['update', 'partial_update']:
            return UpdateCartItemSerializer
        return CartItemSerializer

    def create(self, request, *args, **kwargs):
        cart_pk = self.kwargs.get('cart_pk')
        cart = self._get_allowed_cart(cart_pk)

        if cart is None:
            return Response(
                {'detail': 'شما اجازه دسترسی به این سبد خرید را ندارید.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(data=request.data, context={'cart': cart})
        serializer.is_valid(raise_exception=True)

        product = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity},
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save(update_fields=['quantity'])

        return Response(
            CartItemSerializer(cart_item).data,
            status=status.HTTP_201_CREATED,
        )

    def partial_update(self, request, *args, **kwargs):
        cart_pk = self.kwargs.get('cart_pk')

        if not self._get_allowed_cart(cart_pk):
            return Response(
                {'detail': 'شما اجازه دسترسی به این سبد خرید را ندارید.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        cart_pk = self.kwargs.get('cart_pk')

        if not self._get_allowed_cart(cart_pk):
            return Response(
                {'detail': 'شما اجازه دسترسی به این سبد خرید را ندارید.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        return super().destroy(request, *args, **kwargs)


@require_POST
def add_to_cart_view(request, product_id):
    cart = get_or_create_cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)

    if product.inventory <= 0:
        messages.error(request, 'این محصول در حال حاضر موجود نیست.')
        return redirect(request.META.get('HTTP_REFERER', 'store:product-page'))

    # خواندن quantity واقعی از POST و اعتبارسنجی عددی
    raw_quantity = request.POST.get('quantity')
    try:
        quantity = int(str(raw_quantity).translate(
            str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')
        ))
    except (TypeError, ValueError):
        quantity = None

    if quantity is None or quantity < 1:
        quantity = product.min_order_quantity or 1

    # رعایت حداقل مقدار سفارش
    if quantity < product.min_order_quantity:
        quantity = product.min_order_quantity

    cart_item = CartItem.objects.filter(cart=cart, product=product).first()
    existing = cart_item.quantity if cart_item else 0

    # سقف موجودی: quantity در سبد هرگز از موجودی بیشتر نشود
    if existing + quantity > product.inventory:
        max_addable = product.inventory - existing
        if max_addable <= 0:
            messages.error(
                request,
                f'حداکثر موجودی مجاز «{product.inventory} {product.unit}» است و '
                'همین مقدار از قبل در سبد شما قرار دارد.',
            )
            return redirect(request.META.get('HTTP_REFERER', 'store:product-page'))
        quantity = max_addable
        messages.warning(
            request,
            f'موجودی محصول محدود است؛ {product.inventory} {product.unit} '
            'به سبد شما افزوده شد.',
        )

    new_quantity = existing + quantity

    if cart_item:
        cart_item.quantity = new_quantity
        cart_item.save(update_fields=['quantity'])
    else:
        CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=new_quantity,
        )

    messages.success(
        request,
        f'محصول «{product.title}» به سبد خرید افزوده شد.',
    )

    return redirect(request.META.get('HTTP_REFERER', 'store:product-page'))


@require_POST
def decrease_cart_item_view(request, product_id):
    cart = get_or_create_cart(request)
    product = get_object_or_404(Product, id=product_id)

    cart_item = CartItem.objects.filter(cart=cart, product=product).first()
    if cart_item:
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save(update_fields=['quantity'])
        else:
            cart_item.delete()

    return redirect(request.META.get('HTTP_REFERER', 'store:product-page'))


@require_POST
def remove_from_cart_view(request, product_id):
    cart = get_or_create_cart(request)
    product = get_object_or_404(Product, id=product_id)
    CartItem.objects.filter(cart=cart, product=product).delete()

    return redirect(request.META.get('HTTP_REFERER', 'store:product-page'))


def cart_detail_view(request):
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product').all()

    return render(request, 'cart/cart_detail.html', {
        'cart': cart,
        'cart_items': cart_items,
        'cart_total_price': cart.get_total_price(),
        'cart_count': cart.get_total_quantity(),
    })