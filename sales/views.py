""" create order """
from django.shortcuts import render
from rest_framework import status, generics
from sales.models import Invoice, SaleItem
from sales.serializers import InvoiceCreationSerializer, ReturnInvoiceSerializer
from users.permissions import IsPharmacist
from django_filters.rest_framework import DjangoFilterBackend
from sales.filters import InvoiceFilter
from rest_framework.views import APIView
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
    

class ReturnInvoiceAPIView(APIView):
    def post(self, request, invoice_id):
        """ return invoice """
        serializer = ReturnInvoiceSerializer(invoice_id)
        serializer.is_valid(raise_Exception=True)
        invoice = serializer.data
        invoice.payment_status == "refunded"
        invoice.save()