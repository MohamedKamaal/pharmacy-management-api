import factory 
from sales.models import Invoice, SaleItem
from medicine.tests.factories import SupplierFactory, BatchFactory
from decimal import Decimal
import random


class InvoiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Invoice
    discount = factory.LazyFunction(lambda: Decimal(str(round(random.uniform(5.0, 99.99), 2))))
    

    

class SaleItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SaleItem
    invoice= factory.SubFactory(InvoiceFactory)
    batch = factory.SubFactory(BatchFactory)
    quantity = factory.Faker("random_int", min=1, max=99)
