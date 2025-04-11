import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from orders.models import Order
from medicine.tests.factories import MedicineFactory, SupplierFactory
from orders.tests.factories import OrderFactory, OrderItemFactory
from rest_framework import status
from users.tests.factories import UserFactory


@pytest.mark.django_db
class TestOrderAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user = UserFactory(role="pharmacist")
        self.client.force_authenticate(user=self.user)
        self.supplier = SupplierFactory()

    def test_create_order(self):
        med1 = MedicineFactory(units_per_pack=2)
        med2 = MedicineFactory(units_per_pack=3)

        url = reverse("order-list")

        payload = {
            "supplier": self.supplier.id,
            "items": [
                {
                    "medicine": med1.name,
                    "packs": 2,
                    "units": 1,
                    "discount": 5.00,
                    "expiry_date": "2027-10"
                },
                {
                    "medicine": med2.name,
                    "packs": 1,
                    "units": 0,
                    "discount": 10.00,
                    "expiry_date": "2027-11"
                }
            ]
        }

        response = self.client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert Order.objects.count() == 1
        assert Order.objects.first().items.count() == 2

    def test_list_orders(self):
        OrderFactory.create_batch(3)

        url = reverse("order-list")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

    def test_retrieve_order(self):
        order = OrderFactory()
        url = reverse("order-detail", args=[order.id])

        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
       
    def test_update_order_supplier(self):
        order = OrderFactory()
        new_supplier = SupplierFactory()

        url = reverse("order-detail", args=[order.id])
        response = self.client.patch(url, {"supplier": new_supplier.id}, format="json")

        assert response.status_code == status.HTTP_200_OK
        order.refresh_from_db()
        assert order.supplier.id == new_supplier.id

    def test_delete_order(self):
        order = OrderFactory()
        url = reverse("order-detail", args=[order.id])

        response = self.client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Order.objects.filter(id=order.id).count() == 0
