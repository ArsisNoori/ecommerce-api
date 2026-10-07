from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User
# Register your models here.

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (('Shop',{'fields':('phone_number', 'is_seller')}),)
    list_display = ('username', 'email', 'is_seller', 'is_staff')
    list_filter = UserAdmin.list_filter + ('is_seller',)
