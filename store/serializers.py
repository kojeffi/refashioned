from rest_framework import serializers
from .models import Product, Cart, CartItem, Order, OrderItem, Review, Wishlist, BlogPost, FAQ, PolicyPage, Notification, UserProductInteraction, Customer, Transaction, SalesData, UserBehavior, DemandForecast, SearchQuery, AbandonedCart, Preference, SecurityLog, UserInterest, SocialMediaInteraction

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = '__all__'

class BlogPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = '__all__'

class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = '__all__'

class PolicyPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PolicyPage
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class UserProductInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProductInteraction
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

class SalesDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesData
        fields = '__all__'

class UserBehaviorSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBehavior
        fields = '__all__'

class DemandForecastSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemandForecast
        fields = '__all__'

class SearchQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchQuery
        fields = '__all__'

class AbandonedCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = AbandonedCart
        fields = '__all__'

class PreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preference
        fields = '__all__'

class SecurityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityLog
        fields = '__all__'

class UserInterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInterest
        fields = '__all__'

class SocialMediaInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMediaInteraction
        fields = '__all__'

# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from user_app.models import Profile, Message, Subscription

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Profile
        fields = ['user', 'profile_photo', 'about', 'age', 'total_spent', 'purchase_count', 'churn', 'bio', 'interests']

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['user_message', 'bot_response', 'created_at']

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['email', 'subscribed_at']
