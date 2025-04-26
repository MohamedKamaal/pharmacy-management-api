import pytest
from decimal import Decimal
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from sales.models import Invoice, SaleItem
from medicine.models import Batch
from medicine.tests.factories import BatchFactory, MedicineFactory
from sales.tests.factories import SaleItemFactory, InvoiceFactory
from sales.serializers import SaleItemSerializer, InvoiceCreationSerializer, ReturnInvoiceSerializer


@pytest.mark.django_db
class TestSaleItemSerializer:
    def test_valid_data(self):
        """Test serializer with valid data"""
        batch = BatchFactory(
            stock_units=10,
            expiry_date=timezone.now().date() + timezone.timedelta(days=30)
        )
        data = {"barcode": batch.barcode, "quantity": 5}
        serializer = SaleItemSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data["batch"] == batch
        assert serializer.validated_data["quantity"] == 5

    def test_invalid_barcode(self):
        """Test with non-existent barcode"""
        data = {"barcode": "INVALID123", "quantity": 1}
        serializer = SaleItemSerializer(data=data)
        with pytest.raises(ValidationError) as excinfo:
            serializer.is_valid(raise_exception=True)
        assert "This is not a valid batch barcode" in str(excinfo.value)

    def test_zero_stock(self):
        """Test with batch that has zero stock"""
        batch = BatchFactory(stock_units=0)
        data = {"barcode": batch.barcode, "quantity": 1}
        serializer = SaleItemSerializer(data=data)
        with pytest.raises(ValidationError) as excinfo:
            serializer.is_valid(raise_exception=True)
        assert "This batch stock is zero" in str(excinfo.value)

    def test_expired_batch(self):
        """Test with expired batch"""
        batch = BatchFactory(expiry_date=timezone.now().date() - timezone.timedelta(days=1))
        data = {"barcode": batch.barcode, "quantity": 1}
        serializer = SaleItemSerializer(data=data)
        with pytest.raises(ValidationError) as excinfo:
            serializer.is_valid(raise_exception=True)
        assert "This batch is expired" in str(excinfo.value)

    def test_quantity_exceeds_stock(self):
        """Test when quantity exceeds available stock"""
        batch = BatchFactory(
            stock_units=5,
            expiry_date=timezone.now().date() + timezone.timedelta(days=30)
        )
        data = {"barcode": batch.barcode, "quantity": 6}
        serializer = SaleItemSerializer(data=data)
        with pytest.raises(ValidationError) as excinfo:
            serializer.is_valid(raise_exception=True)
        assert f"We only have {batch.stock_units}" in str(excinfo.value)

    def test_exact_stock_quantity(self):
        """Test when quantity equals available stock"""
        batch = BatchFactory(
            stock_units=5,
            expiry_date=timezone.now().date() + timezone.timedelta(days=30)
        )
        data = {"barcode": batch.barcode, "quantity": 5}
        serializer = SaleItemSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data["quantity"] == 5

    def test_negative_quantity(self):
        """Test with negative quantity"""
        batch = BatchFactory(
            stock_units=10,
            expiry_date=timezone.now().date() + timezone.timedelta(days=30)
        )
        data = {"barcode": batch.barcode, "quantity": -1}
        serializer = SaleItemSerializer(data=data)
        with pytest.raises(ValidationError) as excinfo:
            serializer.is_valid(raise_exception=True)
        assert "Ensure this value is greater than or equal to 0" in str(excinfo.value)


