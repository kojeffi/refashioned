from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile, Cart, CartItem, Order, OrderItem


from django.contrib.auth.forms import AuthenticationForm
from django import forms

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email")

admin.site.login_form = CustomAuthenticationForm


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AdminAuthenticationForm
from django.contrib.admin.sites import AdminSite
from .forms import EmailAuthenticationForm

CustomUser = get_user_model()

class CustomAdminSite(AdminSite):
    login_form = EmailAuthenticationForm

admin.site = CustomAdminSite()
admin.site.register(CustomUser, UserAdmin)

class CustomUserAdmin(UserAdmin):
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
