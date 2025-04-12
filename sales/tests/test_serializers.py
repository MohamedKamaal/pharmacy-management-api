import pytest 
from medicine.serializers import MedicineInSerializer, MedicineOutSerializer, BatchInSerializer,BatchOutSerializer
from medicine.tests.factories import * 
from medicine.models import * 
from django.utils.timezone import now, timedelta 
from rest_framework import exceptions
from sales.serializers import InvoiceCreationSerializer
from sales.models import Invoice, SaleItem

from orders.tests.factories import *

@pytest.mark.django_db
class TestOrderCreationSerializer:

    def test_serializer_valid_input(self):
    
        discount = 25.00
        barcode1 = BatchFactory(units_per_pack=3)
        barcode2 = BatchFactory(units_per_pack=3)
        
        
    
        
        

        data = {
            "discount": 25,
            "payment_status":"paid",
            "items": [
                {
                    "barcode": barcode1,
                    "quantity": 5
        
                },
                {
                    "barcode": barcode2,
                    "quantity": 10
                },
            ],
        }

        ser = InvoiceCreationSerializer(
            data=data
        )
        assert ser.is_valid(), ser.errors
        ser.save()

        assert Invoice.objects.count() == 1
        order = Order.objects.first()
        assert order.items.count() == 2
        assert order.total_before == sum(item.price_item for item in order.items.all())
        assert order.total_after == sum(item.price_item_after for item in order.items.all())
