from django.db import transaction
from rest_framework import serializers

from accounts.models import User
from accounts.serializers import UserSerializer
from cart.models import Cart, CartItem
from store.models import Product
from .models import Order, OrderItem


class OrderItemProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'price']


class OrderItemSerializer(serializers.ModelSerializer):
    product = OrderItemProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'created_at', 'items']


class OrderForAdminSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'created_at', 'items']

class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model =Order
        fields = ['status']
        
class OrderCreateSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(id=cart_id).exists():
            raise serializers.ValidationError('There is no cart with this cart id')

        if CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError('Your cart is empty, please add one product.')

        return cart_id

    def validate(self, attrs):
        cart_id = attrs['cart_id']
        request = self.context['request']
        user = request.user
        cart = Cart.objects.get(id=cart_id)

        if user.is_authenticated:
            if cart.user != user:
                raise serializers.ValidationError('شما اجازه استفاده از این سبد را ندارید.')
        else:
            session_cart_id = request.session.get('cart_id')
            if str(session_cart_id) != str(cart.id):
                raise serializers.ValidationError('شما اجازه استفاده از این سبد را ندارید.')

        return attrs

    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']
            user = self.context['request'].user

            order = Order.objects.create(user=user)

            cart_items = CartItem.objects.select_related('product').filter(cart_id=cart_id)
            order_items = []
            for cart_item in cart_items:
                order_items.append(OrderItem(
                    order=order,
                    product_id=cart_item.product_id,
                    price=cart_item.product.price,
                    quantity=cart_item.quantity
                ))

            OrderItem.objects.bulk_create(order_items)

            Cart.objects.filter(id=cart_id).delete()

            return order
