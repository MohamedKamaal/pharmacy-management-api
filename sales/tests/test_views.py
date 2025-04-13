import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from decimal import Decimal

from users.tests.factories import UserFactory
from medicine.tests.factories import BatchFactory, MedicineFactory
from sales.models import Invoice, SaleItem


@pytest.fixture
def cashier_user():
    return UserFactory(role="cashier")


@pytest.fixture
def non_cashier_user():
    return UserFactory(role="customer")


@pytest.fixture
def auth_client(cashier_user):
    client = APIClient()
    client.force_authenticate(user=cashier_user)
    return client


@pytest.fixture
def unauth_client():
    return APIClient()



@pytest.mark.django_db
def test_create_invoice_success(auth_client):
    # Set up a batch with stock units available
    medicine = MedicineFactory(price=30.00,units_per_pack=3)
    batch = BatchFactory(medicine = medicine, stock_units=3)
    
    # Define valid data for creating an invoice
    data = {
        "items": [
            {"barcode": batch.barcode, "quantity": 2}
        ],
        "payment_status": "paid",
        "discount": 50.00,
    }
    
    url = reverse("invoice-list")
    response = auth_client.post(url, data, format="json")
    
    print(response.data)
    print(f"Generated expiry_date: {batch.expiry_date}")


    # Assert that the invoice creation is successful
    assert response.status_code == status.HTTP_201_CREATED
    assert Invoice.objects.count() == 1
    invoice = Invoice.objects.first()
    
    # Check invoice details
    assert invoice.payment_status == "paid"
    assert invoice.discount == Decimal("50.00")
    assert invoice.total_before_discount == Decimal("20.00")
    assert invoice.total_after_discount == Decimal("10.00")
    
    # Check stock update
    batch.refresh_from_db()
    assert batch.stock_units == 1  # 10 - 2 items sold


@pytest.mark.django_db
def test_retrieve_invoice_success(auth_client):
    # Create a batch and invoice as setup
    medicine = MedicineFactory(price=30.00, units_per_pack=3)
    batch = BatchFactory(medicine=medicine, stock_units=3)
    invoice = Invoice.objects.create(
        payment_status="paid",
        discount=Decimal(50.00),
        total_before_discount=Decimal("20.00"),
  
    )
    SaleItem.objects.create(invoice=invoice, batch=batch, quantity=2)

    url = reverse("invoice-detail", kwargs={"pk": invoice.pk})
    response = auth_client.get(url)

    # Assert the response status is OK and check the invoice details
    assert response.status_code == status.HTTP_200_OK
    assert response.data["payment_status"] == "paid"
    assert response.data["discount"] == ('50.00')
    assert response.data["total_before_discount"] == ('20.00')
    assert response.data["total_after_discount"] == Decimal('10.00')

@pytest.mark.django_db
def test_update_invoice_success(auth_client):
    # Create initial invoice
    medicine = MedicineFactory(price=30.00, units_per_pack=3)
    batch = BatchFactory(medicine=medicine, stock_units=3)
    invoice = Invoice.objects.create(
        payment_status="paid",
        discount=Decimal("50.00"),
        total_before_discount=Decimal("20.00"),
      
    )
    SaleItem.objects.create(invoice=invoice, batch=batch, quantity=2)

    url = reverse("invoice-detail", kwargs={"pk": invoice.pk})
    data = {
        "payment_status": "paid",  # Updating status
        "discount": "30.00",  # New discount
        "items": [{"barcode": batch.barcode, "quantity": 1}],
    }
    response = auth_client.put(url, data, format="json")

    # Assert the response status is OK
    assert response.status_code == status.HTTP_200_OK
    # Verify updated invoice details
    invoice.refresh_from_db()
    assert invoice.payment_status == "paid"
    assert invoice.discount == Decimal("30.00")

@pytest.mark.django_db
def test_delete_invoice_success(auth_client):
    # Create initial invoice
    medicine = MedicineFactory(price=30.00, units_per_pack=3)
    batch = BatchFactory(medicine=medicine, stock_units=3)
    invoice = Invoice.objects.create(
        payment_status="paid",
        discount=Decimal("50.00"),
        total_before_discount=Decimal("20.00"),
  
    )
    SaleItem.objects.create(invoice=invoice, batch=batch, quantity=2)

    url = reverse("invoice-detail", kwargs={"pk": invoice.pk})
    response = auth_client.delete(url)

    # Assert the response status is OK
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Invoice.objects.count() == 0

@pytest.mark.django_db
def test_create_invoice_unauthorized(non_cashier_user, unauth_client):
    # Set up a batch with stock units available
    medicine = MedicineFactory(price=30.00, units_per_pack=3)
    batch = BatchFactory(medicine=medicine, stock_units=3)
    
    # Define valid data for creating an invoice
    data = {
        "items": [
            {"barcode": batch.barcode, "quantity": 2}
        ],
        "payment_status": "paid",
        "discount": "50.00",
    }
    
    url = reverse("invoice-list")
    unauth_client.force_authenticate(user=non_cashier_user)
    response = unauth_client.post(url, data, format="json")

    # Assert that the user cannot create an invoice
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
def test_return_invoice_success(auth_client):
    # Create a batch and invoice as setup
    medicine = MedicineFactory(price=30.00,units_per_pack=3)
    batch = BatchFactory(medicine = medicine, stock_units=3)
    
    # Define valid data for creating an invoice
    data = {
        "items": [
            {"barcode": batch.barcode, "quantity": 2}
        ],
        "payment_status": "paid",
        "discount": "50.00",
    }
    
    url = reverse("invoice-list")
    response = auth_client.post(url, data, format="json")


    # Verify that invoice has associated sale items

    url = reverse("invoice-return")
    invoice = Invoice.objects.first()
    data = {"invoice": invoice.id}
    response = auth_client.post(url, data, format="json")

    # Assert the response status is OK and the payment status is updated
    assert response.status_code == status.HTTP_200_OK
    invoice.refresh_from_db()
    batch.refresh_from_db()
    assert batch.stock_units == 3
    assert invoice.payment_status == "refunded"
