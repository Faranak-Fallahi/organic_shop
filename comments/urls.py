
from . import views
from .views import PostCommentViewSet, ProductCommentViewSet
from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter

app_name = "comments"

router = DefaultRouter()

router.register('post-comments', PostCommentViewSet, basename='post-comments')
router.register('product-comments', ProductCommentViewSet, basename='product-comments')


urlpatterns = [
    re_path(r"post/(?P<slug>[\w\u0600-\u06FF-]+)/add/", views.add_post_comment, name="add-post-comment"),
    re_path(r"product/(?P<slug>[\w\u0600-\u06FF-]+)/add/", views.add_product_comment, name="add-product-comment"),
    path('', include(router.urls)),
]