# tests/test_supplier.py

import pytest
from medicine.tests.factories import SupplierFactory, ManufacturerFactory, CategoryFactory, ActiveIngredientFactory, MedicineFactory, BatchFactory
from medicine.models import Supplier, Manufacturer, Category, ActiveIngredient, Medicine, Batch, generate_barcode
from cities_light.models import Country, City
from django.db import IntegrityError
from phonenumber_field.phonenumber import PhoneNumber
from django.utils.timezone import now , timedelta
from django.core.exceptions import ValidationError

@pytest.mark.django_db
class TestSupplierModel:

    def test_create_supplier(self):
        country = Country.objects.create(name='Egypt', code2='EG')
        city = City.objects.create(name='Cairo', country=country) 
        supplier = SupplierFactory(city=city)
        assert isinstance(supplier, Supplier)
        assert supplier.name is not None
        assert supplier.phone_number is not None
        assert isinstance(supplier.phone_number, PhoneNumber)
        

    def test_same_supplier_fail(self):
        name="farco"
        country = Country.objects.create(name='Egypt', code2='EG')
        city = City.objects.create(name='Cairo', country=country) 
        supplier1 = SupplierFactory(city=city,name=name)
        assert supplier1.__str__() == name
        with pytest.raises(IntegrityError):

            
            supplier2 = SupplierFactory(city=city, name=name)


@pytest.mark.django_db
class TestManufacturerModel:

    def test_create_manufacturer(self):
        manufacturer = ManufacturerFactory()
        
        assert Manufacturer.objects.count() == 1
        assert manufacturer.name
        assert manufacturer.website.startswith("https://")
        assert manufacturer.phone_number  # Make sure a phone number is generated
        assert manufacturer.country  # Ensure a country is assigned
         # Ensure the country has a name
    
    def test_same_manufacturer_fail(self):
        name="farco"
        manufacturer1 = ManufacturerFactory(name=name)
        assert manufacturer1.__str__() == name
        with pytest.raises(IntegrityError):

            
            manufacturer2 = ManufacturerFactory( name=name)

@pytest.mark.django_db
class TestCategoryModel:

    def test_create_Category(self):
        oral = CategoryFactory(name="oral")
        
        assert Category.objects.count() == 1
        assert oral.name == "oral"
        assert oral.__str__() == "oral"
        assert oral.parent is None

        tablets = CategoryFactory(name="tablets")
        tablets.parent = oral 
        
        assert tablets.parent == oral

    def test_same_category_fail(self):
        name="oral"
        cat1 = CategoryFactory(name=name)
        with pytest.raises(IntegrityError):

            
            cat2 = CategoryFactory(name=name)

    
  
@pytest.mark.django_db
class TestActiveIngredientModel:

    def test_create_active_ingredient(self):
        para = ActiveIngredientFactory(name="Paracetamol")
        
        assert ActiveIngredient.objects.count() == 1
        assert para.name == "Paracetamol"
        assert para.__str__() == "Paracetamol"

    
    def test_same_active_ingredient_fail(self):
        name="Paracetamol"
        act1 = ActiveIngredientFactory(name=name)
        with pytest.raises(IntegrityError):

            act2 = ActiveIngredientFactory(name=name)

@pytest.mark.django_db
class TestMedicineModel:

    def test_create_med(self):
        med = MedicineFactory()
        assert med.price == med.price_cents/100
        assert med.__str__() == med.name 
        
       
        
    
    def test_same_med_name_fail(self):
        name="Panadol 500 mg 30 tablets"
        med1 = MedicineFactory(name=name)
        with pytest.raises(IntegrityError):

            med2 = MedicineFactory(name=name)

    def test_same_med_barcode_fail(self):
        barcode = generate_barcode()
        med1 = MedicineFactory(international_barcode=barcode)
        with pytest.raises(IntegrityError):

            med2 = MedicineFactory(international_barcode =barcode)

@pytest.mark.django_db
class TestBatchModel:

    def test_create_batch(self):
        med = MedicineFactory(name="panadol advance",units_per_pack=3)
        batch = BatchFactory(
            medicine = med,
            stock_units = 13,
            expiry_date = now() + timedelta(10)
        )
       
        assert batch.stock_packets == "4:1"
        assert med.stock == "4:1"
        assert Batch.objects.count() == 1 
        assert batch.__str__() == f"panadol advance-{batch.expiry_date}"
        
        batch2 = BatchFactory(
            medicine = med,
            stock_units = 13,
            expiry_date = now() + timedelta(15)
        )
        assert med.stock == "8:2"
        with pytest.raises(IntegrityError):
            batch.stock_units = -2
            batch.save()

  
       
        
    
    def test_same_barcode_fail(self):
        barcode = generate_barcode()
   
        medicine = MedicineFactory(name="panadol advance",units_per_pack=3)
        batch1 = BatchFactory(barcode=barcode,medicine = medicine)

        with pytest.raises(ValidationError):
            batch = Batch(
                barcode = barcode,
                medicine = medicine,
                expiry_date = now()+ timedelta(10)
            )

            batch.full_clean()
            batch.save()
            
    def test_invalid_date_fail(self):
        barcode = generate_barcode()
   
        medicine = MedicineFactory(name="panadol advance",units_per_pack=3)

        with pytest.raises(ValidationError):
            batch = Batch(
                barcode = barcode,
                medicine = medicine,
                expiry_date = now() - timedelta(10)
            )
        
            batch.full_clean()
            batch.save()