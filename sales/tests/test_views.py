import pytest
from decimal import Decimal
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from sales.models import Invoice, SaleItem
from users.tests.factories import UserFactory
from sales.tests.factories import InvoiceFactory, SaleItemFactory
from medicine.tests.factories import BatchFactory
from datetime import timedelta
from django.utils import timezone

@pytest.fixture
def pharmacist_user():
    return UserFactory(role="pharmacist")

@pytest.fixture
def auth_client(pharmacist_user):
    client = APIClient()
    client.force_authenticate(user=pharmacist_user)
    return client

@pytest.mark.django_db
def test_create_invoice(auth_client):
    batch = BatchFactory(stock_units=10)

    data = {
        "items": [{"barcode": batch.barcode, "quantity": 2}],
        "payment_status": "paid",
        "discount_percentage": "10.00",
    }

    url = reverse("invoice-list")
    response = auth_client.post(url, data, format="json")

    assert response.status_code == 201
    assert Invoice.objects.count() == 1
    assert SaleItem.objects.count() == 1

@pytest.mark.django_db
def test_list_invoices(auth_client):
    InvoiceFactory.create_batch(3)

    url = reverse("invoice-list")
    response = auth_client.get(url)

    assert response.status_code == 200
    assert len(response.data) >= 3

@pytest.mark.django_db
def test_retrieve_invoice(auth_client):
    invoice = InvoiceFactory()
    url = reverse("invoice-detail", kwargs={"pk": invoice.id})  # Corrected kwargs
    response = auth_client.get(url)

    assert response.status_code == 200
    assert response.data["id"] == invoice.id

@pytest.mark.django_db
def test_update_invoice(auth_client):
    invoice = InvoiceFactory(discount_integer=500)
    old_item = SaleItemFactory(invoice=invoice, quantity=1)
    batch = BatchFactory(stock_units=10)

    data = {
        "items": [{"barcode": batch.barcode, "quantity": 4}],
        "payment_status": "partially_paid",
        "discount_percentage": "15.00"
    }

    url = reverse("invoice-detail", kwargs={"pk": invoice.id})  # Corrected kwargs
    response = auth_client.patch(url, data)

    assert response.status_code == 200
    invoice.refresh_from_db()
    assert invoice.discount_integer == 1500
    assert invoice.payment_status == "partially_paid"
    assert invoice.sales_items.count() == 1
    assert invoice.sales_items.first().batch == batch

@pytest.mark.django_db
def test_delete_invoice(auth_client):
    invoice = InvoiceFactory()
    url = reverse("invoice-detail", kwargs={"pk": invoice.id})  # Corrected kwargs
    response = auth_client.delete(url)

    assert response.status_code == 204
    assert not Invoice.objects.filter(id=invoice.id).exists()

@pytest.mark.django_db
def test_unauthenticated_user_cannot_access():
    client = APIClient()
    url = reverse("invoice-list")
    response = client.get(url)
    assert response.status_code in [401, 403]

@pytest.mark.django_db
def test_create_invoice_with_empty_items(auth_client):
    data = {
        "items": [],
        "payment_status": "paid",
        "discount_percentage": "5.00"
    }
    url = reverse("invoice-list")
    response = auth_client.post(url, data)

    assert response.status_code == 400
    assert "items" in response.data

@pytest.mark.django_db
def test_create_invoice_with_invalid_barcode(auth_client):
    data = {
        "items": [{"barcode": "nonexistent-barcode", "quantity": 1}],
        "payment_status": "paid",
        "discount_percentage": "0.00"
    }
    url = reverse("invoice-list")
    response = auth_client.post(url, data, format="json")

    assert response.status_code == 400
    assert "barcode" in str(response.data)

@pytest.mark.django_db
def test_create_invoice_with_quantity_exceeding_stock(auth_client):
    batch = BatchFactory(stock_units=2)

    data = {
        "items": [{"barcode": batch.barcode, "quantity": 5}],  # more than available
        "payment_status": "paid",
        "discount_percentage": "0.00"
    }

    url = reverse("invoice-list")
    response = auth_client.post(url, data)

    assert response.status_code == 400
    assert "quantity" in str(response.data)

@pytest.mark.django_db
def test_create_invoice_with_expired_batch(auth_client):
    expired_batch = BatchFactory(expiry_date=timezone.now().date() - timedelta(days=1), stock_units=10)

    data = {
        "items": [{"barcode": expired_batch.barcode, "quantity": 1}],
        "payment_status": "paid",
        "discount_percentage": "0.00"
    }

    url = reverse("invoice-list")
    response = auth_client.post(url, data)

    assert response.status_code == 400
    assert "expired" in str(response.data).lower()
