from . import views
from django.urls import path

app_name = "store"

urlpatterns = [
    path("product/", views.ProductList.as_view(), name="product_list"),
    path("product/<slug:slug>/", views.ProductDetail.as_view(), name="product_detail"),
     path("category/", views.CategoryList.as_view(), name="category_list"),
    path("category/<slug:slug>/", views.CategoryDetail.as_view(), name="category_detail"),
]
