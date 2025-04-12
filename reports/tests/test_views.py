import pytest
from rest_framework import status
from rest_framework.test import APIClient
from medicine.models import Batch
from users.models import User
from django.utils.timezone import now
from datetime import timedelta
from medicine.tests.factories import BatchFactory

@pytest.fixture
def pharmacist_user():
    # Create a test pharmacist user
    return User.objects.create_user(
        email="pharmacist@example.com",  # Include the email argument
        password="password123",
        role="pharmacist"
    )

@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def create_batches():
    # Create some test batches
    BatchFactory(barcode="123456", expiry_date=now() - timedelta(days=1), stock_units=10)  # expired
    BatchFactory(barcode="789101", expiry_date=now() + timedelta(days=30), stock_units=0)  # out of stock
    BatchFactory(barcode="112233", expiry_date=now() + timedelta(days=30), stock_units=10)  # in stock
    BatchFactory(barcode="445566", expiry_date=now() + timedelta(days=90), stock_units=10)  # near expiry

@pytest.mark.django_db
def test_out_of_stock_batches(client, pharmacist_user, create_batches):
    # Authenticate as pharmacist
    client.force_authenticate(user=pharmacist_user)
    
    # Make a GET request to the view
    response = client.get("/reports/out-of-stock/")  # Adjust this path based on your urls
    
    # Check the status and returned data
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1  # Should only return the batch with stock_units=0
    assert response.data[0]["barcode"] == "789101"

@pytest.mark.django_db
def test_expired_batches(client, pharmacist_user, create_batches):
    # Authenticate as pharmacist
    client.force_authenticate(user=pharmacist_user)
    
    # Make a GET request to the view
    response = client.get("/reports/expired/")  # Adjust this path based on your urls
    
    # Check the status and returned data
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1  # Should only return the expired batch
    assert response.data[0]["barcode"] == "123456"

@pytest.mark.django_db
def test_near_expire_batches(client, pharmacist_user, create_batches):
    # Authenticate as pharmacist
    client.force_authenticate(user=pharmacist_user)
    
    # Make a GET request to the view with the `months` query parameter
    response = client.get("/reports/near-expiry/?months=1")  # Adjust this path based on your urls
    
    # Check the status and returned data
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1  # Should only return the batch near expiry (within 1 month)
    assert response.data[0]["barcode"] == "445566"
    
@pytest.mark.django_db
def test_near_expire_invalid_months(client, pharmacist_user, create_batches):
    # Authenticate as pharmacist
    client.force_authenticate(user=pharmacist_user)
    
    # Make a GET request to the view with an invalid `months` query parameter
    response = client.get("/reports/near-expiry/?months=invalid")  # Adjust this path based on your urls
    
    # Check for validation error
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid value for 'months'. It must be an integer." in str(response.data)
    
@pytest.mark.django_db
def test_near_expire_negative_months(client, pharmacist_user, create_batches):
    # Authenticate as pharmacist
    client.force_authenticate(user=pharmacist_user)
    
    # Make a GET request to the view with a negative `months` query parameter
    response = client.get("/reports/near-expiry/?months=-1")  # Adjust this path based on your urls
    
    # Check for validation error
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Months parameter must be a positive integer." in str(response.data)
