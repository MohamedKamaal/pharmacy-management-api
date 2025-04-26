"""
Medicine Pharmacy Models

This module contains all the models related to medicine management in a pharmacy system,
including suppliers, manufacturers, categories, medicines, and batches.

Models:
    - TimeStampedModel: Abstract base model with created/modified timestamps
    - Supplier: Entity that provides medicines to the pharmacy
    - Manufacturer: Company that produces medicines
    - Category: Hierarchical classification for medicines (using MPTT)
    - ActiveIngredient: The active pharmaceutical ingredient in medicines
    - Medicine: The main product model representing a specific medication
    - Batch: Inventory lot tracking for medicines with expiry dates
"""

from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.core.exceptions import ValidationError
from django.utils.timezone import now
import random
import string
from phonenumber_field.modelfields import PhoneNumberField
from cities_light.models import City
from django_countries.fields import CountryField
from decimal import Decimal
from django.core.validators import MinLengthValidator, MinValueValidator
from decimal import Decimal, ROUND_HALF_UP
import secrets


class TimeStampedModel(models.Model):
    """
    Abstract base model that provides self-updating created and modified fields.
    
    Attributes:
        created (DateTimeField): When the record was first created (auto-set)
        modified (DateTimeField): When the record was last updated (auto-updated)
    """
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Supplier(TimeStampedModel):
    """
    Represents a supplier who provides medicines to the pharmacy.
    
    Attributes:
        name (CharField): Unique name of the supplier
        phone_number (PhoneNumberField): Contact number (Egyptian region)
        address (TextField): Physical address details
        city (ForeignKey): Link to the supplier's city
    """
    name = models.CharField(unique=True, max_length=50)
    phone_number = PhoneNumberField(region="EG", null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        verbose_name = 'Supplier'
        verbose_name_plural = 'Suppliers'

    def __str__(self):
        return str(self.name)


class Manufacturer(TimeStampedModel):
    """
    Represents a pharmaceutical company that manufactures medicines.
    
    Attributes:
        name (CharField): Unique name of the manufacturer
        country (CountryField): Country of origin
        phone_number (PhoneNumberField): Contact number
        address (TextField): Physical address details
        website (URLField): Company website URL
    """
    name = models.CharField(unique=True, max_length=50)
    country = CountryField(blank_label="(Select country)")
    phone_number = PhoneNumberField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    website = models.URLField(null=True, blank=True, unique=True, max_length=200)

    class Meta:
        verbose_name = 'Manufacturer'
        verbose_name_plural = 'Manufacturers'

    def __str__(self):
        return str(self.name)


class Category(MPTTModel):
    """
    Hierarchical category system for organizing medicines using Modified Preorder Tree Traversal.
    
    Attributes:
        name (CharField): Name of the category (must be unique)
        parent (TreeForeignKey): Parent category for creating hierarchy
    """
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
    """
    The active pharmaceutical ingredient (API) in medicines.
    
    Attributes:
        name (CharField): Name of the active ingredient (must be unique)
    """
    name = models.CharField("Active Ingredient", max_length=50, unique=True)
    
    def __str__(self):
        return str(self.name)
    
    
class Medicine(TimeStampedModel):
    """
    Represents a specific medication product in the pharmacy.
    
    Attributes:
        international_barcode (CharField): Unique product identifier (13-16 digits)
        name (CharField): Brand name of the medicine
        active_ingredient (ForeignKey): Primary active component
        category (ForeignKey): Classification category
        manufacturer (ForeignKey): Producing company
        units_per_pack (PositiveSmallIntegerField): Quantity of units in one package
        price (DecimalField): Retail price for one pack (in cents)
        
    Properties:
        is_available (bool): Whether any non-expired stock exists
        unit_price (Decimal): Calculated price per single unit
        stock (str): Current inventory level in "packs:units" format
    """
    international_barcode = models.CharField(
        "International Barcode",
        max_length=16,
        unique=True,
        db_index=True,
        validators=[MinLengthValidator(13)]
    )    
    name = models.CharField(unique=True, max_length=50)
    active_ingredient = models.ForeignKey(ActiveIngredient, on_delete=models.CASCADE, related_name="medicines")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="medicines")
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE, related_name="medicines")

    units_per_pack = models.PositiveSmallIntegerField(default=1)
    price = models.DecimalField(
        "price in cents",
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Price of pack"
    )
   
    @property
    def is_available(self):
        """Check if this medicine has any available non-expired stock."""
        return self.batches.filter(stock_units__gt=0).exists()
        
    @property
    def unit_price(self):
        """Calculate and return the price per single unit."""
        return (Decimal(self.price) / Decimal(self.units_per_pack)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    @property
    def stock(self):
        """Return current inventory level in 'packs:units' format."""
        if self.batches:
            total = sum(batch.stock_units for batch in self.batches.all())
            packs = total // self.units_per_pack
            units = total % self.units_per_pack
            return f"{packs}:{units}"
        return 0

    def __str__(self):
        return self.name


def generate_barcode():
    """
    Generate a cryptographically secure 16-digit unique barcode.
    
    Returns:
        str: 16-digit random numeric string
    """
    return ''.join(secrets.choice(string.digits) for _ in range(16))
        
        
class Batch(TimeStampedModel):
    """
    Represents a specific lot or batch of a medicine with expiry tracking.
    
    Attributes:
        barcode (CharField): Unique 16-digit batch identifier
        expiry_date (DateField): When this batch expires
        medicine (ForeignKey): Related medicine product
        stock_units (PositiveIntegerField): Current inventory count
        
    Properties:
        price (Decimal): Unit price from parent medicine
        is_expired (bool): Whether batch has passed expiry date
        has_amount (bool): Whether any stock remains
        stock_packets (str): Inventory in "packs:units" format
    """
    barcode = models.CharField(
        max_length=16,
        unique=True,
        null=True,
        blank=True,
        validators=[MinLengthValidator(16)]
    )
    expiry_date = models.DateField(auto_now=False, auto_now_add=False)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name="batches")
    stock_units = models.PositiveIntegerField()
    
    class Meta:
        unique_together = ["expiry_date", "medicine"]
    
    def __str__(self):
        return f"{self.medicine.name}-{self.expiry_date}"

    def clean(self):
        """Validate batch data before saving."""
        super().clean()
        if self.expiry_date and self.expiry_date <= now().date():
            raise ValidationError({"expiry_date": "This is not a valid date"})
        
        if self.stock_units < 0:
            raise ValidationError({"stock_units": "stock units must be positive"})

    @property 
    def price(self):
        """Get the unit price from the parent medicine."""
        return self.medicine.unit_price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    @property 
    def is_expired(self):
        """Check if this batch has expired."""
        return self.expiry_date <= now().date()

    @property 
    def has_amount(self):
        """Check if this batch has any remaining stock."""
        return self.stock_units > 0
        
    @property
    def stock_packets(self):
        """Return inventory level in 'packs:units' format."""
        packs = self.stock_units // self.medicine.units_per_pack
        units = self.stock_units % self.medicine.units_per_pack
        return f"{packs}:{units}"
    
    def save(self, *args, **kwargs):
        """
        Save the batch, generating a unique barcode if none exists.
        
        The barcode generation ensures uniqueness by checking against existing records.
        """
        if not self.barcode:
            barcode = generate_barcode()
            while Batch.objects.filter(barcode=barcode).exists():
                barcode = generate_barcode()
            self.barcode = barcode

        return super().save(*args, **kwargs)