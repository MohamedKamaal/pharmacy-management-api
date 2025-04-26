from django.urls import path
from medicine.views import (
    MedicineListCreateAPIView, SimilarMedicinesAPIView, MedicineBatchesListCreateAPIView,
    BatchRetrieveUpdateDestroyAPIView, MedicineRetrieveUpdateDestroyAPIView,
    CategoryListCreateAPIView,ActiveIngredientListCreateAPIView,SupplierListCreateAPIView,ManufacturerListCreateAPIView
)


urlpatterns = [
    path("suppliers/",SupplierListCreateAPIView.as_view(), name="supplier-list"),
    path("active_ingredients/",ActiveIngredientListCreateAPIView.as_view(), name="active_ingredient-list"),
    path("manufacturers/",ManufacturerListCreateAPIView.as_view(), name="manufacturer-list"),
    path("categories/",CategoryListCreateAPIView.as_view(), name="category-list"),
    path("",MedicineListCreateAPIView.as_view(), name="medicine-list"),
    path("<int:pk>/",MedicineRetrieveUpdateDestroyAPIView.as_view(), name="medicine-detail"),
    path("<int:id>/similars/",SimilarMedicinesAPIView.as_view(), name="medicine-similars"),
    path("<int:id>/batches/",MedicineBatchesListCreateAPIView.as_view(), name="medicine-batches"),
    path("<int:medicine_id>/<int:batch_id>/",BatchRetrieveUpdateDestroyAPIView.as_view(), name="batch-detail"),
    
]