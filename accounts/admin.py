from django.contrib import admin
from django.contrib.auth.admin import BaseUserAdmin
from .models import CustomUser, Profile, Cart, CartItem, Order, OrderItem

class CustomUserAdmin(BaseUserAdmin):
    model = CustomUser
    list_display = ("email", "first_name", "last_name", "is_staff", "is_active", "is_superuser")
    list_filter = ("is_staff", "is_active", "is_superuser")
    
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser")}),
        ("Important Dates", {"fields": ("last_login",)}),
    )
    
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "is_staff", "is_active", "is_superuser"),
        }),
    )
    
    search_fields = ("email",)
    ordering = ("email",)

# Register CustomUser in Django Admin
admin.site.register(CustomUser, CustomUserAdmin)



# ✅ Register other models
admin.site.register(Profile)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
