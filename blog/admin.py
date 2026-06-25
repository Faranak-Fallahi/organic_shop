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
    list_display = ['title','created_at','published']
    list_filter = ['created_at', PublishedFilter ]
    
    
    
    

    