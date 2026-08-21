from django.db.models import Prefetch
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .models import Order, OrderItem
from .serializers import OrderCreateSerializer, OrderForAdminSerializer, OrderSerializer, OrderUpdateSerializer


class OrderViewSet(viewsets.ModelViewSet):
    http_method_names = ['get','post','patch','delete','options','head']
    
    def get_permissions(self):
        if self.request.method in['PATCH','DELETE']:
            return[IsAdminUser()]
        return[IsAuthenticated()]

    def get_queryset(self):
        queryset = Order.objects.select_related('user').prefetch_related(
            Prefetch(
                'items',
                queryset=OrderItem.objects.select_related('product')
            )
        )
        user = self.request.user
        if user.is_staff:
            return queryset
        return queryset.filter(user=user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderCreateSerializer
        if self.request.method == 'PATCH':
            return OrderUpdateSerializer
        if self.request.user.is_staff:
            return OrderForAdminSerializer
        return OrderSerializer

    def get_serializer_context(self):
        return {'request': self.request}

    def create(self, request, *args, **kwargs):
        create_order_serializer = OrderCreateSerializer(
            data=request.data,
            context={'request': request},
        )
        create_order_serializer.is_valid(raise_exception=True)
        created_order = create_order_serializer.save()

        serializer = OrderSerializer(created_order, context={'request': request})
        return Response(serializer.data)
