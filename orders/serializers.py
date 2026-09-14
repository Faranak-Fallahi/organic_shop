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
        fields = ['id', 'title', 'price', 'final_price', 'unit', 'image']
        read_only_fields = fields


class OrderItemSerializer(serializers.ModelSerializer):
    product = OrderItemProductSerializer(read_only=True)
    total_price = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    total_base_price = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    has_discount = serializers.BooleanField(read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'product',
            'quantity',
            'base_price',
            'price',
            'total_price',
            'total_base_price',
            'has_discount',
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    total_price = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    total_base_price = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    total_discount = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    status_label = serializers.CharField(source='status_label', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'first_name',
            'last_name',
            'phone',
            'city',
            'address',
            'postal_code',
            'status',
            'status_label',
            'created_at',
            'items',
            'total_price',
            'total_base_price',
            'total_discount',
        ]


class OrderForAdminSerializer(OrderSerializer):
    class Meta:
        model = Order
        fields = OrderSerializer.Meta.fields


class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']


class OrderCreateSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=15, required=False, allow_blank=True)
    city = serializers.CharField(max_length=100, required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    postal_code = serializers.CharField(
        max_length=10, required=False, allow_blank=True
    )

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

        # اعتبارسنجی غلظت موجودی + حداقل سفارش
        items = CartItem.objects.filter(cart_id=cart_id).select_related('product')
        for item in items:
            if not item.product.is_active:
                raise serializers.ValidationError(
                    f'محصول «{item.product.title}» فعال نیست.'
                )
            if item.quantity < (item.product.min_order_quantity or 1):
                raise serializers.ValidationError(
                    f'حداقل مقدار سفارش «{item.product.title}» '
                    f'{item.product.min_order_quantity} {item.product.unit} است.'
                )
            if item.quantity > item.product.inventory:
                raise serializers.ValidationError(
                    f'موجودی «{item.product.title}» '
                    f'{item.product.inventory} {item.product.unit} است.'
                )

        return attrs

    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']
            request = self.context['request']
            user = request.user

            profile = None
            if user.is_authenticated:
                try:
                    profile = user.customer_profile
                except Exception:
                    profile = None

            def _val(key, default=''):
                v = self.validated_data.get(key)
                if v is None or str(v).strip() == '':
                    return default
                return v

            first_name = _val('first_name', getattr(user, 'first_name', ''))
            last_name = _val('last_name', getattr(user, 'last_name', ''))
            phone = _val('phone', getattr(user, 'phone', ''))
            city = _val('city', getattr(profile, 'city', '') if profile else '')
            address = _val('address', getattr(profile, 'address', '') if profile else '')
            postal_code = _val(
                'postal_code',
                getattr(profile, 'postal_code', '') if profile else '',
            )

            if user.is_authenticated:
                if first_name:
                    user.first_name = first_name
                if last_name:
                    user.last_name = last_name
                if phone and not user.phone:
                    user.phone = phone
                user.save(update_fields=['first_name', 'last_name', 'phone'])

            order = Order.objects.create(
                user=user,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                city=city,
                address=address,
                postal_code=postal_code,
            )

            cart_items = CartItem.objects.select_related('product').filter(cart_id=cart_id)
            order_items = []
            for cart_item in cart_items:
                order_items.append(OrderItem(
                    order=order,
                    product_id=cart_item.product_id,
                    base_price=cart_item.product.price,
                    price=cart_item.product.final_price,
                    quantity=cart_item.quantity,
                ))

            OrderItem.objects.bulk_create(order_items)

            Cart.objects.filter(id=cart_id).delete()

            return order