
from django.db import models
from medicine.models import TimeStampedModel
from django.core.validators import MinValueValidator, MaxValueValidator
from medicine.models import Medicine, Batch, Supplier, Manufacturer
from decimal import Decimal
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
            self.total_after = sum(item.price_item_after for item in self.items.all())
            
        
        super().save(*args, **kwargs)
    
    @property
    def total_before(self):
        return sum(
           item.price_item for item in self.items.all()
       )
        
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name="items")
    quantity = models.IntegerField()
    discount = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )



  
    
    
    @property
    def price_item_after(self):
      return Decimal(self.quantity * self.batch.medicine.unit_price * (1 - self.discount/100))

    @property
    def price_item(self):
        return Decimal(self.quantity * self.batch.medicine.unit_price)
    

    
    class Meta:
        """ ensure same medicine appear only once per order """
        unique_together = ["order","batch"]
