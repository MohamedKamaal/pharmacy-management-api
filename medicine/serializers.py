from rest_framework import serializers 
from medicine.models import Medicine, Batch, Supplier,ActiveIngredient,Category,Manufacturer
from django.utils.timezone import now 



class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ["name","phone_number","address","city"]

class ActiveIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActiveIngredient
        fields = ["name"]

class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = ["name","country","phone_number","address","website"]

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["name","parent"]

class MedicineInSerializer(serializers.ModelSerializer):
    """ for creation and upadte of medicine """
  
    class Meta:
        model = Medicine
        fields = ["name","international_barcode","active_ingredient",
                  "category","units_per_pack","price","manufacturer"]
        




class MedicineOutSerializer(serializers.ModelSerializer):
    """ for creation and upadte of medicine """
    active_ingredient = serializers.StringRelatedField()
    category = serializers.StringRelatedField()
    manufacturer = serializers.StringRelatedField()
    barcodes = serializers.SerializerMethodField()
    def get_barcodes(self, obj):
        barcodes = obj.batches.values_list("barcode", flat=True)
        return list(barcodes)
                
    class Meta:
        model = Medicine
        fields = ["id","name","active_ingredient","manufacturer",
                  "category","units_per_pack","price","stock","barcodes","international_barcode"]
        read_only_fields = ["international_barcode","barcodes"]



class BatchInSerializer(serializers.ModelSerializer):
    """ for manageing batch """
    packs = serializers.IntegerField(required=True, write_only=True)
    units = serializers.IntegerField(required=False, default=0, write_only=True)
    expiry_date = serializers.DateField(format="%Y-%m",input_formats=["%Y-%m"])
    class Meta:
        model = Batch
        fields = [
            "expiry_date",
            "packs",
            "units"
        ]
    def __init__(self, *args, **kwargs):
        # Call the parent init method
        super().__init__(*args, **kwargs)
        
        # If it's an update request, make 'expiry_date' read-only
        if self.instance:
            self.fields['expiry_date'].read_only = True

    def validate_expiry_date(self, value):
        if value < now().date():
            raise serializers.ValidationError(
                "Expiry date cannot be in the past."
            )
        return value.replace(day=1)  
    
  
   
    def create(self, validated_data):
        packs = validated_data.pop("packs")
        units = validated_data.pop("units",0)
        units_per_pack = validated_data["medicine"].units_per_pack
        if units_per_pack== 1 and units > 0:
            raise serializers.ValidationError(
                "You can't set units for medicine which has only one unit per pack"
            ) 
        total = units + (packs * units_per_pack) 
        validated_data["stock_units"] = total
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        packs = validated_data.pop("packs",None)
        units = validated_data.pop("packs",0)
        units_per_pack = validated_data["medicine"].units_per_pack

        if units_per_pack== 1 and units > 0:
            raise serializers.ValidationError(
                "You can't set units for medicine which has only one unit per pack"
            ) 
        if packs is not None:
            
            total = units + (packs*instance.medicine.units_per_pack)
            validated_data["stock_units"] = total  
        return super().update(instance, validated_data)
    

class BatchOutSerializer(serializers.ModelSerializer):
    """ for manageing batch """
    medicine = serializers.StringRelatedField()
    expiry_date = serializers.DateField(
        format="%Y-%m",input_formats=["%Y-%m"]
    )
    class Meta:
        model = Batch
        fields = [
            "expiry_date",
            "medicine",
            "stock_packets",
            "barcode"
        ]
    