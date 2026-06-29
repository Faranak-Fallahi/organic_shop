from django.contrib import admin,messages
from .models import PostComment ,ProductComment


class CommentAdminBase(admin.ModelAdmin):
    actions = ["make_active", "make_inactive"]

    # custom action
    @admin.action(description="فعال‌سازی کامنت‌های انتخاب شده")
    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} کامنت فعال شد")

    @admin.action(description="غیرفعال‌سازی کامنت‌های انتخاب شده")
    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} کامنت غیرفعال شد")
        
     # computed fields   
    def replies_count(self, obj):
        return obj.replies.count()
    replies_count.short_description = "تعداد پاسخ‌ها"


@admin.register(PostComment)
class PostCommentAdmin(CommentAdminBase):
    list_display = ["user", "post", "is_active", "created_at", "replies_count"]
    list_filter = ["is_active", "post", "created_at",]
    search_fields = ["user__username", "post__title", "body"]
    autocomplete_fields = ['post',]
    
    
    
@admin.register(ProductComment)
class ProductCommentAdmin(CommentAdminBase):
    list_display = ["user", "product", "is_active", "created_at", "replies_count"]
    list_filter = ["is_active", "product", "created_at",]
    search_fields = ["user__username", "product__title", "body"]
    autocomplete_fields = ['product',]
    
    
    
    
  