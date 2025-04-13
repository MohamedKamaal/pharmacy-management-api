import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from medicine.models import Medicine
from users.tests.factories import UserFactory 
from medicine.tests.factories import * 
from django.utils.timezone import now , timedelta
from django.db import IntegrityError
from django.core.exceptions import ValidationError




@pytest.mark.django_db
class TestMedicineAPI:
    def setup_method(self):
        self.client = APIClient()
        
        self.user = UserFactory(role="pharmacist")
        self.client.force_authenticate(user=self.user)
        self.url = reverse("medicine-list")


    
    
    
    def test_search(self):
        med = MedicineFactory(name="Panadol 500mg")
        res = self.client.get(self.url, kwargs={"search":"pana"})
        assert res.status_code == 200 
        assert med.name ==  res.data["results"][0]["name"]
        
       
    def test_add_medicine(self):
        ingredient = ActiveIngredientFactory()
        category = CategoryFactory()
        manufacturer = ManufacturerFactory()
        data = {
            "name": "Paracetamol",
            "international_barcode":"23456789854663",
            "active_ingredient": ingredient.id,
            "category": category.id,
            "manufacturer": manufacturer.id,
            "units_per_pack":3,
            "price":99.99
            
        }
        response = self.client.post(self.url, data)
        assert response.status_code == 201
        assert Medicine.objects.filter(name="Paracetamol").exists()

    def test_list_medicines(self):
        MedicineFactory.create_batch(3)
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 3

    def test_get_medicine(self):
        med = MedicineFactory()
        url = reverse("medicine-detail",kwargs={"pk":med.id})
        response = self.client.get(url)
        assert response.status_code == 200
        assert med.name == response.data["name"]
        
    def test_update_medicine(self):
        med = MedicineFactory()
        url = reverse("medicine-detail",kwargs={"pk":med.id})
        response = self.client.patch(url,data={"whole_price":99.99})
        assert response.status_code == 200
        assert med.name == response.data["name"]
        
    def test_remove_medicine(self):
        med = MedicineFactory()
        url = reverse("medicine-detail",kwargs={"pk":med.id})
        response = self.client.delete(url)
        assert response.status_code == 204
        assert Medicine.objects.count() == 0
        
    def test_similar_medicines(self):
        
        active = ActiveIngredientFactory(name="Paracetamol")
        category = CategoryFactory(name="oral")
        med1 = MedicineFactory(active_ingredient = active, category=category)
        med2 = MedicineFactory(active_ingredient = active, category=category)
        url = reverse("medicine-similars",kwargs={"id":med1.id})
        response = self.client.get(url)
        assert response.status_code == 200
        assert len(response.data['similars']) == 1
      
@pytest.mark.django_db
class TestBatchAPI:
    def setup_method(self):
        self.client = APIClient()
        
        self.user = UserFactory(role="pharmacist")
        self.client.force_authenticate(user=self.user)
        self.url = reverse("medicine-list")


    def test_list_batches(self):
        # create batches
        med = MedicineFactory()
        batch1 = BatchFactory(medicine=med)
        batch2 = BatchFactory(medicine=med)

        url = reverse("medicine-batches",kwargs={"id":med.id})
        res = self.client.get(url)
        assert res.status_code == 200 
        assert (res.data["count"]) == 2 

    def test_create_batches(self):
        med = MedicineFactory()
        data = {
            "packs":4,
            "units":0,
            "expiry_date": "2028-05"
            
        }
        url = reverse("medicine-batches",kwargs={"id":med.id})
        res = self.client.post(url, data=data)
        print(res.status_code)
        print(res.json())
        assert res.status_code == 201 , res
    
        with pytest.raises(IntegrityError):
            data = {
            "packs":3,
            "units":0,
            "expiry_date": "2028-05"
            
                }
            res = self.client.post(url, data=data)

        data = {
        "packs":3,
        "units":0,
        "expiry_date": "202805"
        
            }
        res = self.client.post(url, data=data)
        assert res.status_code == 400
        
    def update_batches(self):
        med = MedicineFactory(units_per_pack=3)
        batch = BatchFactory(medicine=med, stock_units=10)
        data = {
            "packs":4,
            "units":0,
            
        }
        url = reverse("batch-detail",kwargs={"medicine_id":med.id, "batch_id":batch.id})
        res = self.client.patch(url, data=data)
        assert batch.stock_units == 12
        assert res.status_code == 200

            
    def test_delete_batch(self):
        med = MedicineFactory(units_per_pack=3)
        batch = BatchFactory(medicine=med, stock_units=10)
        
        url = reverse("batch-detail",kwargs={"medicine_id":med.id, "batch_id":batch.id})
        res = self.client.delete(url)
        assert Batch.objects.count() == 0
    
        assert res.status_code == 204
    
    def test_get_batch(self):
        med = MedicineFactory(units_per_pack=3)
        batch = BatchFactory(medicine=med, stock_units=10)
        url = reverse("batch-detail",kwargs={"medicine_id":med.id, "batch_id":batch.id})
        res = self.client.get(url)
        assert res.status_code == 200
        assert batch.stock_packets == res.data["stock_packets"]

@pytest.mark.django_db
class TestMedicineAPIExtended:
    def setup_method(self):
        self.client = APIClient()
        self.pharmacist = UserFactory(role="pharmacist")
        self.cashier = UserFactory(role="cashier")
        self.unauthenticated_client = APIClient()
        self.client.force_authenticate(user=self.pharmacist)
        self.url = reverse("medicine-list")

    def test_permission_denied_for_cashier(self):
        self.client.force_authenticate(user=self.cashier)
        ingredient = ActiveIngredientFactory()
        category = CategoryFactory()
        manufacturer = ManufacturerFactory()
        data = {
            "name": "Paracetamol",
            "international_barcode":234567898543,
            "active_ingredient": ingredient.id,
            "category": category.id,
            "manufacturer": manufacturer.id,
            "units_per_pack":3,
            "price":99.99
            
        }
        response = self.client.post(self.url, data=data)
        assert response.status_code == 403  # Forbidden for non-pharmacists

    def test_permission_denied_for_unauthenticated_user(self):
        response = self.unauthenticated_client.get(self.url)
        assert response.status_code == 401  # Unauthorized

    def test_medicine_pagination(self):
        MedicineFactory.create_batch(30)  # more than one page
        response = self.client.get(self.url + "?page=1")
        assert response.status_code == 200
        assert "results" in response.data
        assert len(response.data["results"]) <= 10  # default page size (if set in pagination)

        # check next page
        response2 = self.client.get(self.url + "?page=2")
        assert response2.status_code == 200

    def test_search_by_name(self):
        med = MedicineFactory(name="Zyrtec")
        response = self.client.get(self.url + "?search=zyr")
        assert response.status_code == 200
        assert any(m["name"] == "Zyrtec" for m in response.data["results"])

    def test_search_by_active_ingredient(self):
        active = ActiveIngredientFactory(name="Ibuprofen")
        med = MedicineFactory(active_ingredient=active)
        response = self.client.get(self.url + "?search=ibu")
        assert response.status_code == 200
        assert any(m["name"] == med.name for m in response.data["results"])

    def test_search_by_category(self):
        category = CategoryFactory(name="painkillers")
        med = MedicineFactory(category=category)
        response = self.client.get(self.url + "?search=pain")
        assert response.status_code == 200
        assert any(m["name"] == med.name for m in response.data["results"])
