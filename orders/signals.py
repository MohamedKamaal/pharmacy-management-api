from django.dispatch import receiver
from medicine.models import Batch
from orders.models import OrderItem
from django.db.models.signals import post_save, pre_delete

@receiver(post_save, sender=OrderItem)
def update_stock_upon_create_order_item(sender, instance, created, **kwargs):
    if created:
        instance.batch.stock_units += instance.quantity  # Reduce stock
        instance.batch.save()

@receiver(pre_delete, sender=OrderItem)
def update_stock_upon_delete_order_item(sender, instance, **kwargs):
    instance.batch.stock_units -= instance.quantity  # Restore stock
    instance.batch.save()
