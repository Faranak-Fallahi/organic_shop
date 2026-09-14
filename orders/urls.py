from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = "orders"


router = DefaultRouter()
router.register('api', views.OrderViewSet, basename='orders_api')

urlpatterns = [
    path('create/', views.order_create_view, name='order_create'),
    path('my-orders/', views.order_list_view, name='order_list'),
    path("my-orders/<int:order_id>/", views.order_detail_view, name="order-detail"),
    path("payment/<int:order_id>/", views.order_payment_view, name="order-payment" ),
    path("payment/callback/<int:order_id>/",views.order_payment_callback_view,
        name="order-payment-callback" ),
        
    path('', include(router.urls)),
]
