"""
Order URL Configuration

Defines URL routes for order-related API endpoints.
"""

from django.urls import path
from orders.views import OrderListCreateAPIView, OrderRetrieveUpdateDestroyAPIView


urlpatterns = [
    path("", OrderListCreateAPIView.as_view(), name="order-list"),
    path("<int:pk>/", OrderRetrieveUpdateDestroyAPIView.as_view(), name="order-detail"),
]