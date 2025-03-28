""" add supplier model """
from django.db import models
from medicine.models import TimeStampedModel

from medicine.models import Medicine, Supplier, Manufacturer

# Create your models here.


class Order(TimeStampedModel):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="orders")
    total_before = models.IntegerField(null=True)
    total_after = models.IntegerField(null=True)
    
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
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name="items")
    quantity = models.IntegerField()
    discount = models.IntegerField()

    @property
    def price_item_before(self):
        return int(self.quantity * self.medicine.price * (1 - self.discount / 100))

    @property
    def price_item(self):
        return int(self.quantity * self.medicine.price)
    
    def save(self, *args, **kwargs):
        """ change  """
        self.medicine.stock_units += self.quantity * self.medicine.units_per_pack
        return super().save(*args, **kwargs)
    
    class Meta:
        """ ensure same medicine appear only once per order """
        unique_together = ["order","medicine"]