
import django_filters
from sales.models import Invoice

class InvoiceFilter(django_filters.FilterSet):
    # Date range filters
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
    
    # Exact date filter
    created = django_filters.DateFilter(
        field_name='created',
        lookup_expr='exact',
        label='Exact date (YYYY-MM-DD)'
    )
    
    # Month/year filter
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
        model = Invoice
        fields = [
            'created',
            'created__gte',
            'created__lte',
            'created__month',
            'created__year',
        ]
