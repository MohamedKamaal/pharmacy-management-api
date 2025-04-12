import pytest
from sales.models import Invoice, SaleItem
from medicine.models import Batch, Medicine
from sales.tests.factories import InvoiceFactory, SaleItemFactory
from medicine.tests.factories import BatchFactory, MedicineFactory

pytestmark = pytest.mark.django_db


class TestInvoiceModel:
    def test_invoice_creation(self):
        """Test basic invoice creation"""
        invoice = InvoiceFactory()
        assert invoice.pk is not None
        assert invoice.payment_status == 'paid'
        assert 1 <= invoice.discount_integer <= 100

    def test_invoice_str(self):
        """Test the __str__ method"""
        invoice = InvoiceFactory()
        assert str(invoice).startswith(f"Invoice #{invoice.pk} - $")

    def test_discount_decimal_property(self):
        """Test discount_decimal property converts correctly"""
        invoice = InvoiceFactory(discount_integer=20)
        assert invoice.discount_decimal == .2  # Now expects integer, not decimal

    @pytest.mark.parametrize("discount,expected", [
        (0, 10),    # $10.00 (in cents)
        (5000, 5),    # $5.00
        (10000, 0),     # $0.00
    ])
    def test_total_after_discount_property(self, discount, expected):
        """Test total_after_discount calculation in cents"""
        invoice = InvoiceFactory(discount_integer=discount)
        
        # Create sale item with known total (1000 cents = $10)
        medicine = MedicineFactory(price_cents=1000, units_per_pack=1)  # $10.00 per unit
        batch = BatchFactory(medicine=medicine)
        
        SaleItemFactory(
            invoice=invoice,
            batch=batch,
            quantity=1  # 1 unit of $10
        )
        
        # Verify total after discount calculation in cents
        assert invoice.total_after_discount == expected

    def test_display_total_after_discount(self):
        """Test currency formatting"""
        invoice = InvoiceFactory(discount_integer=1000)
        medicine = MedicineFactory(price_cents=1000, units_per_pack=1)  # $10.00 per unit
        batch = BatchFactory(medicine=medicine)
        SaleItemFactory(invoice=invoice, batch=batch, quantity=1)
        
        # $10 with 10% discount = $9.00
        assert invoice.display_total_after_discount() == "$9.0"

    def test_save_method_updates_total_before_discount(self):
        """Test that save() updates total_before_discount for paid invoices"""
        invoice = InvoiceFactory(payment_status='paid')
        medicine = MedicineFactory(price_cents=1000, units_per_pack=1)  # $10.00 per unit
        batch = BatchFactory(medicine=medicine)
        
        SaleItemFactory(invoice=invoice, batch=batch, quantity=1)  # $10 total
        
        
        invoice.save()
        assert invoice.total_before_discount == 10

    def test_save_does_not_update_for_unpaid_invoices(self):
        """Test that unpaid invoices don't update totals on save"""
        invoice = InvoiceFactory(payment_status='unpaid')
        SaleItemFactory(invoice=invoice)
        
        invoice.save()
        assert invoice.total_before_discount == 0


class TestSaleItemModel:
    def test_sale_item_creation(self):
        """Test basic sale item creation"""
        sale_item = SaleItemFactory()
        assert sale_item.pk is not None
        assert sale_item.quantity >= 1

    def test_sale_item_str(self):
        """Test the __str__ method"""
        sale_item = SaleItemFactory(quantity=3)
        assert sale_item.batch.medicine.name in str(sale_item)
        assert str(sale_item.quantity) in str(sale_item)
        assert "$" in str(sale_item)

    def test_total_property(self):
        """Test line item total calculation in cents"""
        medicine = MedicineFactory(price_cents=1000, units_per_pack=1)  # $10.00 per unit
        batch = BatchFactory(medicine=medicine)
        sale_item = SaleItemFactory(batch=batch, quantity=1)
        
       
        assert sale_item.total == 10

    def test_display_total(self):
        """Test currency formatting"""
        medicine = MedicineFactory(price_cents=1000, units_per_pack=1)  # $10.00 per unit
        batch = BatchFactory(medicine=medicine)
        sale_item = SaleItemFactory(batch=batch, quantity=1)
        
        assert sale_item.display_total() == "$10.0"

    def test_save_updates_invoice_and_batch(self):
        """Test that saving updates invoice and batch stock"""
        batch = BatchFactory(stock_units=100)
        invoice = InvoiceFactory(payment_status='paid')
        sale_item = SaleItemFactory(invoice=invoice, batch=batch, quantity=5)
        
        # Should increase batch stock by quantity
        batch.refresh_from_db()
        assert batch.stock_units == 105
        
        # Should trigger invoice save which updates totals
        invoice.refresh_from_db()
        assert invoice.total_before_discount > 0

    def test_save_does_not_update_batch_for_unpaid_invoices(self):
        """Test that unpaid invoices don't affect batch stock"""
        batch = BatchFactory(stock_units=100)
        invoice = InvoiceFactory(payment_status='unpaid')
        sale_item = SaleItemFactory(invoice=invoice, batch=batch, quantity=5)
        
        # Stock should remain unchanged
        batch.refresh_from_db()
        assert batch.stock_units == 100

    def test_total_calculation_uses_unit_price_cents(self):
        """Test that total calculation uses the unit price"""
        medicine = MedicineFactory(price_cents=1000, units_per_pack=1)  # $10.00 per unit
        batch = BatchFactory(medicine=medicine)
        sale_item = SaleItemFactory(batch=batch, quantity=2)
        

        assert sale_item.total == 20