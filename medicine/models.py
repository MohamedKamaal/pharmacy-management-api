""" medicine models """
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.core.exceptions import ValidationError
from django.utils.timezone import now
import random
import string
from phonenumber_field.modelfields import PhoneNumberField
from cities_light.models import City
from django_countries.fields import CountryField




# Create your models here.

class TimeStampedModel(models.Model):
    created =  models.DateTimeField(auto_now_add=True)
    modified =  models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True 


class Supplier(TimeStampedModel):
    """ Supplier """

    name = models.CharField(unique=True, max_length=50)
    phone_number = PhoneNumberField(region="EG",null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        """Meta definition for MODELNAME."""

        verbose_name = 'Supplier'
        verbose_name_plural = 'Suppliers'

    def __str__(self):
        
        return str(self.name)


class Manufacturer(TimeStampedModel):
    """ Manufacturer """

    name = models.CharField(unique=True, max_length=50)
    country = CountryField(blank_label="(Select country)")
    phone_number = PhoneNumberField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    website = models.URLField(null=True, blank=True,unique=True, max_length=200)

    class Meta:
        """Meta definition for MODELNAME."""

        verbose_name = 'Manufacturer'
        verbose_name_plural = 'Manufacturer'

    def __str__(self):
        """Unicode representation of MODELNAME."""
        return str(self.name)


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
    name = models.CharField(unique=True, max_length=50)
    active_ingredient = models.ForeignKey(ActiveIngredient, on_delete=models.CASCADE, related_name="medicines")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="medicines")
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE, related_name="medicines")
    last_supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="medicines", null=True, blank=True)

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
   
    @property
    def price(self):
        return self.price_cents / 100

    @property
    def unit_price(self):
        return self.price / self.units_per_pack
    
    @property
    def unit_price_cents(self):
        return self.price_cents / self.units_per_pack
    @property
    def stock(self):
        if self.batches:
            total = sum (
                batch.stock_units for batch in self.batches.all()
                )
            packs = total // self.units_per_pack
            units = total % self.units_per_pack
            return f"{packs}:{units}"
        return 0

    def __str__(self):
        return self.name
import secrets

def generate_barcode():
    """Generate a cryptographically secure 16-digit unique barcode"""
   
    barcode = ''.join(secrets.choice(string.digits) for _ in range(16))
       
    return barcode
        
class Batch(TimeStampedModel):
    barcode = models.CharField(max_length=16,unique=True, null=True, blank=True)
    expiry_date = models.DateField(auto_now=False, auto_now_add=False)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name="batches")
    stock_units = models.PositiveIntegerField(default=0)
    class Meta:
        unique_together = ["expiry_date","medicine"]
    
    def __str__(self):
        return f"{self.medicine.name}-{self.expiry_date}"

    def clean(self):
        super().clean()
        if self.expiry_date and self.expiry_date <= now().date():
            raise ValidationError({"expiry_date": "This is not a valid date"})
        
        if self.stock_units <= 0:
            raise ValidationError({"stock_units": "stock units must be greater than zero"})

    @property 
    def price_cents(self):
        return self.medicine.unit_price_cents
    @property 
    def price(self):
        return self.medicine.unit_price
    @property 
    def is_expired(self):
        return self.expiry_date <= now().date()
    @property 
    def has_amount(self):
        return self.stock_units >0
    @property
    def stock_packets(self):
        packs = self.stock_units // self.medicine.units_per_pack
        units = self.stock_units % self.medicine.units_per_pack
        return f"{packs}:{units}"
    
    def save(self, *args, **kwargs):
        """ save unique barcode """
        if not self.barcode:
            barcode = generate_barcode()
            while Batch.objects.filter(
                barcode=barcode
            ).exists():
                barcode = generate_barcode()
            self.barcode = barcode

        return super().save( *args, **kwargs)