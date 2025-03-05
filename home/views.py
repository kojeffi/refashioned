from django.db.models import Q
from django.shortcuts import render
from products.models import Product, Category
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import ShippingAddress
from .serializers import ShippingAddressSerializer

class ShippingAddressListCreateView(APIView):
    """
    API view to list all shipping addresses and create a new one.
    """

    def get(self, request):
        addresses = ShippingAddress.objects.all()
        serializer = ShippingAddressSerializer(addresses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ShippingAddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ShippingAddressDetailView(APIView):
    """
    API view to retrieve, update, or delete a shipping address.
    """

    def get(self, request, pk):
        address = get_object_or_404(ShippingAddress, pk=pk)
        serializer = ShippingAddressSerializer(address)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        address = get_object_or_404(ShippingAddress, pk=pk)
        serializer = ShippingAddressSerializer(address, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        address = get_object_or_404(ShippingAddress, pk=pk)
        address.delete()
        return Response({"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
