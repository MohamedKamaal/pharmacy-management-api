import pytest
from django.db import IntegrityError
from orders.models import Order, OrderItem
from .factories import OrderFactory, OrderItemFactory
from medicine.tests.factories import MedicineFactory, SupplierFactory ,BatchFactory

@pytest.mark.django_db
def test_order_creation():
    """Test that an order is created with the correct supplier"""
    supplier = SupplierFactory.create(name="Test Supplier")
    order = OrderFactory.create(supplier=supplier)
    
    assert order.supplier == supplier
    assert order.total_before is None
    assert order.total_after is None

@pytest.mark.django_db
def test_order_update_totals():
    """Test that total_before and total_after are updated correctly"""
    order = OrderFactory.create()
    order_item_1 = OrderItemFactory.create(order=order, quantity=2, discount_integer=10)
    order_item_2 = OrderItemFactory.create(order=order, quantity=3, discount_integer=5)

    # Update the total_before and total_after
    order.total_before = sum(item.price_item for item in order.items.all())
    order.total_after = sum(item.price_item_after for item in order.items.all())

    order.save()

    assert order.total_before == (order_item_1.price_item + order_item_2.price_item)
    assert order.total_after == (order_item_1.price_item_after + order_item_2.price_item_after)

@pytest.mark.django_db
def test_order_item_creation():
    """Test that an order item is created with the correct details"""
    order_item = OrderItemFactory.create(quantity=2, discount_integer=10)

    assert order_item.quantity == 2
    assert order_item.discount_integer == 10
    assert order_item.price_item == int(2 * order_item.batch.medicine.price)
    assert order_item.price_item_after == int(
     2 * order_item.batch.medicine.price * (1 - order_item.discount_integer / 100)
)
@pytest.mark.django_db
def test_discount_property():
    """Test the discount property calculation"""
    order_item = OrderItemFactory.create(quantity=2, discount_integer=10)

    assert order_item.discount == 0.1

@pytest.mark.django_db
def test_price_item_after_property():
    """Test the price_item_after property calculation"""
    order_item = OrderItemFactory.create(quantity=2, discount_integer=10)
    expected_price_item_after = int(2 * order_item.batch.medicine.price * (1 - 0.1))  # 2 * price * (1 - discount)

    assert order_item.price_item_after == expected_price_item_after

@pytest.mark.django_db
def test_price_item_property():
    """Test the price_item property calculation"""
    order_item = OrderItemFactory.create(quantity=2, discount_integer=10)
    expected_price_item = int(2 * order_item.batch.medicine.price)  # 2 * price

    assert order_item.price_item == expected_price_item

@pytest.mark.django_db
def test_unique_order_item():
    """Test that the unique_together constraint on order and batch works"""
    order = OrderFactory.create()
    batch = BatchFactory.create()

    # Create the first OrderItem
    order_item_1 = OrderItemFactory.create(order=order, batch=batch)

    # Try to create a second OrderItem with the same order and batch (this should raise an IntegrityError)
    with pytest.raises(IntegrityError):
        OrderItemFactory.create(order=order, batch=batch)
