from django.contrib import admin
from .models import Supplier, Manufacturer, Order, OrderItem

# Inline for OrderItem (used inside Order admin)
class OrderItemInline(admin.StackedInline):
    model = OrderItem
    extra = 1  # Number of empty forms shown by default
    autocomplete_fields = ['medicine']  # Optional, if you want to use autocomplete for medicine
    readonly_fields = ['price_item_before', 'price_item']  # Optional, show calculated fields

# Supplier admin
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone_number', 'city']
    search_fields = ['name', 'phone_number']
    list_filter = ['city']

# Manufacturer admin
@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone_number', 'city', 'country', 'website']
    search_fields = ['name', 'phone_number', 'website']
    list_filter = ['country', 'city']

# Order admin with inline OrderItem
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'supplier', 'total_before', 'total_after', 'created', 'modified']
    inlines = [OrderItemInline]
    autocomplete_fields = ['supplier']
    readonly_fields = ['total_before', 'total_after']
