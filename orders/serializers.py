from rest_framework import serializers
from accounts.serializers import  UserSerializer
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
    user = UserSerializer(read_only=True)
    class Meta:
        model = Order 
        fields =['id','user' ,'status' ,'created_at','items']
        