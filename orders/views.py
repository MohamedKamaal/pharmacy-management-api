"""
Order API Views

Defines views for order-related API endpoints.
"""

from rest_framework import status, generics
from orders.models import Order
from orders.serializers import OrderCreationSerializer, OrderReadSerializer
from users.permissions import IsPharmacist
from django_filters.rest_framework import DjangoFilterBackend
from orders.filters import OrderFilter
from rest_framework import permissions


class OrderListCreateAPIView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating orders.
    
    Features:
    - Pharmacist permission required
    - Date filtering capabilities
    - Different serializers for read vs write operations
    """
    permission_classes = [IsPharmacist]
    queryset = Order.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrderFilter
    
    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return OrderReadSerializer
        return OrderCreationSerializer


class OrderRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating and deleting individual orders.
    
    Features:
    - Pharmacist permission required
    - Different serializers for read vs write operations
    - Complete replacement of order items on update
    """
    permission_classes = [IsPharmacist]
    queryset = Order.objects.all()
    
    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return OrderReadSerializer
        return OrderCreationSerializer