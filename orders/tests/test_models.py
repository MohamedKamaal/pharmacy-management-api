import pytest
from django.db import IntegrityError
from orders.models import Order, OrderItem
from .factories import OrderFactory, OrderItemFactory
from medicine.tests.factories import MedicineFactory, SupplierFactory ,BatchFactory
from decimal import Decimal
# tests.py
import pytest
from django.db import IntegrityError
from decimal import Decimal
from decimal import Decimal, ROUND_HALF_UP

from .factories import OrderFactory, OrderItemFactory, BatchFactory

@pytest.mark.django_db
def test_order_update_totals():
    """Test that total_before and total_after are updated correctly"""
    order = OrderFactory.create()
    order_item_1 = OrderItemFactory.create(order=order, quantity=2, discount=10)
    order_item_2 = OrderItemFactory.create(order=order, quantity=3, discount=5)

    # Save order to update totals
    order.save()

    # Ensure that calculations are done using Decimal values
    total_before = (order_item_1.price_item_before + order_item_2.price_item_before)
    total_after = (order_item_1.price_item_after + order_item_2.price_item_after)

    assert order.total_before == total_before
    assert order.total_after == total_after


@pytest.mark.django_db
def test_order_item_creation():
    """Test that an order item is created with the correct details"""
    order_item = OrderItemFactory.create(quantity=2, discount=10)

    assert order_item.quantity == 2
    assert order_item.discount == Decimal('10')  # Ensure it's compared with Decimal

    # Use Decimal when comparing price calculations
    expected_price_item_before = Decimal(2) * order_item.batch.medicine.unit_price
    assert order_item.price_item_before == expected_price_item_before


@pytest.mark.django_db
def test_price_item_after_property():
    """Test the price_item_after property calculation"""
    order_item = OrderItemFactory.create(quantity=2, discount=10)

    total = Decimal(2) * order_item.batch.medicine.unit_price * (Decimal(1) - Decimal('0.10'))
    total = total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)  # Save the rounded value
    assert order_item.price_item_after == total


@pytest.mark.django_db
def test_price_item_property():
    """Test the price_item property calculation"""
    order_item = OrderItemFactory.create(quantity=2, discount=10)

    # Ensure you're using Decimal for price calculation
    total = Decimal(order_item.quantity) * order_item.batch.medicine.unit_price
    total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    assert order_item.price_item_before == total


@pytest.mark.django_db
def test_unique_order_item():
    """Test that the unique_together constraint on order and batch works"""
    order = OrderFactory.create()
    batch = BatchFactory.create()

    # Ensuring unique constraint is respected
    order_item_1 = OrderItemFactory.create(order=order, batch=batch)

    # Attempting to create a duplicate OrderItem should raise an IntegrityError
    with pytest.raises(IntegrityError):
        OrderItemFactory.create(order=order, batch=batch)
