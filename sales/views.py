""" create order """
from django.shortcuts import render
from rest_framework import status, generics
from sales.models import Invoice, SaleItem
from sales.serializers import InvoiceCreationSerializer
from users.permissions import IsPharmacist
from django_filters.rest_framework import DjangoFilterBackend
from orders.filters import InvoiceFilter
# Create your views here.

class InvoiceListCreateAPIView(generics.ListCreateAPIView):
    
    permission_classes = [IsPharmacist]
    serializer_class = InvoiceCreationSerializer
    queryset = Invoice.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = InvoiceFilter
    

class InvoiceRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsPharmacist]
    serializer_class = InvoiceCreationSerializer
    queryset = Invoice.objects.all()
    

