from django.contrib import admin
from .models import  Order, OrderItem

# Inline for OrderItem (used inside Order admin)
class OrderItemInline(admin.StackedInline):
    model = OrderItem
    extra = 1  # Number of empty forms shown by default
    readonly_fields = ['price_item', 'price_item_after']  # Optional, show calculated fields

# Manufacturer admin

# Order admin with inline OrderItem
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'supplier', 'total_before', 'total_after', 'created', 'modified']
    inlines = [OrderItemInline]
    readonly_fields = ['total_before', 'total_after']
