from django.db import models
from decimal import Decimal
from medicine.models import Medicine, TimeStampedModel

class Invoice(TimeStampedModel):
    PAYMENT_STATUS = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    ]
    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS,
        default='unpaid'
    )
    discount_percentage = models.DecimalField(
        "Discount Percentage", 
        max_digits=4, 
        decimal_places=2,
        default=0.00,
        help_text="Discount percentage (0-100)"
    )
    total_before_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        editable=False
    )
    

    class Meta:
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"
        ordering = ['-created']  # Assuming TimeStampedModel has 'created' field

    @property
    def total_after_discount(self):
        """Calculate total after applying discount"""
        discount_factor = (100 - self.discount_percentage) / Decimal('100')
        return self.total_before_discount * discount_factor

    def save(self, *args, **kwargs):
        """Recalculate totals before saving"""
      
        self.total_before_discount = sum(
            Decimal(item.total) for item in self.sales_items.all()
        )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Invoice #{self.pk} - {self.total_after_discount:.2f}"

class SaleItem(models.Model):
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="sales_items"
    )
    medicine = models.ForeignKey(
        Medicine,
        on_delete=models.PROTECT,  # Prevent deletion if medicines are referenced
        related_name="sale_items"
    )
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Sale Item"
        verbose_name_plural = "Sale Items"
        constraints = [
            models.UniqueConstraint(
                fields=['invoice', 'medicine'],
                name='unique_medicine_per_invoice'
            )
        ]

    @property
    def total(self):
        """Calculate line item total with proper decimal handling"""
        return (self.medicine.price * self.quantity) 

    def __str__(self):
        return f"{self.quantity}x {self.medicine.name}"

    def save(self, *args, **kwargs):
        """Update parent invoice totals when saving"""
        super().save(*args, **kwargs)
        self.invoice.save()  # Trigger invoice total recalculation