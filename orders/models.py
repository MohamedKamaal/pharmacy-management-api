
from django.db import models
from medicine.models import TimeStampedModel

from medicine.models import Medicine, Batch, Supplier, Manufacturer

# Create your models here.


class Order(TimeStampedModel):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="orders")
    total_before = models.IntegerField(null=True, blank=True)
    total_after = models.IntegerField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        """ add total before and total_after """
        self.total_before = sum(
            item.price_item_before for item in self.items.all()
        )
        self.total_after = sum(
            item.price_item for item in self.items.all()
        )
        return super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name="items")
    quantity = models.IntegerField()
    discount = models.DecimalField(max_digits=4, decimal_places=2)

    @property
    def price_item_after(self):
        return int(self.quantity * self.medicine.price * (100 - self.discount / 100))

    @property
    def price_item(self):
        return int(self.quantity * self.medicine.price)
    
    # def save(self, *args, **kwargs):
    #     """ change  """
    #     self.medicine.stock_units += self.quantity * self.medicine.units_per_pack
    #     return super().save(*args, **kwargs)
    
    class Meta:
        """ ensure same medicine appear only once per order """
        unique_together = ["order","batch"]
# Task
# add post delete and post save (create) signals 
 
