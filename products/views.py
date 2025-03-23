# Views
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.urls import path
from .models import Category, Product, ProductReview, Wishlist, SizeVariant

from rest_framework import serializers
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.permissions import AllowAny
from products.serializers import CategorySerializer, ProductSerializer, ProductReviewSerializer, WishlistSerializer,RelatedProductSerializer
class CategoryListView(APIView):
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response({
            "message": "Categories retrieved successfully",
            "result_code": status.HTTP_200_OK,
            "data": serializer.data
        })

class ProductListView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        products = Product.objects.prefetch_related("product_images").all()  # ✅ Optimized DB query
        serializer = ProductSerializer(products, many=True, context={"request": request})  # ✅ Pass request context
        return Response({
            "message": "Products retrieved successfully",
            "result_code": status.HTTP_200_OK,
            "data": serializer.data
        })

class ProductDetailView(APIView):
    def get(self, request, slug):
        product = get_object_or_404(Product.objects.prefetch_related("product_images"), slug=slug)  # ✅ Optimize DB query
        serializer = ProductSerializer(product, context={"request": request})  # ✅ Pass request
        return Response({
            "message": "Product details retrieved",
            "result_code": status.HTTP_200_OK,
            "data": serializer.data
        })
    
import uuid

class ProductReviewView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductReviewSerializer

    def get(self, request, slug):
        # Fetch reviews for the specified product using the slug
        product = get_object_or_404(Product, slug=slug)
        reviews = ProductReview.objects.filter(product=product)
        serializer = ProductReviewSerializer(reviews, many=True)
        return Response({
            "message": "Reviews retrieved successfully",
            "data": serializer.data,
        }, status=status.HTTP_200_OK)

    def post(self, request, slug):
        user = request.user  # Get authenticated user
        content = request.data.get('content', '').strip()  # Get review content
        stars = request.data.get('stars', 5)  # Get stars, default to 5 if not provided

        # Fetch product instance using the slug
        product = get_object_or_404(Product, slug=slug)

        # Create a new review
        review = ProductReview.objects.create(
            user=user,
            product=product,
            content=content,
            stars=stars
        )

        # Serialize the review
        serializer = ProductReviewSerializer(review)

        return Response(
            {
                "message": "Review created successfully",
                "data": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


class LikeReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, review_id):
        try:
            review_uuid = uuid.UUID(review_id)  # Convert review_id to UUID
        except ValueError:
            return Response({"detail": "Invalid review ID format."}, status=status.HTTP_400_BAD_REQUEST)

        review = get_object_or_404(ProductReview, id=review_uuid)
        user = request.user

        if user in review.likes.all():
            review.likes.remove(user)  # Unlike
        else:
            review.likes.add(user)  # Like
            review.dislikes.remove(user)  # Remove dislike if present

        return Response({
            "message": "Like toggled successfully",
            "like_count": review.likes.count(),
            "dislike_count": review.dislikes.count(),
        }, status=status.HTTP_200_OK)

class DislikeReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, review_id):
        try:
            review_uuid = uuid.UUID(review_id)  # Convert review_id to UUID
        except ValueError:
            return Response({"detail": "Invalid review ID format."}, status=status.HTTP_400_BAD_REQUEST)

        review = get_object_or_404(ProductReview, id=review_uuid)
        user = request.user

        if user in review.dislikes.all():
            review.dislikes.remove(user)  # Remove dislike
        else:
            review.dislikes.add(user)  # Dislike
            review.likes.remove(user)  # Remove like if present

        return Response({
            "message": "Dislike toggled successfully",
            "like_count": review.likes.count(),
            "dislike_count": review.dislikes.count(),
        }, status=status.HTTP_200_OK)
    

class WishlistView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        wishlist = Wishlist.objects.filter(user=request.user)
        serializer = WishlistSerializer(wishlist, many=True)
        return Response({
            "message": "Wishlist retrieved successfully",
            "result_code": status.HTTP_200_OK,
            "data": serializer.data
        })
    
    def post(self, request):
        product_uid = request.data.get('product_uid')  # Ensure product_uid is passed
        size_name = request.data.get('size_variant')

        try:
            product_uuid = uuid.UUID(product_uid)  # Convert product_uid to UUID
        except ValueError:
            return Response({"detail": "Invalid product ID format."}, status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(Product, uid=product_uuid)  # Fetch using UUID
        size_variant = get_object_or_404(SizeVariant, size_name=size_name) if size_name else None

        wishlist, created = Wishlist.objects.get_or_create(
            user=request.user, 
            product=product, 
            size_variant=size_variant
        )

        return Response({
            "message": "Added to wishlist" if created else "Already in wishlist",
            "result_code": status.HTTP_201_CREATED,
            "data": {}
        })

    def delete(self, request, product_uid):  # Ensure product_uid is passed
        try:
            product_uuid = uuid.UUID(product_uid)  # Convert product_uid to UUID
        except ValueError:
            return Response({"detail": "Invalid product ID format."}, status=status.HTTP_400_BAD_REQUEST)

        Wishlist.objects.filter(user=request.user, product__uid=product_uuid).delete()  # Use product__uid
        return Response({
            "message": "Removed from wishlist",
            "result_code": status.HTTP_204_NO_CONTENT,
            "data": {}
        })
    



#related Products
class RelatedProductsView(APIView):
    def get(self, request, slug):
        product = get_object_or_404(Product, slug=slug)  # Use slug to fetch product
        related_products = Product.objects.filter(
            category=product.category
        ).exclude(uid=product.uid).order_by("-newest_product")[:5]  # Use uid instead of id
        
        serializer = RelatedProductSerializer(related_products, many=True, context={"request": request})

        return Response({
            "message": "Related products retrieved successfully",
            "result_code": status.HTTP_200_OK,
            "data": serializer.data
        })
