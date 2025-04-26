"""
Pagination:
    - MedicinePagination: Custom pagination settings for medicine listings
"""


from rest_framework.pagination import PageNumberPagination
from rest_framework import serializers 
from medicine.models import Medicine, Batch, Supplier, ActiveIngredient, Category, Manufacturer
from django.utils.timezone import now 

class MedicinePagination(PageNumberPagination):
    """
    Custom pagination settings for medicine listings.
    
    Attributes:
        page_size (int): Default items per page
        page_size_query_param (str): Query parameter to override page size
        max_page_size (int): Maximum allowed items per page
    """
    page_size = 10 
    page_size_query_param = "size"
    max_page_size = 10


