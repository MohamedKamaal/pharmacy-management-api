"""
Django admin configurations for sales models.

This module defines admin interfaces for managing Invoice and SaleItem models,
including inline editing, custom list displays, and filters.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Invoice, SaleItem


class SaleItemInline(admin.TabularInline):
    """
    Inline admin interface for SaleItem model.

    Allows editing sale items directly within the Invoice admin interface.
    """
    model = SaleItem
    extra = 1
    fields = ('batch', 'quantity')


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """
    Admin interface for Invoice model.

    Provides list display, filtering, and inline editing of sale items.
    """
    list_display = ('id', 'payment_status', 'created')
    list_filter = ('payment_status', 'created')
    inlines = [SaleItemInline]
    fieldsets = (
        (None, {
            'fields': ('payment_status', 'discount_integer')
        }),
    )


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    """
    Admin interface for SaleItem model.

    Includes custom list display for total cost and filtering/search capabilities.
    """
    list_display = ('invoice', 'batch', 'quantity', 'display_total')
    list_filter = ('invoice__payment_status',)
    search_fields = ('invoice__id', 'batch__medicine__name')

    def display_total(self, obj):
        """Display the total cost of the sale item in the admin list view."""
        if obj.pk:
            return f"${obj.total:.2f}"
        return "-"
    display_total.short_description = 'Total'