from django.contrib import admin
from .models import Cart, CartItem
from django.db.models import Count


class EmptyCartFilter(admin.SimpleListFilter):
    title = 'cart status'
    parameter_name = 'cart_status'

    def lookups(self, request, model_admin):
        return (
            ('empty', 'Empty'),
            ('not_empty', 'Not Empty'),
        )

    def queryset(self, request, queryset):
        queryset = queryset.annotate(items_count=Count('items'))

        if self.value() == 'empty':
            return queryset.filter(items_count=0)

        if self.value() == 'not_empty':
            return queryset.filter(items_count__gt=0)

        return queryset
    
    
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1


@admin.action(description='Delete empty carts')
def delete_empty_carts(modeladmin, request, queryset):
    empty_carts = queryset.annotate(items_count=Count('items')).filter(items_count=0)
    empty_carts.delete()

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at', 'updated_at']
    search_fields = ['user__username', 'user__email']
    inlines = [CartItemInline]
    actions = [delete_empty_carts]
    
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(items_count=Count('items'))

    @admin.display(description='Items Count')
    def items_count(self, obj):
        return obj.items_count
    

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'cart', 'product', 'quantity', 'created_at']
    list_filter = ['created_at']
    search_fields = ['product__title', 'cart__user__username']


    