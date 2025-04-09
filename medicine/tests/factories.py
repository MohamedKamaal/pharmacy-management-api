import factory
from cities_light.models import City
from pytest_factoryboy import register
import random 
from medicine.models import Supplier, Manufacturer, Category, ActiveIngredient, Medicine, Batch, generate_barcode
from phonenumber_field.phonenumber import PhoneNumber
from cities_light.models import Country
from faker import Faker

EGYPT_MOBILE_PREFIXES = ["010", "011", "012", "015"]  # Vodafone, Orange, Etisalat, WE
class SupplierFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Supplier
    name = factory.Faker('name')
   
    address = factory.Faker('address')
    @factory.lazy_attribute
    def city(self):
        cities_ids = City.objects.values_list("id",flat=True)
        return City.objects.get(id=random.choice(list(cities_ids)))
    

    @factory.lazy_attribute
    def phone_number(self):
        prefix = random.choice(EGYPT_MOBILE_PREFIXES)
        number = f"{prefix}{random.randint(10000000, 99999999)}"  # Make it 11 digits total
        return PhoneNumber.from_string(f"+20{number[1:]}", region="EG")  # Drop the leading 0 for international for


fake = Faker()

class ManufacturerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Manufacturer

    name = factory.Faker("name")
    phone_number = factory.LazyFunction(lambda: fake.phone_number())  # Random phone number
    address = factory.Faker("address")

    @factory.lazy_attribute
    def country(self):
        country = factory.LazyAttribute(lambda x: fake.country_code())
        return country
    @factory.lazy_attribute
    def website(self):
        website = f"https://www.{self.name}.com"
        return website
    
class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Faker("name")
    parent = None
   

    
class ActiveIngredientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ActiveIngredient

    name = factory.Faker("name")
   
   

class MedicineFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Medicine
    name = factory.Faker("name")

    active_ingredient = factory.SubFactory(ActiveIngredientFactory)
    category = factory.SubFactory(CategoryFactory)
    manufacturer = factory.SubFactory(ManufacturerFactory)
    units_per_pack = factory.Faker("random_int", min=1, max=5)
    price_cents = factory.Faker("random_int", min=100, max=100000)
    @factory.lazy_attribute
    def international_barcode(self):
    
        # To adjust the length to exactly 16 digits (if required), you can do this:
        international_barcode = generate_barcode()
        return international_barcode
     
class BatchFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Batch
  

    medicine = factory.SubFactory(MedicineFactory)
    expiry_date = factory.Faker('date_between', start_date='today', end_date='+5y')
    stock_units = factory.Faker("random_int", min=1, max=100)
    @factory.lazy_attribute
    def barcode(self):
    
        # To adjust the length to exactly 16 digits (if required), you can do this:
        barcode = generate_barcode()
        return barcode
     
    