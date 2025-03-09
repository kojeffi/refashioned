from django.urls import path
from django.contrib.auth import views as auth_views
from accounts.views import (
    RegisterView,  ActivateAccountView, LoginView, LogoutView, 
    CartView, AddToCartView, OrderHistoryView, OrderDetailView,
    DeleteAccountView, ProfileAPIView, MpesaSTKPushView, CheckoutView,
    MpesaCallbackView,StripePaymentView, PayPalPaymentView, ContactAPIView,FAQListView,FAQDetailView
)

from django.contrib.auth import views as auth_views
from accounts.views import (
    CustomPasswordResetView,
    CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetCompleteView
)
from .views import BlogListCreateView, BlogDetailView, CommentCreateView, CommentListView, RemoveFromCartView, ProductSearchView



urlpatterns = [
    # Authentication APIs 
    path('register/', RegisterView.as_view(), name='api_register'),
    path('login/', LoginView.as_view(), name='api_login'),
    path('logout/', LogoutView.as_view(), name='api_logout'),
    path("activate/<str:uidb64>/<str:token>/", ActivateAccountView.as_view(), name="activate"),
    path('profile/', ProfileAPIView.as_view(), name='profile-api'),
    
    # Cart and Order management
    path('cart/', CartView.as_view(), name='api_cart'),
    path('cart/add/<uuid:uid>/', AddToCartView.as_view(), name='api_add_to_cart'),
    path('api/cart/remove/<str:product_slug>/', RemoveFromCartView.as_view(), name='remove-from-cart'),
    path('orders/', OrderHistoryView.as_view(), name='api_orders'),
    path('orders/<str:order_id>/', OrderDetailView.as_view(), name='api_order_detail'),
    
    # Account deletion
    path('delete-account/', DeleteAccountView.as_view(), name='api_delete_account'),
    
    # Password reset using Django built-in views
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),



    #mpesa
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('mpesa/stk-push/', MpesaSTKPushView.as_view(), name='mpesa_stk_push'),
    path('mpesa/callback/', MpesaCallbackView.as_view(), name='mpesa_callback'),


    #paypal and stripe
    path('payment/stripe/', StripePaymentView.as_view(), name='stripe-payment'),
    path('payment/paypal/', PayPalPaymentView.as_view(), name='paypal-payment'),


    path('contact/', ContactAPIView.as_view(), name='contact-api'),

    path('faqs/', FAQListView.as_view(), name='faq-list'),
    path('faqs/<int:faq_id>/', FAQDetailView.as_view(), name='faq-detail'),



    path('blogs/', BlogListCreateView.as_view(), name='blog-list-create'),
    path('blogs/<int:pk>/', BlogDetailView.as_view(), name='blog-detail'),
    path('blogs/<int:pk>/comments/', CommentListView.as_view(), name='comment-list'),
    path('blogs/<int:pk>/comments/create/', CommentCreateView.as_view(), name='comment-create'),



    path('products/search/', ProductSearchView.as_view(), name='product-search'),


]
