from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "slug")
    search_fields = ("title",)
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "category", "price", "is_active", "created_at" ,
                    "availability_status", "inventory_status")
    list_editable = ("price",)
    list_filter = ("is_active", "category", "created_at")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    
    # به اینا میگنcomputed fields
    def inventory_status(self,obj):
        if obj.inventory<10:
            return 'low'
        if obj.inventory>50:
            return 'heigh'
        return 'medium'
        
    def availability_status(self,obj):
        if obj.inventory == 0:
            return 'اتمام موجودی'
        return 'موجود'
