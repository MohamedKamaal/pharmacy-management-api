""" Views:
    - CRUD views for all medicine-related models
    - Specialized views for medicine batches and similar medicines """
from django.shortcuts import render, get_object_or_404



from users.permissions import IsPharmacist
from medicine.models import Medicine, Batch, ActiveIngredient, Manufacturer, Supplier, Category
from medicine.serializers import MedicineInSerializer, MedicineOutSerializer, BatchInSerializer, BatchOutSerializer,ActiveIngredientSerializer,CategorySerializer,ManufacturerSerializer,SupplierSerializer
from rest_framework import generics
from medicine.paginations import MedicinePagination
from rest_framework.response import Response
from rest_framework import status
from rest_framework.filters import SearchFilter
from django.http import Http404

# Create your views here.


class ActiveIngredientListCreateAPIView(generics.ListCreateAPIView):
    """API endpoint for listing and creating ActiveIngredients."""
    permission_classes = [IsPharmacist]
    queryset = ActiveIngredient.objects.all()
    serializer_class = ActiveIngredientSerializer


class ManufacturerListCreateAPIView(generics.ListCreateAPIView):
    """API endpoint for listing and creating Manufacturers."""
    permission_classes = [IsPharmacist]
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer


class SupplierListCreateAPIView(generics.ListCreateAPIView):
    """API endpoint for listing and creating Suppliers."""
    permission_classes = [IsPharmacist]
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer


class CategoryListCreateAPIView(generics.ListCreateAPIView):
    """API endpoint for listing and creating Categories."""
    permission_classes = [IsPharmacist]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class MedicineListCreateAPIView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating Medicines.
    
    Features:
    - Search functionality
    - Custom pagination
    - Different serializers for GET vs POST
    """
    filter_backends = [SearchFilter]
    search_fields = ['name', 'active_ingredient', 'category']
    permission_classes = [IsPharmacist]
    pagination_class = MedicinePagination
    queryset = Medicine.objects.select_related("active_ingredient", "category")

    def get_serializer_class(self):
        """Use MedicineOutSerializer for GET, MedicineInSerializer for POST."""
        if self.request.method == "GET":
            return MedicineOutSerializer
        return MedicineInSerializer


class MedicineRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, and deleting individual Medicines.
    """
    permission_classes = [IsPharmacist]
    queryset = Medicine.objects.select_related("active_ingredient", "category")

    def get_serializer_class(self):
        """Use MedicineOutSerializer for GET, MedicineInSerializer for others."""
        if self.request.method == "GET":
            return MedicineOutSerializer
        return MedicineInSerializer


class SimilarMedicinesAPIView(generics.GenericAPIView):
    """
    API endpoint for finding medicines with the same active ingredient and category.
    """
    permission_classes = [IsPharmacist]
    
    def get(self, request, id):
        """Get similar medicines based on active ingredient and category."""
        medicine = get_object_or_404(Medicine, id=id)
        active_ingredient = medicine.active_ingredient
        category = medicine.category
        
        similars = Medicine.objects.select_related("active_ingredient", "category")\
            .exclude(id=id)\
            .filter(active_ingredient=active_ingredient, category=category)
        
        if similars.exists():
            serializer = MedicineOutSerializer(similars, many=True)
            return Response(
                {"similars": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(
            {"similars": "No similar medicines"},
            status=status.HTTP_204_NO_CONTENT
        )


class MedicineBatchesListCreateAPIView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating Batches for a specific Medicine.
    """
    permission_classes = [IsPharmacist]
    pagination_class = MedicinePagination
    
    def get_queryset(self):
        """Get batches for the specified medicine ID."""
        id = self.kwargs.get("id", None)
        medicine = get_object_or_404(Medicine, id=id)
        return medicine.batches.all()

    def get_serializer_class(self):
        """Use BatchOutSerializer for GET, BatchInSerializer for POST."""
        if self.request.method == "GET":
            return BatchOutSerializer
        return BatchInSerializer
    
    def perform_create(self, serializer):
        """Associate new batch with the specified medicine."""
        id = self.kwargs.get("id", None)
        medicine = get_object_or_404(Medicine, id=id) 
        serializer.save(medicine=medicine)


class BatchRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, and deleting individual Batches.
    """
    permission_classes = [IsPharmacist]
    
    def get_serializer_class(self):
        """Use BatchOutSerializer for GET, BatchInSerializer for others."""
        if self.request.method == "GET":
            return BatchOutSerializer
        return BatchInSerializer
    
    def get_object(self):
        """Get batch ensuring it belongs to the specified medicine."""
        med_id = self.kwargs.get("medicine_id")
        batch_id = self.kwargs.get("batch_id")

        obj = get_object_or_404(Batch, id=batch_id)
        if obj.medicine.id == med_id:
            return obj
        raise Http404("Batch does not belong to the specified medicine.")

    def perform_update(self, serializer):
        """Ensure batch remains associated with the same medicine on update."""
        med_id = self.kwargs.get("medicine_id")
        medicine = get_object_or_404(Medicine, id=med_id)
        serializer.save(medicine=medicine)