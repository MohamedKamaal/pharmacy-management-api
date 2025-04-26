"""
Serializers:
    - SupplierSerializer: For supplier data
    - ActiveIngredientSerializer: For active ingredient data
    - ManufacturerSerializer: For manufacturer data
    - CategorySerializer: For category hierarchy
    - MedicineInSerializer: For medicine creation/updates (input)
    - MedicineOutSerializer: For medicine retrieval (output)
    - BatchInSerializer: For batch creation/updates (input)
    - BatchOutSerializer: For batch retrieval (output)

"""

from rest_framework import serializers 
from medicine.models import Medicine, Batch, Supplier,ActiveIngredient,Category,Manufacturer
from django.utils.timezone import now 




class SupplierSerializer(serializers.ModelSerializer):
    """Serializer for Supplier model (read/write)."""
    class Meta:
        model = Supplier
        fields = ["name", "phone_number", "address", "city"]


class ActiveIngredientSerializer(serializers.ModelSerializer):
    """Serializer for ActiveIngredient model (read/write)."""
    class Meta:
        model = ActiveIngredient
        fields = ["name"]


class ManufacturerSerializer(serializers.ModelSerializer):
    """Serializer for Manufacturer model (read/write)."""
    class Meta:
        model = Manufacturer
        fields = ["name", "country", "phone_number", "address", "website"]


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model (read/write)."""
    class Meta:
        model = Category
        fields = ["name", "parent"]


class MedicineInSerializer(serializers.ModelSerializer):
    """
    Input serializer for Medicine creation and updates.
    
    Used for POST, PUT, PATCH requests.
    """
    class Meta:
        model = Medicine
        fields = [
            "name",
            "international_barcode",
            "active_ingredient",
            "category",
            "units_per_pack",
            "price",
            "manufacturer"
        ]


class MedicineOutSerializer(serializers.ModelSerializer):
    """
    Output serializer for Medicine retrieval.
    
    Includes additional computed fields and related data representations.
    """
    active_ingredient = serializers.StringRelatedField()
    category = serializers.StringRelatedField()
    manufacturer = serializers.StringRelatedField()
    barcodes = serializers.SerializerMethodField()
    
    def get_barcodes(self, obj):
        """Get all barcodes associated with this medicine's batches."""
        barcodes = obj.batches.values_list("barcode", flat=True)
        return list(barcodes)
                
    class Meta:
        model = Medicine
        fields = [
            "id",
            "name",
            "active_ingredient",
            "manufacturer",
            "category",
            "units_per_pack",
            "price",
            "stock",
            "barcodes",
            "international_barcode"
        ]
        read_only_fields = ["international_barcode", "barcodes"]


class BatchInSerializer(serializers.ModelSerializer):
    """
    Input serializer for Batch creation and updates.
    
    Handles special packing/unit calculations and expiry date validation.
    """
    packs = serializers.IntegerField(required=True, write_only=True)
    units = serializers.IntegerField(required=False, default=0, write_only=True)
    expiry_date = serializers.DateField(format="%Y-%m", input_formats=["%Y-%m"])
    
    class Meta:
        model = Batch
        fields = ["expiry_date", "packs", "units"]
    
    def __init__(self, *args, **kwargs):
        """Make expiry_date read-only for update operations."""
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['expiry_date'].read_only = True

    def validate_expiry_date(self, value):
        """Validate that expiry date is in the future."""
        if value < now().date():
            raise serializers.ValidationError(
                "Expiry date cannot be in the past."
            )
        return value.replace(day=1)  
    
    def create(self, validated_data):
        """Create batch with calculated total units from packs + units."""
        packs = validated_data.pop("packs")
        units = validated_data.pop("units", 0)
        units_per_pack = validated_data["medicine"].units_per_pack
        
        if units_per_pack == 1 and units > 0:
            raise serializers.ValidationError(
                "You can't set units for medicine which has only one unit per pack"
            ) 
        
        total = units + (packs * units_per_pack) 
        validated_data["stock_units"] = total
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update batch with recalculated units if packs are provided."""
        packs = validated_data.pop("packs", None)
        units = validated_data.pop("packs", 0)
        units_per_pack = validated_data["medicine"].units_per_pack

        if units_per_pack == 1 and units > 0:
            raise serializers.ValidationError(
                "You can't set units for medicine which has only one unit per pack"
            ) 
        
        if packs is not None:
            total = units + (packs * instance.medicine.units_per_pack)
            validated_data["stock_units"] = total  
        return super().update(instance, validated_data)


class BatchOutSerializer(serializers.ModelSerializer):
    """
    Output serializer for Batch retrieval.
    
    Provides formatted expiry date and related medicine information.
    """
    medicine = serializers.StringRelatedField()
    expiry_date = serializers.DateField(format="%Y-%m", input_formats=["%Y-%m"])
    
    class Meta:
        model = Batch
        fields = [
            "expiry_date",
            "medicine",
            "stock_packets",
            "barcode"
        ]
