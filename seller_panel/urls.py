from django.urls import path
from . import views

app_name = 'seller_panel'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    # محصولات
    path('products/', views.product_list_view, name='product_list'),
    path('products/create/', views.product_create_view, name='product_create'),
    path('products/<int:pk>/edit/', views.product_edit_view, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete_view, name='product_delete'),

    # دسته‌بندی‌ها
    path('categories/', views.category_list_view, name='category_list'),
    path('categories/create/', views.category_create_view, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit_view, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete_view, name='category_delete'),
    path('orders/', views.order_list_view, name='order_list'),
    path('orders/<int:pk>/', views.order_detail_view, name='order_detail'),

    # نظرات
    path('comments/', views.comment_list_view, name='comment_list'),
    path('comments/<str:kind>/<int:pk>/approve/', views.comment_approve_view, name='comment_approve'),
    path('comments/<str:kind>/<int:pk>/reject/', views.comment_reject_view, name='comment_reject'),
]
