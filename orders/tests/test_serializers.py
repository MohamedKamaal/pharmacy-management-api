import pytest
from decimal import Decimal
from medicine.serializers import MedicineInSerializer, MedicineOutSerializer, BatchInSerializer, BatchOutSerializer
from medicine.tests.factories import *
from medicine.models import *
from django.utils.timezone import now, timedelta
from rest_framework import exceptions
from orders.serializers import OrderItemSerializer, OrderCreationSerializer
from orders.models import Order, OrderItem
from orders.tests.factories import *
from rest_framework.exceptions import ValidationError
@pytest.mark.django_db
class TestOrderCreationSerializer:

    def test_serializer_valid_input(self):
        supplier = SupplierFactory()
        medicine1 = MedicineFactory(units_per_pack=3)
        medicine2 = MedicineFactory(units_per_pack=3)
        
        packs = 10
        units = 0
        discount = Decimal('25.00')

        data = {
            "supplier": supplier.id,
            "items": [
                {
                    "medicine": medicine1.name,
                    "packs": packs,
                    "units": units,
                    "discount": discount,
                    "expiry_date": "2028-02"
                },
                {
                    "medicine": medicine2.name,
                    "packs": packs + 5,
                    "units": units,
                    "discount": discount + Decimal('10.00'),
                    "expiry_date": "2028-03"
                },
            ],
        }

        ser = OrderCreationSerializer(data=data)
        assert ser.is_valid(), ser.errors
        order = ser.save()

        assert Order.objects.count() == 1
        assert order.items.count() == 2
        assert order.total_before == round(sum(item.price_item_before for item in order.items.all()), 2)
        assert order.total_after == round(sum(item.price_item_after for item in order.items.all()), 2)


    def test_create_order_with_items(self):
        """Test creating an order with items"""
        medicine = MedicineFactory.create(units_per_pack=10)
        supplier = SupplierFactory()

        data = {
            "supplier": supplier.id,
            "items": [
                {
                    "medicine": medicine.name,
                    "packs": 2,
                    "units": 5,
                    "discount": Decimal('10.00'),
                    "expiry_date": "2025-06",
                }
            ],
        }

        serializer = OrderCreationSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

        order = serializer.save()
        assert order.items.count() == 1
        assert order.items.first().quantity == 25  # 5 + (2 * 10)
        assert order.total_before is not None
        assert order.total_after is not None


    def test_update_order_items(self):
        """Test updating the items of an order"""
        order = OrderFactory.create()
        medicine = MedicineFactory.create(units_per_pack=10)
        order_item = OrderItemFactory(order=order)

        data = {
            "items": [
                {
                    "medicine": medicine.name,
                    "packs": 2,
                    "units": 5,
                    "discount": Decimal(10.00),
                    "expiry_date": "2025-06",
                }
            ],
        }

        serializer = OrderCreationSerializer(order, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors

        order_updated = serializer.save()
        assert order_updated.items.count() == 1
        assert order_updated.items.first().quantity == 25  # 5 + (2 * 10)


    def test_invalid_update_order_items(self):
        """Test that providing invalid items causes an error"""
        order = OrderFactory()
        supplier = SupplierFactory()
        data = {
            "supplier":supplier.id,
            "items": [
                {
                    "medicine": "Non-existing medicine",  # This should trigger an error
                    "packs": 2,
                    "units": 5,
                    "discount": Decimal('10.00'),
                    "expiry_date": "2025-06",
                   
                }
            ],
        }

        serializer = OrderCreationSerializer(instance=order, data=data)
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)
            serializer.save()


    def test_total_calculation(self):
        """Test that total_before and total_after are calculated correctly"""
        medicine = MedicineFactory.create(units_per_pack=10,price=Decimal(100.00))
        supplier = SupplierFactory()

        data = {
            "supplier": supplier.id,
            "items": [
                {
                    "medicine": medicine.name,
                    "packs": 2,
                    "units": 5,
                    "discount": Decimal('10.00'),
                    "expiry_date": "2025-06",
                }
            ],
        }

        serializer = OrderCreationSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

        order = serializer.save()
        assert order.total_before == Decimal('250.00')  # Assuming price per unit, adjust if needed
        assert order.total_after == Decimal('225.00')  # Assuming 10% discount


@pytest.mark.django_db
class TestOrderItemSerializer:

    def test_validate_units_per_pack(self):
        """Test validation when units exceed allowed limit for a medicine"""
        medicine = MedicineFactory(units_per_pack=1)
        data = {
            "medicine": medicine.name,
            "packs": 1,
            "units": 2,
            "discount": Decimal('0.00'),
            "expiry_date": "2025-06",
        }

        serializer = OrderItemSerializer(data=data)
        with pytest.raises(exceptions.ValidationError):
            serializer.is_valid(raise_exception=True)


    def test_calculate_quantity(self):
        """Test that the quantity is calculated correctly"""
        medicine = MedicineFactory.create(units_per_pack=10)
        data = {
            "medicine": medicine.name,
            "packs": 2,
            "units": 5,
            "discount": Decimal('10.00'),
            "expiry_date": "2025-06",
        }

        serializer = OrderItemSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

        validated_data = serializer.validated_data
        expected_quantity = 5 + (2 * 10)  # 5 + 20 = 25
        assert validated_data['quantity'] == expected_quantity


    def test_create_batch_on_order_item_creation(self):
        """Test that batch is created or updated correctly"""
        medicine = MedicineFactory.create(units_per_pack=10)
        supplier = SupplierFactory()
        data = {
            "items":
                [
                    {
                    "medicine": medicine.name,
                    "packs": 2,
                    "units": 5,
                    "discount": Decimal('10.00'),
                    "expiry_date": "2025-06",
                    }
                ],
                "supplier":supplier.id
            
        }

        serializer = OrderCreationSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        
        # Call the create method and check if the batch was created
        order = serializer.save()
        batch = Batch.objects.get(medicine=medicine, expiry_date="2025-06-01")
        assert batch.stock_units == 25  # 5 + (2 * 10)


    def test_update_order_item_not_allowed(self):
        order_item = OrderItemFactory()
        data = {
            "medicine": order_item.batch.medicine.name,
            "packs": 2,
            "units": 5,
            "discount": Decimal("10.00"),
            "expiry_date": "2025-06",
        }

        serializer = OrderItemSerializer(order_item, data=data)
        with pytest.raises(ValidationError, match="Updating order items is not allowed."):
            assert serializer.is_valid()  # ensure it passes validation
            serializer.save() 
