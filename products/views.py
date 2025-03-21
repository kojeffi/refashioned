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
    
    

class ProductReviewView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, slug):  # Add GET method to fetch reviews
        product = get_object_or_404(Product, slug=slug)
        reviews = ProductReview.objects.filter(product=product)  # Use the ProductReview model
        serializer = ProductReviewSerializer(reviews, many=True)
        return Response({
            "message": "Reviews fetched successfully",
            "result_code": status.HTTP_200_OK,
            "reviews": serializer.data
        })
    
    def post(self, request, slug):  # POST method to add a review
        product = get_object_or_404(Product, slug=slug)
        serializer = ProductReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, product=product)
            return Response({
                "message": "Review added successfully",
                "result_code": status.HTTP_201_CREATED,
                "data": serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


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
        product_uid = request.data.get('product_uid')  # ✅ Changed from product_id to product_uid
        size_name = request.data.get('size_variant')

        product = get_object_or_404(Product, uid=product_uid)  # ✅ Fetch using UID instead of ID
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

    def delete(self, request, product_uid):  # ✅ Changed from product_id to product_uid
        Wishlist.objects.filter(user=request.user, product__uid=product_uid).delete()  # ✅ Use product__uid
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
