""" create order """
from django.shortcuts import render
from rest_framework import status, generics
from sales.models import Invoice, SaleItem
from sales.serializers import InvoiceCreationSerializer
from users.permissions import IsPharmacist
# Create your views here.

class InvoiceListCreateAPIView(generics.ListCreateAPIView):
    
    permission_classes = [IsPharmacist]
    serializer_class = InvoiceCreationSerializer
    queryset = Invoice.objects.all()
    

class InvoiceRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsPharmacist]
    serializer_class = InvoiceCreationSerializer
    queryset = Invoice.objects.all()
    

