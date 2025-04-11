from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from medicine.models import Batch
from orders.models import OrderItem, Order



@receiver(pre_delete, sender=OrderItem)
def update_stock_upon_delete_order_item(sender, instance, **kwargs):
    instance.batch.stock_units -= instance.quantity  # Restore stock
    instance.batch.save()
    instance.order.save()

