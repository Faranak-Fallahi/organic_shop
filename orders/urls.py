from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from . import views

app_name = "orders"

router = DefaultRouter()
router.register('', views.OrderViewSet, basename='orders')

urlpatterns = [
    path('', include(router.urls)),
    
]
