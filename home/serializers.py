from rest_framework import serializers
from .models import ShippingAddress

class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = ['user', 'first_name', 'last_name', 'address', 'street', 'street_number', 'zip_code', 'city', 'country', 'phone', 'current_address']
