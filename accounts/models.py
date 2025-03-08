from django.db import models
from django.conf import settings
import os
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from base.models import BaseModel
from products.models import Product, ColorVariant, SizeVariant, Coupon
from home.models import ShippingAddress
import uuid
from cloudinary.models import CloudinaryField

from django.db import models
from rest_framework import serializers, status
from django.shortcuts import get_object_or_404
from django.urls import path
from .models import Product 


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)  # Ensure superuser is active

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


from django.core.exceptions import ObjectDoesNotExist

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

    @property
    def profile(self):
        """Ensure Profile is created if it does not exist"""
        profile, created = Profile.objects.get_or_create(user=self)
        return profile


class Profile(BaseModel):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="profile")
    is_email_verified = models.BooleanField(default=False)
    email_token = models.CharField(default=uuid.uuid4, max_length=36, unique=True, editable=False)
    profile_image = CloudinaryField('image', null=True, blank=True)  # ✅ Using CloudinaryField
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    shipping_address = models.ForeignKey(
        ShippingAddress, on_delete=models.SET_NULL, related_name="shipping_addresses", null=True, blank=True
    )

    def __str__(self):
        return self.user.email

    def get_cart_count(self):
        return CartItem.objects.filter(cart__is_paid=False, cart__user=self.user).count()

class Cart(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="cart", null=True, blank=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    mpesa_transaction_id = models.CharField(max_length=100, null=True, blank=True)
    stripe_payment_id = models.CharField(max_length=100, null=True, blank=True)
    paypal_payment_id = models.CharField(max_length=100, null=True, blank=True)

    def get_cart_total(self):
        cart_items = self.cart_items.all()
        return sum(cart_item.get_product_price() for cart_item in cart_items)

    def get_cart_total_price_after_coupon(self):
        total = self.get_cart_total()
        if self.coupon and total >= self.coupon.minimum_amount:
            total -= self.coupon.discount_amount
        return total


class CartItem(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    color_variant = models.ForeignKey(ColorVariant, on_delete=models.SET_NULL, null=True, blank=True)
    size_variant = models.ForeignKey(SizeVariant, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=1)

    def get_product_price(self):
        price = self.product.price * self.quantity if self.product else 0
        if self.color_variant:
            price += self.color_variant.price
        if self.size_variant:
            price += self.size_variant.price
        return price


class Order(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="orders")
    order_id = models.CharField(max_length=100, unique=True)
    order_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=100)
    shipping_address = models.TextField(blank=True, null=True)
    payment_mode = models.CharField(max_length=100)
    order_total_price = models.DecimalField(max_digits=10, decimal_places=2)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)
    mpesa_transaction_id = models.CharField(max_length=100, null=True, blank=True)
    stripe_payment_id = models.CharField(max_length=100, null=True, blank=True)
    paypal_payment_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Order {self.order_id} by {self.user.email}"

    def get_order_total_price(self):
        return self.order_total_price


class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    size_variant = models.ForeignKey(SizeVariant, on_delete=models.SET_NULL, null=True, blank=True)
    color_variant = models.ForeignKey(ColorVariant, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    product_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    def __str__(self):
        return f"{self.product.product_name if self.product else 'Unknown'} - {self.quantity}"

    def get_total_price(self):
        return self.product_price * self.quantity if self.product_price else 0

# Contact Model
class Contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question




from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Blog(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    cover_image = models.ImageField(upload_to='blog_images/')
    brief = models.TextField()
    content = models.TextField()
    tag = models.ForeignKey(Tag, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Comment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.email} on {self.blog.title}"