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
    """
    API view that returns a list of medicine batches that are completely out of stock.

    Permissions:
        - Only pharmacists and admins are allowed to access this endpoint.

    Returns:
        - A list of serialized `Batch` objects where `stock_units` is 0.
    """
    permission_classes = [IsPharmacistOnly]
    serializer_class = BatchOutSerializer
    queryset = Batch.objects.filter(stock_units=0)


class ExpiredAPIView(ListAPIView):
    """
    API view that returns a list of medicine batches that have already expired.

    Permissions:
        - Only pharmacists and admins can access this view.

    Returns:
        - A list of serialized `Batch` objects where the `expiry_date` is on or before today.
    """
    permission_classes = [IsPharmacistOnly]
    serializer_class = BatchOutSerializer
    queryset = Batch.objects.filter(expiry_date__lte=now().date())


class NearExpireAPIView(ListAPIView):
    """
    API view that returns a list of medicine batches that are near expiry.

    Definition of 'near expiry':
        - Batches with expiry dates between today and a future date,
          defined by the `months` query parameter (default: 1 month).

    Permissions:
        - Only accessible by pharmacists and admins.

    Query Parameters:
        - `months`: Integer, optional (default=1).
            Number of months ahead to consider for near-expiry detection.
            Must be a non-negative integer.

    Returns:
        - A filtered queryset of serialized `Batch` objects meeting the near-expiry condition.
    """
    permission_classes = [IsPharmacistOnly]
    serializer_class = BatchOutSerializer

    def get_queryset(self):
        months = self.request.query_params.get('months', 1)

        try:
            months = int(months)
            if months < 0:
                raise ValidationError("Months parameter must be a positive integer.")
        except ValueError:
            raise ValidationError("Invalid value for 'months'. It must be an integer.")

        return Batch.objects.filter(
            expiry_date__gte=now().date(),
            expiry_date__lte=now().date() + relativedelta(months=months)
        )
