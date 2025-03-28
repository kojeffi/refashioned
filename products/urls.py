from django.urls import path
from products.views import *

# urlpatterns = [
    # path('wishlist/', wishlist_view, name='wishlist'),
    # path('wishlist/add/<uid>/', add_to_wishlist, name='add_to_wishlist'),
    # path('wishlist/move_to_cart/<uid>/', move_to_cart, name='move_to_cart'),
    # path('wishlist/remove/<uid>/', remove_from_wishlist, name='remove_from_wishlist'),
    # path('product-reviews/', product_reviews, name='product_reviews'),
    # path('product-reviews/edit/<uuid:review_uid>/', edit_review, name='edit_review'),
    # path('like-review/<review_uid>/', like_review, name='like_review'),
    # path('dislike-review/<review_uid>/',dislike_review, name='dislike_review'),
    # path('<slug>/', get_product, name='get_product'),
    # path('<slug>/<review_uid>/delete/', delete_review, name='delete_review'),
# ]
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.urls import path
from .models import Category, Product, ProductReview, Wishlist, SizeVariant
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<slug:slug>/', ProductDetailView.as_view(), name='product-detail'),
    path('products/<slug:slug>/reviews/', ProductReviewView.as_view(), name='product-reviews'),
    path('wishlist/', WishlistView.as_view(), name='wishlist'),
    path('wishlist/<uuid:product_uid>/', WishlistView.as_view(), name='wishlist-delete'),
    path('products/<slug:slug>/related/', RelatedProductsView.as_view(), name='related-products'),


    path('reviews/<uuid:review_id>/like/', LikeReviewView.as_view(), name='like-review'),
    path('reviews/<uuid:review_id>/dislike/', DislikeReviewView.as_view(), name='dislike-review'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

