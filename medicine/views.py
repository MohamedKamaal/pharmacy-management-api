""" add medicine , edit medicine ,remove medicine , list medicines, search for medicine """
from django.shortcuts import render, get_object_or_404
from users.permissions import IsPharmacist
from medicine.models import Medicine, Batch
from medicine.serializers import MedicineInSerializer, MedicineOutSerializer, BatchInSerializer, BatchOutSerializer
from rest_framework import generics
from medicine.paginations import MedicinePagination
from rest_framework.response import Response
from rest_framework import status
from rest_framework.filters import SearchFilter

# Create your views here.

class MedicineListAPIView(generics.ListCreateAPIView):
    filter_backends = [SearchFilter]
    search__fields = ['name','active_ingredient','category']
    permission_classes = [IsPharmacist]
    pagination_class = MedicinePagination
    queryset = Medicine.objects.select_related("active_ingredient","category")

    def get_serializer_class(self) -> MedicineOutSerializer | MedicineInSerializer:
        if self.request.method == "GET":
            return MedicineInSerializer
        else:
            return MedicineInSerializer
    


class MedicineRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsPharmacist]

    def get_serializer_class(self) -> MedicineOutSerializer | MedicineInSerializer:
        if self.request.method == "GET":
            return MedicineOutSerializer
        else:
            return MedicineInSerializer
    
    queryset = Medicine.objects.select_related("active_ingredient","category")
    


    

class SimilarMedicinesAPIView(generics.GenericAPIView):
    permission_classes = [IsPharmacist]
    def get(self, request, id):
        medicine = get_object_or_404(Medicine, id=id)
        active_ingredient = medicine.active_ingredient
        category = medicine.category
        similars = Medicine.objects.select_related("active_ingredient","category").exclude(id=id).filter(active_ingredient=active_ingredient, category=category)
        if similars.exists():
            serializer = MedicineOutSerializer(similars, many=True)
            formatted_data = {"similars":serializer.data}
            return Response(
                formatted_data
                ,status=status.HTTP_200_OK
            )
        return Response(
         {"similars":"No similar medicines"},
          status=status.HTTP_204_NO_CONTENT
        )


class MedicineBatchesListAPIView(generics.ListCreateAPIView):
    "list all medcine batches"
    permission_classes = [IsPharmacist]
    pagination_class = MedicinePagination
    
    def get_queryset(self):
        id = self.kwargs.get("id",None)
        medicine = get_object_or_404(Medicine, id=id)
        batches = medicine.batches.all()
        return batches

    def get_serializer_class(self) -> MedicineOutSerializer | MedicineInSerializer:
        if self.request.method == "GET":
            return BatchOutSerializer
        else:
            return BatchInSerializer
    
    def perform_create(self, serializer):
        id = self.kwargs.get("id",None)
        medicine = get_object_or_404(Medicine, id=id) 
        serializer.save(medicine = medicine)



class BatchRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsPharmacist]
    
    
    def get_serializer_class(self) -> MedicineOutSerializer | MedicineInSerializer:
        if self.request.method == "GET":
            return BatchOutSerializer
        else:
            return BatchInSerializer
    
    queryset = Batch.objects.all()
    