from rest_framework import serializers
from django.contrib.auth import get_user_model
from accounts.models import Profile, Cart, CartItem, Order, OrderItem, Contact,FAQ
from home.models import ShippingAddress
from products.models import Product, SizeVariant

CustomUser = get_user_model()  # Ensures compatibility with custom user models


# ✅ User Serializer
class UserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'password', 'confirm_password', 'is_active']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        """Ensure passwords match"""
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords must match."})
        return data

    def create(self, validated_data):
        """Create user and ensure Profile is created"""
        validated_data.pop('confirm_password')
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )

        # Ensure profile is created
        Profile.objects.get_or_create(user=user)
        return user


# ✅ Profile Serializer
class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Now allows updates

    class Meta:
        model = Profile
        fields = ['user', 'phone_number', 'profile_image', 'bio', 'shipping_address', 'is_email_verified', 'email_token']

    def update(self, instance, validated_data):
        """Allow updating user details along with profile"""
        user_data = validated_data.pop('user', None)
        if user_data:
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save()

        return super().update(instance, validated_data)


# ✅ CartItem Serializer
# ✅ OrderItem Serializer
class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    size_name = serializers.ReadOnlyField(source='size_variant.size_name')

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'product_name', 'size_variant', 'size_name', 'quantity', 'price']


# ✅ Order Serializer
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True, source='orderitem_set')

    class Meta:
        model = Order
        fields = ['id', 'user', 'order_id', 'items', 'order_date', 'status', 'total_price']


# ✅ Shipping Address Serializer
class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = ['id', 'user', 'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country']


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'  

# Contact Serializer
class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'

class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = '__all__'

