from django.contrib import admin
from django.utils.html import format_html
from .models import Invoice, SaleItem

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1
    fields = ('batch', 'quantity')
 
   

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
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
    list_display = ('invoice', 'batch', 'quantity', 'display_total')
    list_filter = ('invoice__payment_status',)
    search_fields = ('invoice__id', 'batch__medicine__name')
    
    def display_total(self, obj):
        if obj.pk:  # Only if object exists
            return f"${obj.total:.2f}"
        return "-"
    display_total.short_description = 'Total'