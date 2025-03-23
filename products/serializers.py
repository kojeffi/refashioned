from rest_framework import serializers
from django.conf import settings
from .models import Product, ProductImage, Category, ProductReview, Wishlist

class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None  # Return None if request is not available or image is missing

    class Meta:
        model = ProductImage
        fields = ["image_url"]


        

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    product_images = ProductImageSerializer(many=True, read_only=True)  # ✅ Fixed: Added related images

    class Meta:
        model = Product
        fields = [
            "uid", "product_name", "slug", "price", "product_description",  # ⚠️ Rename in model if necessary
            "newest_product", "category", "product_images"
        ]


class ProductReviewSerializer(serializers.ModelSerializer):
    like_count = serializers.SerializerMethodField()
    dislike_count = serializers.SerializerMethodField()

    class Meta:
        model = ProductReview
        fields = ["id", "user", "product", "content", "stars", "date_added", "like_count", "dislike_count"]

    def get_like_count(self, obj):
        return obj.like_count()

    def get_dislike_count(self, obj):
        return obj.dislike_count()

class WishlistSerializer(serializers.ModelSerializer):
    # Nested serializers for related fields
    product = ProductSerializer(read_only=True)  # Serialize the related Product

    class Meta:
        model = Wishlist
        fields = [
            "uid",  # Include the Wishlist ID
            "user",  # Include the user (you might want to exclude this in some cases)
            "product",  # Include the nested product details
            "added_on",  # Include the timestamp
        ]
        read_only_fields = ["uid", "added_on"]  # These fields are read-only

    # Optional: If you want to include the user's email in the response
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["user"] = instance.user.email  # Add the user's email to the response
        return representation
    


class RelatedProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    product_images = ProductImageSerializer(many=True)

    class Meta:
        model = Product
        fields = ["uid", "product_name", "slug", "price", "product_description", "newest_product", "category", "product_images"]

