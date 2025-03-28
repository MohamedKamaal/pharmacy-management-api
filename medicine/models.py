""" medicine models """
from django.db import models
from mptt import MPTTModel, TreeForeignKey
from django.core.exceptions import ValidationError
from django.utils.timezone import now
import random
import string




# Create your models here.

class TimeStampedModel(models.Model):
    created =  models.DateTimeField(auto_now_add=True)
    modified =  models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True 
        
class Category(MPTTModel):
    name = models.CharField(max_length=100, unique=True)
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name

class ActiveIngredient(TimeStampedModel):
    name = models.CharField("Active Ingredient", max_length=50, unique=True)
    def __str__(self):
        return str(self.name)
    
    
class Medicine(TimeStampedModel):
    international_barcode = models.CharField(
        "International Barcode",
        max_length=16,
        unique=True,
        db_index=True
    )    
    active_ingredient = models.ForeignKey(ActiveIngredient, on_delete=models.CASCADE, related_name="medicines")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="medicines")
    units_per_pack = models.IntegerField(default=1)
    price_cents = models.PositiveIntegerField(
        "price in cents",
        help_text="Price of pack in cents"
    )
    last_discount_percent = models.DecimalField(
        "Last Discount Percent",
        max_digits=4,  # allows up to 99.99
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Percentage discount you got when last purchasing this medicine."
    )
    def clean_price_cents(self, value):
        if value <= 0:
            raise ValidationError(
                "Price can't be negative or zero"
            )
    @property
    def price(self):
        return self.price_cents / 100

    @property
    def stock(self):
        if self.batches:
            total = sum (
                stock for stock in self.batches.stock_units
                )
            packs = total // self.units_per_pack
            units = total % self.units_per_pack
            return f"{packs}:{units}"
        return 0


import secrets

def generate_barcode(self):
    """Generate a cryptographically secure 16-digit unique barcode"""
   
    barcode = ''.join(secrets.choice(string.digits) for _ in range(16))
       
    return barcode
        
class Batch(TimeStampedModel):
    barcode = models.IntegerField(max_length=16,unique=True, null=True, blank=True)
    expiry_date = models.DateField(auto_now=False, auto_now_add=False)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name="batches")
    stock_units = models.PositiveIntegerField(default=0)
    class Meta:
        unique_together = ["expiry_date","medicine"]
    
    def clean_expiry_date(self, value):
        if value <= now():
            raise ValidationError(
                "this is not a valid date"
            )
    
            
    @property
    def stock_packets(self):
        packs = self.stock_units // self.medicine.units_per_pack
        units = self.stock_units % self.medicine.units_per_pack
        return f"{packs}:{units}"
    
    def save(self, *args, **kwargs):
        """ save unique barcode """
        barcode = generate_barcode()
        while Batch.objects.filter(
            barcode=barcode
        ).exists():
            barcode = generate_barcode()
        self.barcode = barcode

        return super().save( *args, **kwargs)