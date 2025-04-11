
from django.db import models
from medicine.models import TimeStampedModel

from medicine.models import Medicine, Batch, Supplier, Manufacturer

# Create your models here.


class Order(TimeStampedModel):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="orders")
    total_after = models.IntegerField(null=True, blank=True)
    
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
    discount_integer = models.PositiveSmallIntegerField()



    @property
    def discount_decimal(self):
        return self.discount_integer / 100 
    
    
    @property
    def price_item_after(self):
      return int(self.quantity * self.batch.medicine.unit_price * (1 - self.discount_decimal))

    @property
    def price_item(self):
        return int(self.quantity * self.batch.medicine.unit_price)
    

    
    class Meta:
        """ ensure same medicine appear only once per order """
        unique_together = ["order","batch"]
