from .views import PostCommentViewSet, ProductCommentViewSet
from django.urls import path, include
from rest_framework.routers import DefaultRouter


router = DefaultRouter()

router.register('post-comments', PostCommentViewSet, basename='post-comments')
router.register('product-comments', ProductCommentViewSet, basename='product-comments')


urlpatterns = [
    path('', include(router.urls)),
]