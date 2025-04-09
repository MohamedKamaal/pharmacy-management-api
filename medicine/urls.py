from django.urls import path
from medicine.views import (
    MedicineListCreateAPIView, SimilarMedicinesAPIView, MedicineBatchesListCreateAPIView,
    BatchRetrieveUpdateDestroyAPIView, MedicineRetrieveUpdateDestroyAPIView
)


urlpatterns = [
    path("",MedicineListCreateAPIView.as_view(), name="medicine-list"),
    path("<int:pk>/",MedicineRetrieveUpdateDestroyAPIView.as_view(), name="medicine-detail"),
    path("<int:id>/similars/",SimilarMedicinesAPIView.as_view(), name="medicine-similars"),
    path("<int:id>/batches/",MedicineBatchesListCreateAPIView.as_view(), name="medicine-batches"),
    path("<int:medicine_id>/<int:batch_id>/",BatchRetrieveUpdateDestroyAPIView.as_view(), name="batch-detail"),
    
]