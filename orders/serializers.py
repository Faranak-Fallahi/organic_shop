from rest_framework import serializers
from accounts.serializers import  UserSerializer
from cart.models import Cart, CartItem
from store.models import Product
from .models import Order, OrderItem

class  OrderItemProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields =['id','title' ,'price' ]
        

class  OrderItemSerializer(serializers.ModelSerializer):
    product = OrderItemProductSerializer(read_only=True)
    class Meta:
        model =  OrderItem
        fields =['id','product' ,'quantity' ,'price']
        
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    class Meta:
        model = Order 
        fields =['id','user' ,'status' ,'created_at','items']
        
class OrderForAdminSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    user = UserSerializer(read_only=True)
    class Meta:
        model = Order 
        fields =['id','user' ,'status' ,'created_at','items']
        
class OrderCreateSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()
    
    def validate_cart_id(self, cart_id):
        # روش اول
        # try:
        #     if Cart.objects.prefetch_related('items').get(id=cart_id).items.count () == 0:
        #     raise serializers.ValidationError('Your cart is empty,please add one product.')
        # except Cart.DoesNotExist:
        #      raise serializers.ValidationError('There is no cart with this cart id')
        # روش دوم
        if not Cart.objects.filter(id=cart_id).exists():
            raise serializers.ValidationError('There is no cart with this cart id')
        if CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError('Your cart is empty,please add one product.')
        return cart_id