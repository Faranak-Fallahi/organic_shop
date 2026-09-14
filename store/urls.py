from . import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = "store"

router = DefaultRouter()
router.register("products", views.ProductViewSet, basename="products")
router.register("categories", views.CategoryViewSet, basename="categories")

urlpatterns = [
    path("", views.home_view, name="home"),
    path("products/", views.product_list_view, name="product-list"),
    path("page/", views.product_list_view, name="product-page"),
    path("favorites/", views.favorite_list_view, name="favorite-list"),
    path("favorites/add/<int:product_id>/", views.add_to_favorite_view,name="add-to-favorite"),
    path("favorites/remove/<int:product_id>/",views.remove_from_favorite_view,name="remove-from-favorite"),
    path('product/<str:slug>/', views.product_detail, name='product_detail'),
    path("api/", include(router.urls)),
]
