import pytest 
from medicine.serializers import MedicineInSerializer, MedicineOutSerializer, BatchInSerializer,BatchOutSerializer
from medicine.tests.factories import * 
from medicine.models import * 
from django.utils.timezone import now, timedelta 
from rest_framework import exceptions
from orders.serializers import OrderItemSerializer, OrderCreationSerializer
from orders.models import Order , OrderItem
from orders.tests.factories import *

@pytest.mark.django_db
class TestOrderCreationSerializer:

    def test_serializer_valid_input(self):
        supplier = SupplierFactory()
        medicine1 = MedicineFactory(units_per_pack=3)
        medicine2 = MedicineFactory(units_per_pack=3)
        
        
    
        
        packs = 10
        units = 0
        discount = 25.00

        data = {
            "supplier": supplier.id,
            "items": [
                {
                    "medicine": medicine1.name,
                    "packs": packs,
                    "units": units,
                    "discount": discount,
                    "expiry_date":"2028-02"
                },
                {
                    "medicine": medicine2.name,
                    "packs": packs + 5,
                    "units": units,
                    "discount": discount + 10.00,
                    "expiry_date":"2028-03"
                },
            ],
        }

        ser = OrderCreationSerializer(data=data)
        assert ser.is_valid(), ser.errors
        ser.save()

        assert Order.objects.count() == 1
        order = Order.objects.first()
        assert order.items.count() == 2
        assert order.total_before == sum(item.price_item for item in order.items.all())
        assert order.total_after == sum(item.price_item_after for item in order.items.all())
