from django.contrib import admin
from django.utils.html import format_html
from .models import Invoice, SaleItem

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1
    fields = ('batch', 'quantity', 'display_total')
    readonly_fields = ('display_total',)
    
    def display_total(self, obj):
        if obj.pk:  # Only if object exists
            return f"${obj.total:.2f}"
        return "-"
    display_total.short_description = 'Total'

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'payment_status', 'display_totals', 'created')
    list_filter = ('payment_status', 'created')
    inlines = [SaleItemInline]
    readonly_fields = ('display_totals',)
    
    fieldsets = (
        (None, {
            'fields': ('payment_status', 'discount_integer')
        }),
        ('Totals', {
            'fields': ('display_totals',),
            'classes': ('collapse',)
        }),
    )
    
    def display_totals(self, obj):
        if obj.pk:  # Only if invoice exists
            try:
                subtotal = obj.total_before_discount  if obj.total_before_discount else 0
                discount = obj.discount_integer / 100
                total = obj.total_after_discount  if obj.total_after_discount else 0
                
                return format_html(
                    f"Subtotal: ${subtotal:.2f}<br>"
                    f"Discount: {discount}<br>"
                    f"Total: ${total:.2f}"
                )
            except (AttributeError, TypeError):
                return "Calculating totals..."
        return "Save invoice to calculate totals"
    display_totals.short_description = 'Invoice Totals'

@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'batch', 'quantity', 'display_total')
    list_filter = ('invoice__payment_status',)
    search_fields = ('invoice__id', 'batch__medicine__name')
    
    def display_total(self, obj):
        if obj.pk:  # Only if object exists
            return f"${obj.total:.2f}"
        return "-"
    display_total.short_description = 'Total'