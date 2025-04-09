from rest_framework import serializers 
from medicine.models import Medicine, Batch
from django.utils.timezone import now 
class MedicineInSerializer(serializers.ModelSerializer):
    """ for creation and upadte of medicine """
    whole_price = serializers.DecimalField(max_digits=8, decimal_places=2, write_only=True)
    class Meta:
        model = Medicine
        fields = ["name","international_barcode","active_ingredient",
                  "category","units_per_pack","whole_price","manufacturer"]
        

    def create(self, validated_data):
        whole_price = validated_data.pop("whole_price")
        validated_data["price_cents"] = int(whole_price *100)
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        whole_price = validated_data.pop("whole_price",None)
        if whole_price:
            validated_data["price_cents"] = int(whole_price*100)
        return super().update(instance, validated_data)


class MedicineOutSerializer(serializers.ModelSerializer):
    """ for creation and upadte of medicine """
    active_ingredient = serializers.StringRelatedField()
    category = serializers.StringRelatedField()
    manufacturer = serializers.StringRelatedField()
    class Meta:
        model = Medicine
        fields = ["id","name","active_ingredient","manufacturer",
                  "category","units_per_pack","price","stock","international_barcode"]
        



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
        ]
    