"""
Models for managing invoices and sale items in a sales system.

This module defines the `Invoice` and `SaleItem` models, which handle the creation,
management, and calculations related to invoices and their associated sale items.
The `Invoice` model includes payment status, discount, and total calculations, while
the `SaleItem` model tracks individual items sold within an invoice.
"""

from django.db import models
from medicine.models import Medicine, TimeStampedModel, Batch
from django.core.validators import MinValueValidator
from decimal import Decimal, ROUND_HALF_UP


class Invoice(TimeStampedModel):
    """
    Represents an invoice in the sales system.

    Attributes:
        payment_status (CharField): The payment status of the invoice ('paid' or 'refunded').
        discount (DecimalField): The discount percentage applied to the invoice (0-100%).
        total_before_discount (DecimalField): The total amount before applying the discount.
    """
    PAYMENT_STATUS = [
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    ]
    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS,
        default='paid'
    )
    discount = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    total_before_discount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0
    )

    class Meta:
        """Metadata for the Invoice model."""
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"
        ordering = ['-created']

    @property
    def total_after_discount(self):
        """Calculate the total after applying the discount."""
        subtotal = self.total_before_discount
        amount = Decimal(subtotal)
        discounted = amount * (1 - (self.discount / Decimal('100')))
        return discounted.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def save(self, *args, **kwargs):
        """Recalculate totals and handle stock updates before saving."""
        if self.pk and hasattr(self, "sales_items") and self.payment_status == 'paid':
            self.total_before_discount = sum(
                item.total for item in self.sales_items.all()
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        if self.payment_status == "refunded":
            for item in self.sales_items.all():
                item.batch.stock_units += item.quantity
                item.batch.save()
        super().save(*args, **kwargs)

    def __str__(self):
        """String representation of the Invoice."""
        return f"Invoice #{self.pk} - {self.total_after_discount}"


class SaleItem(models.Model):
    """
    Represents an individual item sold within an invoice.

    Attributes:
        invoice (ForeignKey): The invoice this sale item belongs to.
        batch (ForeignKey): The batch of medicine being sold.
        quantity (PositiveIntegerField): The quantity of the item sold.
    """
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="sales_items"
    )
    batch = models.ForeignKey(
        Batch,
        on_delete=models.PROTECT,
        related_name="sale_items"
    )
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        """Metadata for the SaleItem model."""
        verbose_name = "Sale Item"
        verbose_name_plural = "Sale Items"

    @property
    def total(self):
        """Calculate the total cost of the sale item."""
        pack_price = self.batch.medicine.price
        units_per_pack = self.batch.medicine.units_per_pack
        total = (pack_price / units_per_pack) * self.quantity
        return Decimal(total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    def __str__(self):
        """String representation of the SaleItem."""
        return f"{self.quantity}x {self.batch.medicine.name} ({self.total})"

    def save(self, *args, **kwargs):
        """Update stock and parent invoice totals when saving."""
        super().save(*args, **kwargs)
        self.batch.stock_units -= self.quantity
        self.batch.save()
        self.invoice.save()