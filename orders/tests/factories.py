import factory 
from orders.models import OrderItem, Order
from medicine.tests.factories import SupplierFactory, BatchFactory




class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order
    supplier = factory.SubFactory(SupplierFactory)
    
    

class OrderItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrderItem
    order = factory.SubFactory(OrderFactory)
    batch = factory.SubFactory(BatchFactory)
    quantity = factory.Faker("random_int", min=1, max=100)
    discount_integer = factory.Faker("random_int", min=1, max=100)
