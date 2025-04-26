# tests/test_supplier.py

import pytest
from medicine.tests.factories import SupplierFactory, ManufacturerFactory, CategoryFactory, ActiveIngredientFactory, MedicineFactory, BatchFactory
from medicine.models import Supplier, Manufacturer, Category, ActiveIngredient, Medicine, Batch, generate_barcode
from cities_light.models import Country, City
from django.db import IntegrityError
from phonenumber_field.phonenumber import PhoneNumber
from django.utils.timezone import now , timedelta
from django.core.exceptions import ValidationError
from decimal import Decimal 


@pytest.mark.django_db
class TestSupplierModel:

    def test_create_supplier(self):
        country = Country.objects.create(name='Egypt', code2='EG')
        city = City.objects.create(name='Cairo', country=country)
        supplier = SupplierFactory(city=city)

        assert isinstance(supplier, Supplier)
        assert supplier.name
        assert supplier.phone_number
        assert isinstance(supplier.phone_number, PhoneNumber)
        assert supplier.__str__() == supplier.name

    def test_same_supplier_name_fails(self):
        country = Country.objects.create(name='Egypt', code2='EG')
        city = City.objects.create(name='Cairo', country=country)
        name = "Farco"
        SupplierFactory(city=city, name=name)

        with pytest.raises(IntegrityError):
            SupplierFactory(city=city, name=name)


@pytest.mark.django_db
class TestManufacturerModel:

    def test_create_manufacturer(self):
        manufacturer = ManufacturerFactory()
        assert manufacturer.name
        assert manufacturer.phone_number
        assert manufacturer.country
        assert manufacturer.website.startswith("https://")
        assert Manufacturer.objects.count() == 1

    def test_same_manufacturer_name_fails(self):
        name = "Farco"
        ManufacturerFactory(name=name)

        with pytest.raises(IntegrityError):
            ManufacturerFactory(name=name)

    def test_same_website_fails(self):
        url = "https://example.com"
        ManufacturerFactory(website=url)

        with pytest.raises(IntegrityError):
            ManufacturerFactory(website=url)


@pytest.mark.django_db
class TestCategoryModel:

    def test_create_category_and_hierarchy(self):
        parent = CategoryFactory(name="oral")
        child = CategoryFactory(name="tablets", parent=parent)

        assert Category.objects.count() == 2
        assert child.parent == parent
        assert parent.__str__() == "oral"
        assert child.__str__() == "tablets"

    def test_same_category_name_fails(self):
        name = "oral"
        CategoryFactory(name=name)

        with pytest.raises(IntegrityError):
            CategoryFactory(name=name)


@pytest.mark.django_db
class TestActiveIngredientModel:

    def test_create_active_ingredient(self):
        ingredient = ActiveIngredientFactory(name="Paracetamol")

        assert ActiveIngredient.objects.count() == 1
        assert ingredient.name == "Paracetamol"
        assert ingredient.__str__() == "Paracetamol"

    def test_same_active_ingredient_name_fails(self):
        name = "Paracetamol"
        ActiveIngredientFactory(name=name)

        with pytest.raises(IntegrityError):
            ActiveIngredientFactory(name=name)


@pytest.mark.django_db
class TestMedicineModel:

    def test_create_medicine(self):
        med = MedicineFactory()

       
        assert med.__str__() == med.name
        assert isinstance(med.stock, str)
        assert isinstance(med.unit_price, Decimal)

    def test_same_name_fails(self):
        name = "Panadol 500 mg"
        MedicineFactory(name=name)

        with pytest.raises(IntegrityError):
            MedicineFactory(name=name)

    def test_same_barcode_fails(self):
        barcode = generate_barcode()
        MedicineFactory(international_barcode=barcode)

        with pytest.raises(IntegrityError):
            MedicineFactory(international_barcode=barcode)


@pytest.mark.django_db
class TestBatchModel:

    def test_create_batch_and_stock_logic(self):
        med = MedicineFactory(units_per_pack=3)
        batch = BatchFactory(medicine=med, stock_units=13, expiry_date=now() + timedelta(days=10))

        assert batch.stock_packets == "4:1"
        assert med.stock == "4:1"
        assert batch.__str__() == f"{med.name}-{batch.expiry_date}"
        assert Batch.objects.count() == 1

        # Add a second batch
        batch2 = BatchFactory(medicine=med, stock_units=13, expiry_date=now() + timedelta(days=15))
        assert med.stock == "8:2"

    def test_negative_stock_units_fails(self):
        med = MedicineFactory(units_per_pack=2)
        batch = BatchFactory.build(medicine=med, stock_units=-5, expiry_date=now() + timedelta(days=10))

        with pytest.raises(ValidationError):
            batch.full_clean()

    def test_duplicate_barcode_fails(self):
        med = MedicineFactory(units_per_pack=3)
        barcode = generate_barcode()
        BatchFactory(barcode=barcode, medicine=med)

        with pytest.raises(ValidationError):
            duplicate = Batch(barcode=barcode, medicine=med, expiry_date=now() + timedelta(days=10), stock_units=5)
            duplicate.full_clean()

    def test_invalid_expiry_date_fails(self):
        med = MedicineFactory(units_per_pack=3)
        batch = Batch(barcode=generate_barcode(), medicine=med, expiry_date=now() - timedelta(days=5), stock_units=5)

        with pytest.raises(ValidationError):
            batch.full_clean()
