from django.contrib import admin
from .models import Post

# custom filtering
class PublishedFilter(admin.SimpleListFilter):
        IS_PUBLISHED = 'yes'
        IS_NOT_PUBLISHED = 'no'
        title = 'وضعیت انتشار'
        parameter_name = 'published'

        def lookups(self, request, model_admin):
            return (
                (PublishedFilter.IS_PUBLISHED,'منتشر شده'),
                (PublishedFilter.IS_NOT_PUBLISHED,'منتشر نشده'),
            )

        def queryset(self, request, queryset):
            if self.value() == 'yes':
                return queryset.filter(published=True)

            if self.value() == 'no':
                return queryset.filter(published=False)

            return queryset
    


    
    
    
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title','created_at','published',]
    list_filter = ['created_at', PublishedFilter ,]
    search_fields = ["title__startswith",]
    prepopulated_fields = {"slug": ("title",)}
    actions = ['make_published','make_draft',]
   
    
    # custom action   
    @admin.action(description="انتشار پست‌های انتخاب‌شده")
    def make_published(self, request, queryset):
        updated = queryset.update(published=True)  # اگر فیلد Boolean دارید
        self.message_user(request, f"{updated} پست با موفقیت منتشر شدند.")

    @admin.action(description="انتقال به پیش‌نویس")
    def make_draft(self, request, queryset):
        updated = queryset.update(published=False)
        self.message_user(request, f"{updated} پست به پیش‌نویس منتقل شدند.")
        