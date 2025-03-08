from rest_framework import serializers
from django.contrib.auth import get_user_model
from accounts.models import Profile, Cart, CartItem, Order, OrderItem, Contact, FAQ
from home.models import ShippingAddress
from products.models import Product, SizeVariant, ColorVariant, Category, ProductImage, Coupon, ProductReview, Wishlist

CustomUser = get_user_model()

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'password', 'confirm_password', 'is_active']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords must match."})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        Profile.objects.get_or_create(user=user)
        return user

# Profile Serializer
class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Profile
        fields = ['user', 'phone_number', 'profile_image', 'bio', 'shipping_address', 'is_email_verified', 'email_token']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save()
        return super().update(instance, validated_data)

# Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category_name', 'slug', 'category_image']

# Product Image Serializer
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['image']

# Product Serializer
class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, source='product_images', read_only=True)

    class Meta:
        model = Product
        fields = ['product_name', 'slug', 'category', 'price', 'product_description', 'newest_product', 'images']

# Size Variant Serializer
class SizeVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = SizeVariant
        fields = ['size_name', 'price']

# Color Variant Serializer
class ColorVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColorVariant
        fields = ['color_name', 'price']

# Cart Item Serializer
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = CartItem
        fields = ['product', 'quantity', 'size_variant', 'color_variant']

# Cart Serializer
class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True)

    class Meta:
        model = Cart
        fields = ['user', 'is_paid', 'cart_items']

# Order Item Serializer
class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    size_variant = SizeVariantSerializer()

    class Meta:
        model = OrderItem
        fields = [ 'order', 'product', 'size_variant', 'quantity', 'price']

# Order Serializer
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True, source='orderitem_set')

    class Meta:
        model = Order
        fields = [ 'user', 'order_id', 'items', 'order_date', 'status', 'total_price']

# Coupon Serializer
class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['coupon_code', 'is_expired', 'discount_amount', 'minimum_amount']

# Product Review Serializer
class ProductReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = [ 'product', 'user', 'likes', 'dislikes', 'stars', 'content', 'date_added']

# Wishlist Serializer
class WishlistSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = Wishlist
        fields = ['user', 'product', 'size_variant', 'added_on']

# Contact Serializer
class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'

# FAQ Serializer
class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = '__all__'
