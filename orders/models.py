"""
Order Management Models

This module contains models for handling medicine orders from suppliers.

Models:
    - Order: Represents a purchase order to a supplier
    - OrderItem: Individual items within an order with quantity and discount
"""

from django.db import models
from medicine.models import TimeStampedModel
from django.core.validators import MinValueValidator, MaxValueValidator
from medicine.models import Medicine, Batch, Supplier, Manufacturer
from decimal import Decimal, ROUND_HALF_UP


class Order(TimeStampedModel):
    """
    Represents a purchase order to a supplier.
    
    Attributes:
        supplier (ForeignKey): Supplier being ordered from
        total_after (DecimalField): Final order total after discounts
    """
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="orders")
    total_after = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    def save(self, *args, **kwargs):
        """Calculate and update order total when saving."""
        if self.pk and hasattr(self, 'items'):
            self.total_after = round(sum(item.price_item_after for item in self.items.all()), 2)
        super().save(*args, **kwargs)
    
    @property
    def total_before(self):
        """Calculate order total before any discounts."""
        total = sum(item.price_item_before for item in self.items.all())
        return Decimal(total).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class OrderItem(models.Model):
    """
    Individual item within a purchase order.
    
    Attributes:
        order (ForeignKey): Parent order
        batch (ForeignKey): Medicine batch being ordered
        quantity (PositiveIntegerField): Number of units ordered
        discount (DecimalField): Percentage discount applied
    """
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
        """Calculate item price after discount."""
        discount_multiplier = (Decimal(1) - Decimal(self.discount) / Decimal(100))
        total = Decimal(self.quantity) * self.batch.medicine.unit_price * discount_multiplier
        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    @property
    def price_item_before(self):
        """Calculate item price before discount."""
        total = Decimal(self.quantity) * self.batch.medicine.unit_price
        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    class Meta:
        """Ensure same medicine appears only once per order."""
        unique_together = ["order", "batch"]