@pytest.mark.django_db
class TestInvoiceCreationSerializer:
    def test_valid_invoice_creation(self):
        """Test creating an invoice with items"""
        med1 = MedicineFactory(price=Decimal('20.00'), units_per_pack=3)
        med2 = MedicineFactory(price=Decimal('30.00'), units_per_pack=2)
        
        batch1 = BatchFactory(medicine=med1, stock_units=9)
        batch2 = BatchFactory(medicine=med2, stock_units=6)
        data = {
            "items": [
                {"barcode": batch1.barcode, "quantity": 3},
                {"barcode": batch2.barcode, "quantity": 2},
            ],
            "payment_status": "paid",
            "discount": Decimal('10.00'),
        }
        serializer = InvoiceCreationSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        invoice = serializer.save()
        assert invoice.payment_status == "paid"
        assert invoice.sales_items.count() == 2
        # med1: (20.00 / 3) * 3 = 20.00, med2: (30.00 / 2) * 2 = 30.00, total = 50.00
        assert invoice.total_before_discount == Decimal('50.00')
        # 50.00 * (1 - 10/100) = 50.00 * 0.9 = 45.00
        assert invoice.total_after_discount == Decimal('45.00')
        assert invoice.sales_items.filter(batch=batch1, quantity=3).exists()
        assert invoice.sales_items.filter(batch=batch2, quantity=2).exists()
        batch1.refresh_from_db()
        batch2.refresh_from_db()
        assert batch1.stock_units == 6  # 9 - 3 = 6
        assert batch2.stock_units == 4  # 6 - 2 = 4

    def test_invoice_with_no_items(self):
        """Test invoice with no items should fail"""
        data = {
            "items": [],
            "payment_status": "paid",
            "discount": Decimal('5.00'),
        }
        serializer = InvoiceCreationSerializer(data=data)
        with pytest.raises(ValidationError) as excinfo:
            serializer.is_valid(raise_exception=True)
        assert "This list may not be empty" in str(excinfo.value)

    def test_invoice_with_invalid_items(self):
        """Test invoice with invalid items should fail"""
        batch = BatchFactory(stock_units=1)
        data = {
            "items": [{"barcode": batch.barcode, "quantity": 2}],
            "payment_status": "paid",
            "discount": Decimal('5.00'),
        }
        serializer = InvoiceCreationSerializer(data=data)
        with pytest.raises(ValidationError) as excinfo:
            serializer.is_valid(raise_exception=True)
        assert "We only have" in str(excinfo.value)

    def test_invoice_update_replace_items(self):
        """Test updating an invoice with new items"""
        invoice = InvoiceFactory(discount=Decimal('5.00'))
        med1 = MedicineFactory(price=Decimal('20.00'), units_per_pack=2)
        med2 = MedicineFactory(price=Decimal('30.00'), units_per_pack=3)
        batch1 = BatchFactory(medicine=med1, stock_units=10)
        SaleItemFactory(invoice=invoice, batch=batch1, quantity=1)
        batch2 = BatchFactory(medicine=med2, stock_units=6)
        
        # New data with one item
        data = {
            "items": [{"barcode": batch2.barcode, "quantity": 3}],
            "discount": Decimal('10.00'),
        }
        
        serializer = InvoiceCreationSerializer(invoice, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors
        updated_invoice = serializer.save()
        
        assert updated_invoice.discount == Decimal('10.00')
        assert updated_invoice.sales_items.count() == 1
        assert updated_invoice.sales_items.first().batch == batch2
        assert updated_invoice.sales_items.first().quantity == 3
        
        # med2: (30.00 / 3) * 3 = 30.00
        expected_total_before_discount = Decimal('30.00')
        # 30.00 * (1 - 10/100) = 30.00 * 0.9 = 27.00
        expected_total_after_discount = Decimal('27.00')
        
        assert updated_invoice.total_before_discount == expected_total_before_discount
        assert updated_invoice.total_after_discount == expected_total_after_discount

    def test_invoice_update_discount_only(self):
        """Test updating only discount"""
        invoice = InvoiceFactory(discount=Decimal('5.00'))
        med = MedicineFactory(price=Decimal('20.00'), units_per_pack=1)  # units_per_pack=1 for simplicity
        batch = BatchFactory(medicine=med, stock_units=10)
        SaleItemFactory(invoice=invoice, batch=batch, quantity=2)

        # Update the discount
        data = {"discount": Decimal('10.00')}
        serializer = InvoiceCreationSerializer(invoice, data=data, partial=True)

        assert serializer.is_valid(), serializer.errors
        updated_invoice = serializer.save()

        assert updated_invoice.discount == Decimal('10.00')
        assert updated_invoice.sales_items.count() == 1
        assert updated_invoice.sales_items.first().quantity == 2

        # med: (20.00 / 1) * 2 = 40.00
        expected_total_before_discount = Decimal('40.00')
        # 40.00 * (1 - 10/100) = 40.00 * 0.9 = 36.00
        expected_total_after_discount = Decimal('36.00')

        assert updated_invoice.total_before_discount == expected_total_before_discount
        assert updated_invoice.total_after_discount == expected_total_after_discount

    def test_invoice_update_payment_status_only(self):
        """Test updating only payment status"""
        invoice = InvoiceFactory(discount=Decimal('5.00'), payment_status="pending")
        batch = BatchFactory(stock_units=10)
        SaleItemFactory(invoice=invoice, batch=batch, quantity=1)
        data = {"payment_status": "paid"}
        serializer = InvoiceCreationSerializer(invoice, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors
        updated_invoice = serializer.save()
        assert updated_invoice.payment_status == "paid"
        assert updated_invoice.discount == Decimal('5.00')
        assert updated_invoice.sales_items.count() == 1

    def test_invalid_payment_status(self):
        """Test invalid payment status"""
        batch = BatchFactory(stock_units=10)
        data = {
            "items": [{"barcode": batch.barcode, "quantity": 1}],
            "payment_status": "invalid_status",
            "discount": Decimal('5.00'),
        }
        serializer = InvoiceCreationSerializer(data=data)
        with pytest.raises(ValidationError) as excinfo:
            serializer.is_valid(raise_exception=True)
        assert "is not a valid choice" in str(excinfo.value)

    def test_discount_too_large(self):
        """Test discount percentage exceeding max_digits"""
        batch = BatchFactory(stock_units=10)
        data = {
            "items": [{"barcode": batch.barcode, "quantity": 1}],
            "payment_status": "paid",
            "discount": Decimal('100.01'),
        }
        serializer = InvoiceCreationSerializer(data=data)
        with pytest.raises(ValidationError) as excinfo:
            serializer.is_valid(raise_exception=True)
        assert "Ensure that there are no more than 4 digits in total" in str(excinfo.value)

    def test_negative_discount(self):
        """Test negative discount percentage"""
        batch = BatchFactory(stock_units=10)
        data = {
            "items": [{"barcode": batch.barcode, "quantity": 1}],
            "payment_status": "paid",
            "discount": Decimal('-5.00'),
        }
        serializer = InvoiceCreationSerializer(data=data)
        with pytest.raises(ValidationError) as excinfo:
            serializer.is_valid(raise_exception=True)
        assert "Ensure this value is greater than or equal to 0" in str(excinfo.value)


@pytest.mark.django_db
class TestReturnInvoiceSerializer:
    def test_valid_invoice_id(self):
        """Test with valid invoice ID"""
        invoice = InvoiceFactory()
        data = {"invoice": str(invoice.id)}
        serializer = ReturnInvoiceSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data["invoice"] == invoice

    def test_invalid_invoice_id(self):
        """Test with non-existent invoice ID"""
        data = {"invoice": "999"}
        serializer = ReturnInvoiceSerializer(data=data)
        with pytest.raises(ValidationError) as excinfo:
            serializer.is_valid(raise_exception=True)
        assert "This is not a valid invoice ID" in str(excinfo.value)