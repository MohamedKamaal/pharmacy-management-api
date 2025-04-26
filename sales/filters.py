"""
FilterSet for filtering invoices based on creation date.

This module defines a Django FilterSet for filtering Invoice objects by various
date-related criteria, such as exact date, date range, month, and year.
"""

import django_filters
from sales.models import Invoice


class InvoiceFilter(django_filters.FilterSet):
    """
    FilterSet for filtering Invoice objects.

    Provides filters for filtering invoices by creation date, including exact date,
    date range (greater than or equal to, less than or equal to), month, and year.
    """
    created__gte = django_filters.DateFilter(
        field_name='created',
        lookup_expr='gte',
        label='Created after or on (YYYY-MM-DD)'
    )
    created__lte = django_filters.DateFilter(
        field_name='created',
        lookup_expr='lte',
        label='Created before or on (YYYY-MM-DD)'
    )
    created = django_filters.DateFilter(
        field_name='created',
        lookup_expr='exact',
        label='Exact date (YYYY-MM-DD)'
    )
    created__month = django_filters.NumberFilter(
        field_name='created',
        lookup_expr='month',
        label='Month (1-12)'
    )
    created__year = django_filters.NumberFilter(
        field_name='created',
        lookup_expr='year',
        label='Year (YYYY)'
    )

    class Meta:
        """Metadata for the InvoiceFilter."""
        model = Invoice
        fields = [
            'created',
            'created__gte',
            'created__lte',
            'created__month',
            'created__year',
        ]