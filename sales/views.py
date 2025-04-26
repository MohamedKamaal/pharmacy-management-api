
from django.shortcuts import render
from rest_framework import status, generics
from sales.models import Invoice, SaleItem
from sales.serializers import InvoiceCreationSerializer, ReturnInvoiceSerializer
<<<<<<< HEAD
from users.permissions import IsPharmacist
=======
from users.permissions import IsCashier
>>>>>>> code_refactoing
from django_filters.rest_framework import DjangoFilterBackend
from sales.filters import InvoiceFilter
from rest_framework.views import APIView
from rest_framework.response import Response
# Create your views here.

class InvoiceListCreateAPIView(generics.ListCreateAPIView):
    
    permission_classes = [IsCashier]
    queryset = Invoice.objects.filter(payment_status="paid")
    serializer_class = InvoiceCreationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = InvoiceFilter
    
    

<<<<<<< HEAD
=======
class InvoiceRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsCashier]
    queryset = Invoice.objects.all()
    serializer_class = InvoiceCreationSerializer

    

>>>>>>> code_refactoing
class ReturnInvoiceAPIView(APIView):
    def post(self, request):
        """Return invoice (mark as refunded)."""
        serializer = ReturnInvoiceSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            invoice = serializer.validated_data['invoice']
            
            # Update the payment status to 'refunded'
            invoice.payment_status = 'refunded'
            invoice.save()

            # Optionally, handle any necessary logic for stock adjustment, etc.
            # For example, reverting stock changes made during the sale.
            
            return Response(
                {"message": f"Invoice #{invoice.pk} refunded successfully."},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)