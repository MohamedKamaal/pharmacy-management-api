import pytest
from decimal import Decimal
from sales.models import Invoice, SaleItem
from medicine.models import Batch, Medicine
from sales.tests.factories import InvoiceFactory, SaleItemFactory
from medicine.tests.factories import BatchFactory, MedicineFactory
from math import ceil

pytestmark = pytest.mark.django_db


class TestInvoiceModel:
    def test_invoice_creation(self):
        invoice = InvoiceFactory()
        assert invoice.pk is not None
        assert invoice.payment_status == 'paid'
        assert invoice.discount >= 0

    def test_invoice_str(self):
        invoice = InvoiceFactory()
        assert f"Invoice #{invoice.pk}" in str(invoice)

    @pytest.mark.parametrize("discount,expected", [
        (Decimal('0.00'), Decimal('1000.00')),
        (Decimal('50.00'), Decimal('500.00')),
    ])
    def test_total_after_discount_property(self, discount, expected):
        invoice = InvoiceFactory(discount=discount)

        medicine = MedicineFactory(price=Decimal("1000.00"), units_per_pack=1)
        batch = BatchFactory(medicine=medicine, stock_units=100)

        SaleItemFactory(invoice=invoice, batch=batch, quantity=1)

        assert invoice.total_after_discount == expected

    def test_save_method_updates_total_before_discount(self):
        invoice = InvoiceFactory(payment_status='paid')
        medicine = MedicineFactory(units_per_pack=1, price=Decimal("15.50"))
        batch = BatchFactory(medicine=medicine, stock_units=10)

        SaleItemFactory(invoice=invoice, batch=batch, quantity=1)

        invoice.save()
        assert invoice.total_before_discount == Decimal('15.50')

    def test_save_does_not_update_for_unpaid_invoices(self):
        invoice = InvoiceFactory(payment_status='unpaid')
        batch = BatchFactory(stock_units=10)
        SaleItemFactory(invoice=invoice, batch=batch, quantity=1)

        invoice.save()
        assert invoice.total_before_discount == 0


class TestSaleItemModel:
    def test_sale_item_creation(self):
        batch = BatchFactory(stock_units=10)
        sale_item = SaleItemFactory(batch=batch, quantity=1)
        assert sale_item.pk is not None
        assert sale_item.quantity >= 1

    def test_sale_item_str(self):
        batch = BatchFactory(stock_units=10)
        sale_item = SaleItemFactory(batch=batch, quantity=3)
        assert sale_item.batch.medicine.name in str(sale_item)
        assert str(sale_item.quantity) in str(sale_item)

    def test_total(self):
        medicine = MedicineFactory(price=Decimal("10.10"), units_per_pack=3)
        batch = BatchFactory(medicine=medicine, stock_units=10)
        sale_item = SaleItemFactory(batch=batch, quantity=3)

        # If your model does `ceil(total, 2)` or returns Decimal directly, adjust accordingly
        expected_total = Decimal("10.10")  # 1 pack = 3 units, 3 quantity = 1 pack
        assert sale_item.total == expected_total

    def test_save_updates_invoice_and_batch(self):
        batch = BatchFactory(stock_units=100)
        invoice = InvoiceFactory(payment_status='paid')
        SaleItemFactory(invoice=invoice, batch=batch, quantity=5)

        batch.refresh_from_db()
        assert batch.stock_units == 95  # 100 - 5 units sold

        invoice.refresh_from_db()
        assert invoice.total_before_discount > 0

    def test_total_calculation_uses_unit_price(self):
        medicine = MedicineFactory(price=Decimal("30.00"), units_per_pack=2)
        batch = BatchFactory(medicine=medicine, stock_units=10)
        sale_item = SaleItemFactory(batch=batch, quantity=2)

        # Should equal 1 pack → 1 x 30.00
        assert sale_item.total == Decimal("30.00")
