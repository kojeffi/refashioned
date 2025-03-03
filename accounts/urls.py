from django.urls import path
from django.contrib.auth import views as auth_views
from accounts.views import (
    RegisterView,  ActivateAccountView, LoginView, LogoutView, 
    CartView, AddToCartView, OrderHistoryView, OrderDetailView,
    DeleteAccountView, ProfileAPIView, MpesaSTKPushView, MpesaCallbackView
)

from django.contrib.auth import views as auth_views
from accounts.views import (
    CustomPasswordResetView,
    CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetCompleteView
)


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
    path('mpesa/stk-push/', MpesaSTKPushView.as_view(), name='mpesa_stk_push'),
    path('mpesa/callback/', MpesaCallbackView.as_view(), name='mpesa_callback'),


]
