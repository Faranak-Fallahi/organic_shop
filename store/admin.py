from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "slug")
    search_fields = ("title",)
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "category", "price", "is_active", "created_at")
    list_editable = ("price",)
    list_filter = ("is_active", "category", "created_at")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
