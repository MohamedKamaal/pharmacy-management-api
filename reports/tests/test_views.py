import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.utils.timezone import  now
from datetime import timedelta
from users.tests.factories import UserFactory
from medicine.tests.factories import BatchFactory

@pytest.fixture
def pharmacist_user():
    return UserFactory(role="pharmacist")

@pytest.fixture
def non_pharmacist_user():
    return UserFactory(role="cashier")

@pytest.fixture
def auth_client(pharmacist_user):
    client = APIClient()
    client.force_authenticate(user=pharmacist_user)
    return client

@pytest.fixture
def unauth_client():
    return APIClient()

@pytest.mark.django_db
class TestOutOfStockAPIView:
    """Tests for OutOfStockAPIView"""

    def test_get_out_of_stock_authenticated(self, auth_client):
        bat1 = BatchFactory(stock_units=0)  # Out of stock
        bat2 = BatchFactory(stock_units=10)  # In stock

        url = reverse('out-of-stock')
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert bat1.medicine.name in response.data[0]["medicine"], response.data
    def test_get_out_of_stock_unauthenticated(self, unauth_client):
        url = reverse('out-of-stock')
        response = unauth_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_out_of_stock_non_pharmacist(self, auth_client, non_pharmacist_user):
        auth_client.force_authenticate(user=non_pharmacist_user)
        url = reverse('out-of-stock')
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_out_of_stock_empty(self, auth_client):
        BatchFactory(stock_units=10)  # In stock
        url = reverse('out-of-stock')
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

@pytest.mark.django_db
class TestExpiredAPIView:
    """Tests for ExpiredAPIView"""

    def test_get_expired_authenticated(self, auth_client):
        BatchFactory(expiry_date=now().date() - timedelta(days=1))  # Expired
        BatchFactory(expiry_date=now().date() + timedelta(days=1))  # Not expired

        url = reverse('expired')
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['expiry_date'] <= str(now().date())

    def test_get_expired_unauthenticated(self, unauth_client):
        url = reverse('expired')
        response = unauth_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_expired_non_pharmacist(self, auth_client, non_pharmacist_user):
        auth_client.force_authenticate(user=non_pharmacist_user)
        url = reverse('expired')
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_expired_empty(self, auth_client):
        BatchFactory(expiry_date=now().date() + timedelta(days=1))
        url = reverse('expired')
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

@pytest.mark.django_db
class TestNearExpireAPIView:
    """Tests for NearExpireAPIView"""

    def test_get_near_expire_default_month(self, auth_client):
        BatchFactory(expiry_date=now().date() + timedelta(days=15))  # Within 1 month
        BatchFactory(expiry_date=now().date() + timedelta(days=45))  # Beyond 1 month

        url = reverse('near-expiry')
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_get_near_expire_custom_month(self, auth_client):
        BatchFactory(expiry_date=now().date() + timedelta(days=45))  # Within 2 months
        BatchFactory(expiry_date=now().date() + timedelta(days=90))  # Beyond 2 months

        url = reverse('near-expiry')
        response = auth_client.get(f"{url}?months=2")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_get_near_expire_invalid_months(self, auth_client):
        url = reverse('near-expiry')

        response = auth_client.get(f"{url}?months=-1")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        response = auth_client.get(f"{url}?months=invalid")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_near_expire_unauthenticated(self, unauth_client):
        url = reverse('near-expiry')
        response = unauth_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_near_expire_non_pharmacist(self, auth_client, non_pharmacist_user):
        auth_client.force_authenticate(user=non_pharmacist_user)
        url = reverse('near-expiry')
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_near_expire_empty(self, auth_client):
        BatchFactory(expiry_date=now().date() + timedelta(days=90))  # Not near expiry
        url = reverse('near-expiry')
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0
