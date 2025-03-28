from django.urls import path
from orders.views import * 


urlpatterns = [
    path("", OrderListCreateAPIView.as_view(),name="order-list"),
    path("<int:id>/",OrderRetrieveUpdateDestroyAPIView.as_view(), name="order-detail"),
]