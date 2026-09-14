from rest_framework import serializers
from .models import Category ,Product


class CategorySerializer(serializers.ModelSerializer):
    
    num_of_products = serializers.IntegerField(source='products.count',read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'title', 'slug', 'num_of_products']
        
        
class ProductSerializer(serializers.ModelSerializer):
    base_price = serializers.DecimalField(
        source='price',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    final_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    has_discount = serializers.BooleanField(read_only=True)
    image = serializers.ImageField(read_only=True)
    unit = serializers.CharField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'category',
            'title',
            'slug',
            'image',
            'description',
            'unit',
            'price',
            'base_price',
            'final_price',
            'discount',
            'has_discount',
            'inventory',
            'min_order_quantity',
            'is_active',
            'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'updated_at']

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError('قیمت باید بزرگ‌تر از صفر باشد.')
        return value

    def validate_discount(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError('تخفیف باید بین ۰ تا ۱۰۰ باشد.')
        return value