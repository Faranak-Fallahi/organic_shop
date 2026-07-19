from django.contrib import admin
from .models import User, CustomerProfile

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'phone', 'is_staff', ]
    ordering = ['username']
    search_fields = ['username__startswith', 'phone']


@admin.register(CustomerProfile)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['get_username', 'get_phone', 'get_is_staff', 'city']
    ordering = ['user__username']
    search_fields = ['user__username', 'user__phone', 'city']

    @admin.display(description='Username', ordering='user__username')
    def get_username(self, obj):
        return obj.user.username

    @admin.display(description='Phone', ordering='user__phone')
    def get_phone(self, obj):
        return obj.user.phone

    @admin.display(description='Is Staff', boolean=True)
    def get_is_staff(self, obj):
        return obj.user.is_staff
