from django.contrib import admin
from django.contrib.admin import register
from mptt.admin import MPTTModelAdmin
from .models import Category, Medicine, Batch, ActiveIngredient, Supplier, Manufacturer

@register(Category)
class CategoryAdmin(MPTTModelAdmin):
    list_display = ('name', 'parent')
    search_fields = ('name',)
    mptt_level_indent = 20
    list_filter = ('parent',)

@register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('international_barcode', 'category', 'price', 'units_per_pack', 'last_discount_percent')
    list_filter = ('category',)
    search_fields = ('international_barcode', 'category__name')
    raw_id_fields = ('category',)
    
    def price(self, obj):
        return f"${obj.price:.2f}"
    price.short_description = 'Price'

@register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ('barcode', 'medicine', 'expiry_date', 'stock_units', 'stock_packets')
    list_filter = ('expiry_date', 'medicine__category')
    search_fields = ('barcode', 'medicine__international_barcode')
    raw_id_fields = ('medicine',)
    date_hierarchy = 'expiry_date'
    
@register(ActiveIngredient)
class ActiveIngredientAdmin(admin.ModelAdmin):
    list_display = ('name',)
    
@register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone_number', 'city']
    search_fields = ['name', 'phone_number']
    list_filter = ['city']

@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone_number', 'country', 'website']
    search_fields = ['name', 'phone_number', 'website']
    list_filter = ['country',]
