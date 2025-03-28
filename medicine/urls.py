from django.urls import path
from medicine.views import (
    MedicineListAPIView, SimilarMedicinesAPIView, MedicineBatchesListAPIView,
    BatchRetrieveUpdateDestroyAPIView, MedicineRetrieveUpdateDestroyAPIView
)


urlpatterns = [
    path("",MedicineListAPIView.as_view(), name="medicine-list"),
    path("<int:id>/",MedicineRetrieveUpdateDestroyAPIView.as_view(), name="medicine-detail"),
    path("<int:id>/similars",SimilarMedicinesAPIView.as_view(), name="medicine-similars"),
    path("<int:id>/batches/",MedicineBatchesListAPIView.as_view(), name="medicine-batches"),
    path("<int:id>/similars",SimilarMedicinesAPIView.as_view(), name="medicine-similars"),
    path("<int:medicine_id>/<int:batch_id>/",BatchRetrieveUpdateDestroyAPIView.as_view(), name="batch-detail"),
    
]