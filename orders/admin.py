"""
Order Admin Configuration

Configures Django admin interface for order management models.
"""

from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.StackedInline):
    """Inline admin for OrderItems within Order admin."""
    model = OrderItem
    extra = 1  # Number of empty forms shown by default
    readonly_fields = ['price_item_after']  # Show calculated fields


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin interface for Order model."""
    list_display = ['id', 'supplier', 'total_before', 'total_after', 'created', 'modified']
    inlines = [OrderItemInline]
    readonly_fields = ['total_before', 'total_after']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin interface for OrderItem model."""
    list_display = ['order', 'batch', 'quantity', 'discount', 'price_item_before', 'price_item_after']