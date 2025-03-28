""" create order """
from django.shortcuts import render
from rest_framework import status, generics
from orders.models import Order, OrderItem
from orders.serializers import OrderCreationSerializer
from users.permissions import IsPharmacist
# Create your views here.

class OrderListCreateAPIView(generics.ListCreateAPIView):
    
    permission_classes = [IsPharmacist]
    serializer_class = OrderCreationSerializer
    queryset = Order.objects.all()
    

class OrderRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsPharmacist]
    serializer_class = OrderCreationSerializer
    queryset = Order.objects.all()
    

