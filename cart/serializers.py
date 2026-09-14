from rest_framework import serializers
from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source='product.title', read_only=True)
    product_image = serializers.ImageField(source='product.image', read_only=True)
    product_unit = serializers.CharField(source='product.unit', read_only=True)
    product_price = serializers.DecimalField(
        source='product.price',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    product_final_price = serializers.DecimalField(
        source='product.final_price',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    base_price = serializers.DecimalField(
        source='product.price',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    final_price = serializers.DecimalField(
        source='product.final_price',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    has_discount = serializers.BooleanField(source='product.has_discount', read_only=True)
    total_item = serializers.SerializerMethodField()
    total_base_item = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            'id',
            'product',
            'product_title',
            'product_image',
            'product_unit',
            'product_price',
            'product_final_price',
            'base_price',
            'final_price',
            'has_discount',
            'quantity',
            'total_item',
            'total_base_item',
        ]
        read_only_fields = ['id', 'product', 'quantity']

    def get_total_item(self, cart_item):
        return cart_item.get_total_price()

    def get_total_base_item(self, cart_item):
        return cart_item.get_total_base_price()


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    total_price = serializers.SerializerMethodField()
    total_base_price = serializers.SerializerMethodField()
    total_discount = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_price', 'total_base_price', 'total_discount']
        read_only_fields = ['id']

    def get_total_price(self, cart):
        return cart.get_total_price()

    def get_total_base_price(self, cart):
        return cart.get_total_base_price()

    def get_total_discount(self, cart):
        return cart.get_total_discount()


class AddCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['product', 'quantity']

    def validate(self, attrs):
        product = attrs['product']
        quantity = attrs.get('quantity', 1)

        if not product.is_active:
            raise serializers.ValidationError('این محصول فعال نیست.')
        if product.inventory <= 0:
            raise serializers.ValidationError('این محصول در حال حاضر موجود نیست.')

        cart = self.context.get('cart')
        existing_qty = 0
        if cart:
            existing_qty = CartItem.objects.filter(cart=cart, product=product).values_list('quantity', flat=True).first() or 0

        min_qty = product.min_order_quantity or 1
        if quantity < min_qty:
            raise serializers.ValidationError(
                f'حداقل مقدار سفارش این محصول {min_qty} {product.unit} است.'
            )
        if existing_qty + quantity > product.inventory:
            raise serializers.ValidationError(
                f'موجودی این محصول {product.inventory} {product.unit} است.'
            )
        return attrs


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError('تعداد باید حداقل ۱ باشد.')
        return value

    def validate(self, attrs):
        item = self.instance
        if item and attrs.get('quantity', 0) > item.product.inventory:
            raise serializers.ValidationError(
                f'موجودی این محصول {item.product.inventory} {item.product.unit} است.'
            )
        return attrs