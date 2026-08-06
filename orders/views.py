from django.db.models import Prefetch
from rest_framework import  viewsets
from .models import Order, OrderItem
from .serializers import OrderForAdminSerializer, OrderSerializer
from rest_framework.permissions import IsAuthenticated

class OrderViewSet(viewsets.ModelViewSet):
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

    def get_serializer_class(self):
        if self.request.user.is_staff:
            return OrderForAdminSerializer
        return OrderSerializer