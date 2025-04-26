from django.db import models
from medicine.models import Medicine, TimeStampedModel, Batch
from django.core.validators import MinValueValidator
<<<<<<< HEAD
from decimal import Decimal
=======
from decimal import Decimal, ROUND_HALF_UP

>>>>>>> code_refactoing

class Invoice(TimeStampedModel):
    PAYMENT_STATUS = [
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    ]
    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS,
        default='paid'
    )
    discount= models.DecimalField(
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
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"
        ordering = ['-created']  

    
    @property
    def total_after_discount(self):
<<<<<<< HEAD
        """Calculate total after applying discount (in cents)"""
        amount = sum(
            item.total for item in self.sales_items.all()
        )
        total = amount * (1-(self.discount/100))
        return total
=======
        """Calculate total after applying discount"""
        subtotal = self.total_before_discount  # Assuming this is a Decimal already
        amount = Decimal(subtotal)
        
        # Apply discount as a percentage (i.e., 10% discount is 0.10)
        discounted = amount * (1 - (self.discount / Decimal('100')))
>>>>>>> code_refactoing

        # Ensure rounding to 2 decimal places
        return discounted.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    def save(self, *args, **kwargs):
        """Recalculate totals before saving"""
        if self.pk and hasattr(self, "sales_items") and self.payment_status == 'paid':
            self.total_before_discount = sum(
                item.total for item in self.sales_items.all()
<<<<<<< HEAD
            )
        if self.payment_status == "refunded":
            for item in self.items.all():
                item.batch.stock_units += self.item.quantity
=======
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            
        if self.payment_status == "refunded":
            for item in self.sales_items.all():
                item.batch.stock_units +=item.quantity
                item.batch.save()
>>>>>>> code_refactoing
        super().save(*args, **kwargs)


    def __str__(self):
        return f"Invoice #{self.pk} - {self.total_after_discount}"
    
    

class SaleItem(models.Model):
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="sales_items"
    )
    batch= models.ForeignKey(
        Batch,
        on_delete=models.PROTECT,
        related_name="sale_items"
    )
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Sale Item"
        verbose_name_plural = "Sale Items"
        

    @property   
    def total(self):
<<<<<<< HEAD
        """Calculate line item total in cents"""
        return Decimal((self.batch.medicine.unit_price_cents * self.quantity) /100)

    def display_total(self):
        """Format the integer value as decimal currency"""
        return f"${self.total}"
=======
        """Calculate line item total in cents (rounded to 2 decimals)"""
        # Use pack price and units_per_pack directly
        pack_price = self.batch.medicine.price
        units_per_pack = self.batch.medicine.units_per_pack
        total = (pack_price / units_per_pack) * self.quantity
        return Decimal(total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
>>>>>>> code_refactoing

    def __str__(self):
        return f"{self.quantity}x {self.batch.medicine.name} ({self.total})"

    def save(self, *args, **kwargs):
        """Update parent invoice totals when saving"""
        super().save(*args, **kwargs)
        
        self.batch.stock_units -= self.quantity  # Decrease stock
        self.batch.save()
        self.invoice.save()