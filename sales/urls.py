from django.urls import path
from sales.views import * 


urlpatterns = [
    path("", InvoiceListCreateAPIView.as_view(),name="inovice-list"),
    path("<int:id>/",InvoiceRetrieveUpdateDestroyAPIView.as_view(), name="invoice-detail"),
]