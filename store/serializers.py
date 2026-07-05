from rest_framework import serializers
from .models import Category ,Product


class CategorySerializer(serializers.ModelSerializer):
    
    num_of_products = serializers.IntegerField(source='products.count',read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'title', 'slug', 'num_of_products']
        
        
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id', 
            'category', 
            'title', 
            'slug', 
            'description', 
            'price', 
            'inventory', 
            'is_active', 
            'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'updated_at']