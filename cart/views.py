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
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer
    permission_classes = [AllowAny]
    http_method_names = ['post', 'get']

    def create(self, request, *args, **kwargs):
        cart = Cart.objects.create()
        serializer = self.get_serializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CartItemViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]

    def get_queryset(self):
        cart_pk = self.kwargs.get('cart_pk')
        return CartItem.objects.filter(cart_id=cart_pk).select_related('product')

    def get_serializer_class(self):
        if self.action == 'create':
            return AddCartItemSerializer
        if self.action in ['update', 'partial_update']:
            return UpdateCartItemSerializer
        return CartItemSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart_pk = self.kwargs.get('cart_pk')
        cart = get_object_or_404(Cart, pk=cart_pk)

        product = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        output_serializer = CartItemSerializer(cart_item)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
