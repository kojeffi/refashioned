from django.urls import path
from home.views import *

urlpatterns = [
    path('shipping-addresses/', ShippingAddressListCreateView.as_view(), name='shipping-address-list'),
    path('shipping-addresses/<int:pk>/', ShippingAddressDetailView.as_view(), name='shipping-address-detail'),
]
