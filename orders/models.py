
from django.db import models
from medicine.models import TimeStampedModel
from django.core.validators import MinValueValidator, MaxValueValidator
from medicine.models import Medicine, Batch, Supplier, Manufacturer
from decimal import Decimal, ROUND_HALF_UP
# Create your models here.


class Order(TimeStampedModel):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="orders")
    total_after = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    def save(self, *args, **kwargs):
        
    
        # Calculate totals only if this is an existing order with items
        if self.pk and hasattr(self, 'items'):
            self.total_after = round(sum(item.price_item_after for item in self.items.all()),2)
            
        
        super().save(*args, **kwargs)
    
    @property
    def total_before(self):
            total = sum(item.price_item_before for item in self.items.all())
            return Decimal(total).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name="items")
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    discount = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )



  
    
    
    @property
    def price_item_after(self):
        discount_multiplier = (Decimal(1) - Decimal(self.discount) / Decimal(100))
        total = Decimal(self.quantity) * self.batch.medicine.unit_price * discount_multiplier
        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    @property
    def price_item_before(self):
        total = Decimal(self.quantity) * self.batch.medicine.unit_price
        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    

    
    class Meta:
        """ ensure same medicine appear only once per order """
        unique_together = ["order","batch"]
