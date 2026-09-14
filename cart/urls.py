from . import views
from django.urls import path, include
from rest_framework_nested import routers
from rest_framework.routers import DefaultRouter

app_name = "cart"

router = DefaultRouter()
router.register('', views.CartViewSet, basename='carts')

cart_router = routers.NestedDefaultRouter(router, '', lookup='cart')
cart_router.register('items', views.CartItemViewSet, basename='cart-items')

urlpatterns = [
    path('detail/', views.cart_detail_view, name='cart_detail'),
    path('add/<int:product_id>/', views.add_to_cart_view, name='cart_add'),
    path('decrease/<int:product_id>/', views.decrease_cart_item_view, name='cart_decrease'),
    path('remove/<int:product_id>/', views.remove_from_cart_view, name='cart_remove'),
    path('', include(router.urls)),
    path('', include(cart_router.urls)),
   
]
