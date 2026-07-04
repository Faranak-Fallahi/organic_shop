from . import models
from django.contrib import admin


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display =["username", "phone",] 
    ordering = ["username",]
    search_fields = ["username__startswith","phone",]
    

