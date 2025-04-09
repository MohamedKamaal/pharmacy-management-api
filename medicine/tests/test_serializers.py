import pytest 
from medicine.serializers import MedicineInSerializer, MedicineOutSerializer, BatchInSerializer,BatchOutSerializer
from medicine.tests.factories import * 
from medicine.models import * 
from django.utils.timezone import now, timedelta 
from rest_framework import exceptions

@pytest.mark.django_db
class TestMedicineSerializer():
    
    def test_in_serializer_valid_input(self):
        active_ingredient = ActiveIngredientFactory(name="Paracetamol")
        category = CategoryFactory(name="oral")
        manufacturer = ManufacturerFactory(name="biomed")
        data = {
            "international_barcode":2344522334337,
            "units_per_pack":3,
            "whole_price":99.99,
            "active_ingredient":active_ingredient.id,
            "category":category.id,
            "manufacturer":manufacturer.id
        }
        ser = MedicineInSerializer(data=data)
        assert ser.is_valid(), ser.errors
        ser.save()
        
        # check for creation of medicine 
        assert Medicine.objects.count() == 1
        medicine = Medicine.objects.get(international_barcode = data["international_barcode"])
        assert medicine.price_cents == data["whole_price"] * 100
        
        # test update 
        data2 = {
            "whole_price":55.55,
           
        }
        ser = MedicineInSerializer(data= data2, instance=medicine, partial=True)
        ser.is_valid()
        ser.save()
        assert medicine.price_cents == data2["whole_price"] * 100

    def test_outserializer_valid(self):
        active_ingredient = ActiveIngredientFactory(name="Paracetamol")
        category = CategoryFactory(name="oral")
        manufacturer = ManufacturerFactory(name="Pfizer")
        med = MedicineFactory(active_ingredient = active_ingredient, category=category, manufacturer = manufacturer)
        ser = MedicineOutSerializer(med)

        assert ser.data == {
            "id":med.id,
            "active_ingredient":med.active_ingredient.name,
            "manufacturer":med.manufacturer.name,
            "category":med.category.name,
            "units_per_pack":med.units_per_pack,
            "price":med.price,
            "stock":med.stock,
            "international_barcode":med.international_barcode
        }, ser.data
        

@pytest.mark.django_db
class TestBatchSerializer():
    def test_inserializer_valid_data_pass(self):
        med = MedicineFactory(units_per_pack = 3)
        data = {
            "expiry_date":(now() + timedelta(days=10)).date(), 
            "packs":1,
            "units":2,
           
        }
        
        ser = BatchInSerializer(data=data)
        assert ser.is_valid(), ser.errors
        ser.save(medicine=med)
      
        assert Batch.objects.count() == 1 
        assert med.batches.count() == 1
    
    def test_inserializer_invalid_date_fail(self):
        med = MedicineFactory(units_per_pack = 3)
        data = {
            "expiry_date":(now() - timedelta(days=10)).date(), 
            "packs":1,
            "units":2,
           
        }
        
        ser = BatchInSerializer(data=data)
        assert not ser.is_valid(), ser.errors

    def test_inserializer_invalid_date_fail(self):
        med = MedicineFactory(units_per_pack = 3)
        data = {
            "expiry_date":(now() - timedelta(days=10)).date(), 
            "packs":1,
            "units":2,
           
        }
        
        ser = BatchInSerializer(data=data)
        assert not ser.is_valid(), ser.errors

    def test_inserializer_one_pack_fail(self):
        med = MedicineFactory(units_per_pack = 1)
        data = {
            "expiry_date":(now() +timedelta(days=10)).date(), 
            "packs":1,
            "units":2,
           
        }
        
        ser = BatchInSerializer(data=data)
        assert ser.is_valid(), ser.errors
        with pytest.raises(exceptions.ValidationError):
            ser.save(medicine = med)
            
            
    def test_outserializer(self):
        med = MedicineFactory(units_per_pack=3)
        batch = BatchFactory(stock_units=13, medicine=med, expiry_date=(now()+ timedelta(days=10)).date())
        
      
        ser = BatchOutSerializer(batch)
        assert ser.data == {
            "expiry_date":batch.expiry_date.isoformat(),
            "medicine":batch.medicine.name,
            "stock_packets": f"4:1"
        }