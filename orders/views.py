""" create order """
from django.shortcuts import render
from rest_framework import status, generics
from orders.models import Order, OrderItem
from orders.serializers import OrderCreationSerializer, OrderReadSerializer
from users.permissions import IsPharmacist
from django_filters.rest_framework import DjangoFilterBackend
from orders.filters import OrderFilter
from rest_framework import permissions


# Create your views here.

class OrderListCreateAPIView(generics.ListCreateAPIView):
    
    permission_classes = [IsPharmacist]
    queryset = Order.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrderFilter
    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return OrderReadSerializer
        return OrderCreationSerializer
    

class OrderRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsPharmacist]
    queryset = Order.objects.all()
    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return OrderReadSerializer
        return OrderCreationSerializer
    

