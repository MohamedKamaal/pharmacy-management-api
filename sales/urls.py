from django.urls import path
from sales.views import * 


urlpatterns = [
    path("", InvoiceListCreateAPIView.as_view(),name="invoice-list"),
    path("<int:pk>/",InvoiceRetrieveUpdateDestroyAPIView.as_view(), name="invoice-detail"),
    path("<int:pk>/return/",ReturnInvoiceAPIView.as_view(), name="invoice-return"),
]