from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views


app_name = "store"


router = DefaultRouter()

router.register(
    "products",
    views.ProductViewSet,
    basename="product"
)

router.register(
    "categories",
    views.CategoryViewSet,
    basename="category"
)


urlpatterns = [
    path(
        "",
        views.product_list_view,
        name="product-page"
    ),

    path(
        "api/",
        include(router.urls)
    ),
]
