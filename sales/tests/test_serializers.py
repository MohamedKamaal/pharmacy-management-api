import pytest
from decimal import Decimal
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from sales.models import Invoice, SaleItem
from medicine.models import Batch
from medicine.tests.factories import BatchFactory
from sales.tests.factories import SaleItemFactory, InvoiceFactory
from sales.serializers import SaleItemSerializer, InvoiceCreationSerializer


# Task
@pytest.mark.django_db
class TestSaleItemSerializer:
    def test_valid_data(self):
        """Test serializer with valid data"""
        batch = BatchFactory(stock_units=10, expiry_date=timezone.now().date() + timezone.timedelta(days=30))
        data = {
            "barcode": batch.barcode,
            "quantity": 5
        }
        serializer = SaleItemSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data["batch"] == batch
        assert serializer.validated_data["quantity"] == 5

    def test_invalid_barcode(self):
        """Test with non-existent barcode"""
        data = {
            "barcode": "INVALID123",
            "quantity": 1
        }
        serializer = SaleItemSerializer(data=data)
        with pytest.raises(ValidationError) as excinfo:
            serializer.is_valid(raise_exception=True)
        assert "This is not a valid batch barcode" in str(excinfo.value)

    def test_zero_stock(self):
        """Test with batch that has zero stock"""
        batch = BatchFactory(stock_units=0)
        data = {
            "barcode": batch.barcode,
            "quantity": 1
        }
        serializer = SaleItemSerializer(data=data)
        with pytest.raises(ValidationError) as excinfo:
            serializer.is_valid(raise_exception=True)
        assert "This batch stock is zero" in str(excinfo.value)

    def test_expired_batch(self):
        """Test with expired batch"""
        batch = BatchFactory(expiry_date=timezone.now() - timezone.timedelta(days=1))
        data = {
            "barcode": batch.barcode,
            "quantity": 1
        }
        serializer = SaleItemSerializer(data=data)
        with pytest.raises(ValidationError) as excinfo:
            serializer.is_valid(raise_exception=True)
        assert "This batch is expired" in str(excinfo.value)
    # Task
    def test_quantity_exceeds_stock(self):
        """Test when quantity exceeds available stock"""
        batch = BatchFactory(stock_units=5, expiry_date=timezone.now().date() + timezone.timedelta(days=30))
        data = {
            "barcode": batch.barcode,
            "quantity": 6
        }
        serializer = SaleItemSerializer(data=data)
        with pytest.raises(ValidationError) as excinfo:
            serializer.is_valid(raise_exception=True)
        assert f"We only have {batch.stock_units}" in str(excinfo.value)
    # tASK
    def test_create_sale_item(self):
        """Test creating a sale item"""
        batch = BatchFactory(stock_units=10, expiry_date=timezone.now().date() + timezone.timedelta(days=30))
        invoice = InvoiceFactory(discount_integer = 1000)
        data = {
            "barcode": batch.barcode,
            "quantity": 3
        }
        serializer = SaleItemSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        sale_item = serializer.save(invoice=invoice)
        
        assert sale_item.batch == batch
        assert sale_item.quantity == 3
        assert sale_item.invoice == invoice
        assert not hasattr(sale_item, 'barcode')  # barcode should be removed

    def test_update_not_allowed(self):
        """Test that updates are not allowed"""
        sale_item = SaleItemFactory()
        serializer = SaleItemSerializer()
        with pytest.raises(ValidationError) as excinfo:
            serializer.update(sale_item, {})
        assert "Updating sale items is not allowed" in str(excinfo.value)


@pytest.mark.django_db
class TestInvoiceCreationSerializer:
    def test_valid_invoice_creation(self):
        """Test creating an invoice with items"""
        batch1 = BatchFactory(stock_units=10)
        batch2 = BatchFactory(stock_units=5)
        data = {
            "items": [
                {"barcode": batch1.barcode, "quantity": 2},
                {"barcode": batch2.barcode, "quantity": 3},
            ],
            "payment_status": "paid",
            "discount_percentage": Decimal("10.00"),
        }
        serializer = InvoiceCreationSerializer(data=data)
        assert serializer.is_valid()
        invoice = serializer.save()
        
        assert invoice.payment_status == "paid"
        assert invoice.discount_integer == 1000  # 10.00 * 100
        assert invoice.sales_items.count() == 2
        assert invoice.total_before_discount > 0
        assert invoice.total_after_discount > 0
        assert invoice.total_after_discount < invoice.total_before_discount

    def test_invoice_with_no_items(self):
        """Test invoice with no items should fail"""
        data = {
            "items": [],
            "payment_status": "paid",
            "discount_percentage": Decimal("5.00"),
        }
        serializer = InvoiceCreationSerializer(data=data)
        with pytest.raises(ValidationError) as excinfo:
            serializer.is_valid(raise_exception=True)
        assert "This list may not be empty" in str(excinfo.value)

    def test_invoice_with_invalid_items(self):
        """Test invoice with invalid items should fail"""
        batch = BatchFactory(stock_units=1)
        data = {
            "items": [
                {"barcode": batch.barcode, "quantity": 2},  # Quantity exceeds stock
            ],
            "payment_status": "paid",
            "discount_percentage": Decimal("5.00"),
        }
        serializer = InvoiceCreationSerializer(data=data)
        with pytest.raises(ValidationError) as excinfo:
            serializer.is_valid(raise_exception=True)
        assert "We only have" in str(excinfo.value)

    def test_invoice_update(self):
        """Test updating an invoice"""
        invoice = InvoiceFactory(discount_integer=500)  # 5%
        batch1 = BatchFactory(stock_units=10)
        SaleItemFactory(invoice=invoice, batch=batch1, quantity=1)
        
        batch2 = BatchFactory(stock_units=5)
        data = {
            "items": [
                {"barcode": batch2.barcode, "quantity": 3},
            ],
            "discount_percentage": Decimal("15.00"),
        }
        serializer = InvoiceCreationSerializer(invoice, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors
        updated_invoice = serializer.save()
        
        assert updated_invoice.discount_integer == 1500  # 15.00 * 100
        assert updated_invoice.sales_items.count() == 1
        assert updated_invoice.sales_items.first().batch == batch2

    def test_invoice_update_without_items(self):
        """Test updating just discount without changing items"""
        invoice = InvoiceFactory(discount_integer=500)  # 5%
        SaleItemFactory(invoice=invoice)  # Create at least one item
        data = {
            "discount_percentage": Decimal("10.00"),
        }
        serializer = InvoiceCreationSerializer(invoice, data=data, partial=True)
        assert serializer.is_valid()
        updated_invoice = serializer.save()
        
        assert updated_invoice.discount_integer == 1000  # 10.00 * 100
        assert updated_invoice.sales_items.exists()  # Original items still there

    def test_discount_percentage_validation(self):
        """Test discount percentage validation"""
        batch = BatchFactory(stock_units=10)
        data = {
            "items": [{"barcode": batch.barcode, "quantity": 1}],
            "payment_status": "paid",
            "discount_percentage": Decimal("100.01"),  # > 100%
        }
        serializer = InvoiceCreationSerializer(data=data)
        with pytest.raises(ValidationError) as excinfo:
            serializer.is_valid(raise_exception=True)
        assert "Ensure that there are no more than 4 digits in total." in str(excinfo.value)