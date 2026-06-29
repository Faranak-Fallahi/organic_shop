from django.contrib import admin ,messages
from .models import Category, Product
from django.db.models import Count
import csv
from django.http import HttpResponse


    
# inline    
class ProductInLine(admin.TabularInline):
    model = Product
    fields = ["title", "category", "price", "is_active",
                "description"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display =["id", "title", "product_count",] 
    search_fields =["title",] 
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ProductInLine]
    
    # omputed fields
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            products_total=Count("products")
        )
    def product_count(self, obj):
        return obj.products_total

    product_count.short_description = "تعداد محصولات"
    


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "category", "price", "is_active", "created_at" ,
                    "availability_status", "inventory_status" ,"description"]
    list_editable = ["price",]
    list_filter = ["is_active", "category", "created_at",]
    search_fields = ["title__startswith","price",]
    prepopulated_fields = {"slug": ("title",)}
    actions = ['clear_inventory','make_active','make_inactive','export_products_csv']
    autocomplete_fields = ['category',]
    
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

    # custom action
    @admin.action(description="پاک کردن موجودی")
    def clear_inventory(self,request,queryset):
       update = queryset.update(inventory=0)
       self.message_user(
           request,
          f' محصول با موفقیت صفر شد {update}موجودی '
       ) 
       
    
    @admin.action(description="فعال‌سازی محصولات انتخاب‌شده")
    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} محصول با موفقیت فعال شدند.")

    @admin.action(description="غیرفعال‌سازی محصولات انتخاب‌شده")
    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} محصول با موفقیت غیرفعال شدند.")


    @admin.action(description="خروجی CSV از اطلاعات محصولات")
    def export_products_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = 'attachment; filename="products.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['عنوان', 'دسته‌بندی', 'قیمت', 'موجودی', 'وضعیت فعال بودن'])
        
        for product in queryset:
            category_title = product.category.title if product.category else "بدون دسته‌بندی"
            writer.writerow([product.title, category_title, product.price, product.inventory, "فعال" if product.is_active else "غیرفعال"])
            
        return response
    export_products_csv.short_description = "خروجی CSV از اطلاعات محصولات"