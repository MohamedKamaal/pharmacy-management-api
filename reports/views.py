from django.shortcuts import render
from rest_framework import status, generics
from sales.models import Invoice, SaleItem
from sales.serializers import InvoiceCreationSerializer
from users.permissions import IsPharmacistOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from medicine.serializers import BatchOutSerializer
from medicine.models import Batch
from django.utils.timezone import now
from rest_framework.exceptions import ValidationError
from dateutil.relativedelta import relativedelta  # Add this import

class OutOfStockAPIView(ListAPIView):
    """ return out of stock batches """
    permission_classes = [ IsPharmacistOnly] 
    serializer_class = BatchOutSerializer
    queryset = Batch.objects.filter(
      stock_units = 0 
    )

class ExpiredAPIView(ListAPIView):
    """ return out of stock batches """
    permission_classes = [IsPharmacistOnly] 
    serializer_class = BatchOutSerializer
    queryset = Batch.objects.filter(
      expiry_date__lte=now().date()
    )

class NearExpireAPIView(ListAPIView):
    """ Return batches that are near expiry (within a specified number of months) """
    permission_classes = [IsPharmacistOnly] 
    serializer_class = BatchOutSerializer
    
    def get_queryset(self):
        # Get the number of months from the query parameters (default is 1 month)
        months = self.request.query_params.get('months', 1)
        
        try:
            months = int(months)
            if months < 0:
                raise ValidationError("Months parameter must be a positive integer.")
        except ValueError:
            raise ValidationError("Invalid value for 'months'. It must be an integer.")
        
        # Filter batches where expiry date is between today and the specified months from now
        return Batch.objects.filter(
            expiry_date__gte=now().date(),
            expiry_date__lte=now().date()  + relativedelta(months=months)
        )