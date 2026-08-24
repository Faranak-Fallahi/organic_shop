from django.contrib import admin
from .models import Branch


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("title", "phone", "whatsapp", "is_active", "order")
    list_filter = ("is_active",)
    search_fields = ("title", "address", "phone")
    list_editable = ("is_active", "order")
