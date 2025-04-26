"""
API views for managing invoices and sale items.

This module defines API views for listing, creating, retrieving, updating,
deleting, and returning invoices. Views are restricted to users with cashier
permissions.
"""

from django.shortcuts import render
from rest_framework import status, generics
from sales.models import Invoice, SaleItem
from sales.serializers import InvoiceCreationSerializer, ReturnInvoiceSerializer
from users.permissions import IsCashier
from django_filters.rest_framework import DjangoFilterBackend
from sales.filters import InvoiceFilter
from rest_framework.views import APIView
from rest_framework.response import Response


class InvoiceListCreateAPIView(generics.ListCreateAPIView):
    """
    API view for listing and creating invoices.

    Lists all paid invoices and allows creating new invoices. Supports filtering
    by creation date using InvoiceFilter.
    """
    permission_classes = [IsCashier]
    queryset = Invoice.objects.filter(payment_status="paid")
    serializer_class = InvoiceCreationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = InvoiceFilter


class InvoiceRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting invoices.

    Allows cashiers to retrieve, update, or delete a specific invoice by ID.
    """
    permission_classes = [IsCashier]
    queryset = Invoice.objects.all()
    serializer_class = InvoiceCreationSerializer


class ReturnInvoiceAPIView(APIView):
    """
    API view for returning (refunding) an invoice.

    Marks an invoice as refunded and updates related stock quantities.
    """
    def post(self, request):
        """Return invoice (mark as refunded)."""
        serializer = ReturnInvoiceSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            invoice = serializer.validated_data['invoice']
            invoice.payment_status = 'refunded'
            invoice.save()
            return Response(
                {"message": f"Invoice #{invoice.pk} refunded successfully."},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)