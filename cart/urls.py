from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from . import views

app_name = "cart"

router = DefaultRouter()
router.register('', views.CartViewSet, basename='carts')

cart_router = routers.NestedDefaultRouter(router, '', lookup='cart')
cart_router.register('items', views.CartItemViewSet, basename='cart-items')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(cart_router.urls)),
]
