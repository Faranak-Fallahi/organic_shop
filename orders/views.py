from django.db.models import Prefetch
from django.shortcuts import render
from rest_framework import  viewsets
from .models import Order, OrderItem
from .serializers import OrderSerializer
from rest_framework.permissions import IsAuthenticated

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset =Order.objects.select_related('user').prefetch_related(
            Prefetch(
                'items',
                
                queryset=OrderItem.objects.select_related('product')),
            )
        user = self.request.user
        if user.is_staff:
            return queryset
        return queryset.filter(user=user)
