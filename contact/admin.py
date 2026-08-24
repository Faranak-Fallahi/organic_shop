from django.contrib import admin
from .models import Branch


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("title", "phone", "whatsapp", "is_active", "order")
    list_filter = ("is_active",)
    search_fields = ("title", "address", "phone")
    list_editable = ("is_active", "order")

from django.contrib import admin
from .models import AboutPage, AboutFeature, AboutCategory


class AboutFeatureInline(admin.TabularInline):
    model = AboutFeature
    extra = 1
    ordering = ("order", "id")


class AboutCategoryInline(admin.TabularInline):
    model = AboutCategory
    extra = 1
    ordering = ("order", "id")


@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    inlines = [
        AboutFeatureInline,
        AboutCategoryInline,
    ]

    fieldsets = (
        (
            "بنر بالای صفحه",
            {
                "fields": (
                    "hero_title",
                    "hero_subtitle",
                )
            }
        ),
        (
            "اطلاعات برند",
            {
                "fields": (
                    "brand_name",
                    "brand_description",
                    "logo",
                )
            }
        ),
        (
            "داستان برند",
            {
                "fields": (
                    "story_title",
                    "story_text_1",
                    "story_text_2",
                )
            }
        ),
        (
            "بخش محصولات",
            {
                "fields": (
                    "products_title",
                    "products_description",
                )
            }
        ),
    )

    def has_add_permission(self, request):
        return not AboutPage.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
