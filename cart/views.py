from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Cart, CartItem
from .serializers import (
    CartSerializer,
    CartItemSerializer,
    AddCartItemSerializer,
    UpdateCartItemSerializer,
)


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [AllowAny]
    http_method_names = ['post', 'get' ,'delete']
    lookup_value_regex = '[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'

    SESSION_CART_KEY = 'cart_id'
    
    # def create(self, request, *args, **kwargs):
    #     cart = Cart.objects.create()
    #     request.session[self.SESSION_CART_KEY] = str(cart.id)
    #     request.session.modified = True
    #     serializer = self.get_serializer(cart)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)
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
                    status=status.HTTP_403_FORBIDDEN
                )

        if request.user.is_authenticated and cart.user != request.user:
            return Response(
                {'detail': 'شما اجازه حذف این سبد خرید را ندارید.'},
                status=status.HTTP_403_FORBIDDEN
            )

        response = super().destroy(request, *args, **kwargs)

        if request.session.get(self.SESSION_CART_KEY) == str(cart.id):
            del request.session[self.SESSION_CART_KEY]
            request.session.modified = True

        return response
    
class CartItemViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    http_method_names = ['get','patch','post','delete']
    SESSION_CART_KEY = 'cart_id'
    
    # def _is_allowed_cart(self, cart_id):
    #     if self.request.user.is_authenticated:
    #         return Cart.objects.filter(id=cart_id, user=self.request.user).exists()

    #     session_cart_id = self.request.session.get(self.SESSION_CART_KEY)
    #     return session_cart_id and str(session_cart_id) == str(cart_id)
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


    # def get_queryset(self):
    #     cart_pk = self.kwargs.get('cart_pk')
    #     if not self._is_allowed_cart(cart_pk):
    #         return CartItem.objects.none()
    #     return CartItem.objects.filter(cart_id=cart_pk).select_related('cart','product')
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

    # def create(self, request, *args, **kwargs):
    #     cart_pk = self.kwargs.get('cart_pk')

    #     if not self._is_allowed_cart(cart_pk):
    #         return Response(
    #             {'detail': 'شما اجازه دسترسی به این سبد خرید را ندارید.'},
    #             status=status.HTTP_403_FORBIDDEN
    #         )

    #     cart = get_object_or_404(Cart, pk=cart_pk)

    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)

    #     product = serializer.validated_data['product']
    #     quantity = serializer.validated_data['quantity']

    #     cart_item, created = CartItem.objects.get_or_create(
    #         cart=cart,
    #         product=product,
    #         defaults={'quantity': quantity}
    #     )

    #     if not created:
    #         cart_item.quantity += quantity
    #         cart_item.save()

    #     output_serializer = CartItemSerializer(cart_item)
    #     return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    def create(self, request, *args, **kwargs):
        cart_pk = self.kwargs.get('cart_pk')
        cart = self._get_allowed_cart(cart_pk)

        if cart is None:
            return Response(
                {'detail': 'شما اجازه دسترسی به این سبد خرید را ندارید.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(data=request.data)
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

        if not self._is_allowed_cart(cart_pk):
            return Response(
                {'detail': 'شما اجازه دسترسی به این سبد خرید را ندارید.'},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        cart_pk = self.kwargs.get('cart_pk')

        if not self._is_allowed_cart(cart_pk):
            return Response(
                {'detail': 'شما اجازه دسترسی به این سبد خرید را ندارید.'},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().destroy(request, *args, **kwargs)