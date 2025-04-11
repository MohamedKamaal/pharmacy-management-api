import django_filters
from orders.models import Order
from django.db import models

class OrderFilter(django_filters.FilterSet):
    # Date range filters
    created_at_gte = django_filters.DateFilter(
        field_name='created_at', 
        lookup_expr='gte',
        label='Created after or on (YYYY-MM-DD)'
    )
    created_at_lte = django_filters.DateFilter(
        field_name='created_at', 
        lookup_expr='lte',
        label='Created before or on (YYYY-MM-DD)'
    )
    
    # Exact date filter
    created_at = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='exact',
        label='Exact date (YYYY-MM-DD)'
    )
    
    # Month/year filter
    created_at_month = django_filters.NumberFilter(
        field_name='created',
        lookup_expr='month',
        label='Month (1-12)'
    )
    
    created_at_year = django_filters.NumberFilter(
        field_name='created',
        lookup_expr='year',
        label='Year (YYYY)'
    )

    class Meta:
        model = Order
        fields = {
            'created': ['exact', 'gte', 'lte'],
        }
        filter_overrides = {
            models.DateTimeField: {
                'filter_class': django_filters.DateTimeFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                },
            },
        }