"""
Django Admin Configuration for Medicine Models

This module registers all medicine-related models with the Django admin interface,
configuring their display and behavior.

Admin Models:
    - CategoryAdmin: Hierarchical display using MPTT
    - MedicineAdmin: Medicine listing with search/filter
    - BatchAdmin: Batch management with expiry date tracking
    - ActiveIngredientAdmin: Simple list view
    - SupplierAdmin: Supplier management with location filtering
    - ManufacturerAdmin: Manufacturer details with country filtering
"""

from django.contrib import admin
from django.contrib.admin import register
from mptt.admin import MPTTModelAdmin
from django.utils.html import format_html
from .models import Category, Medicine, Batch, ActiveIngredient, Supplier, Manufacturer


@register(Category)
class CategoryAdmin(MPTTModelAdmin):
    """Admin interface for Category model with tree hierarchy support."""
    list_display = ('name', 'parent')
    search_fields = ('name',)
    mptt_level_indent = 20
    list_filter = ('parent',)


@register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    """Admin interface for Medicine model with search and filtering."""
    list_display = ('international_barcode', 'category', 'price', 'units_per_pack')
    list_filter = ('category',)
    search_fields = ('international_barcode', 'category__name')
    raw_id_fields = ('category',)


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    """Admin interface for Batch model with expiry date management."""
    list_display = ('medicine', 'barcode', 'expiry_date', 'stock_units')
    list_filter = ('expiry_date', 'medicine__category')
    search_fields = ('barcode', 'medicine__name')
    date_hierarchy = 'expiry_date'
    readonly_fields = ['barcode']
    autocomplete_fields = ['medicine']  # Enables search while showing add button


@register(ActiveIngredient)
class ActiveIngredientAdmin(admin.ModelAdmin):
    """Simple admin interface for ActiveIngredient model."""
    list_display = ('name',)


@register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    """Admin interface for Supplier model with location filtering."""
    list_display = ['name', 'phone_number', 'city']
    search_fields = ['name', 'phone_number']
    list_filter = ['city']


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    """Admin interface for Manufacturer model with country filtering."""
    list_display = ['name', 'phone_number', 'country', 'website']
    search_fields = ['name', 'phone_number', 'website']
    list_filter = ['country']