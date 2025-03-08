from rest_framework import serializers
from django.conf import settings
from .models import Product, ProductImage, Category, ProductReview, Wishlist

class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    def get_image_url(self, obj):
        request = self.context.get("request")  
        if obj.image:
            return request.build_absolute_uri(obj.image.url)  
        return None

    class Meta:
        model = ProductImage
        fields = ["image_url"]  # ✅ Fixed: Returning full URL


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    product_image = serializers.SerializerMethodField()  # ✅ Fetch first image
    product_images = ProductImageSerializer(many=True, read_only=True)  # ✅ All images

    class Meta:
        model = Product
        fields = [
            "uid", "product_name", "slug", "price", "product_description",
            "newest_product", "category", "product_image", "product_images"
        ]

    def get_product_image(self, obj):
        """Retrieve the first product image URL if available"""
        image = obj.product_images.first()  # Get the first image
        return image.image.url if image else None  # Return URL if image exists



class ProductReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = '__all__'


class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = '__all__'


class RelatedProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "product_name", "price", "slug"]

