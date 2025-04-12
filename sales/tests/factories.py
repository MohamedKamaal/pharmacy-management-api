import factory 
from sales.models import Invoice, SaleItem
from medicine.tests.factories import SupplierFactory, BatchFactory




class InvoiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Invoice
    discount_integer = factory.Faker("random_int", min=1, max=100)
    

    

class SaleItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SaleItem
    invoice= factory.SubFactory(InvoiceFactory)
    batch = factory.SubFactory(BatchFactory)
    quantity = factory.Faker("random_int", min=1, max=100)
