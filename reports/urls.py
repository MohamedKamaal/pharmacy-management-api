from django.urls import path
from .views import OutOfStockAPIView, ExpiredAPIView, NearExpireAPIView

urlpatterns = [
    path('out-of-stock/', OutOfStockAPIView.as_view(), name='out-of-stock'),
    path('expired/', ExpiredAPIView.as_view(), name='expired'),
    path('near-expiry/', NearExpireAPIView.as_view(), name='near-expiry'),
]