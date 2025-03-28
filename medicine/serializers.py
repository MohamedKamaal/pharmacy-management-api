from rest_framework import serializers 
from medicine.models import Medicine, Batch
class MedicineInSerializer(serializers.ModelSerializer):
    """ for creation and upadte of medicine """
    whole_price = serializers.DecimalField(max_digits=8, decimal_places=2)
    class Meta:
        model = Medicine
        fields = ["international_barcode","active_ingredient",
                  "category","units_per_pack","whole_price"]
        

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
    class Meta:
        model = Medicine
        fields = ["id","active_ingredient",
                  "category","units_per_pack","price","stock"]
        



class BatchInSerializer(serializers.ModelSerializer):
    """ for manageing batch """
    packs = serializers.IntegerField(required=True)
    units = serializers.IntegerField(required=False, default=0)
    class Meta:
        model = Batch
        fields = [
            "expiry_date",
            "packs",
            "units"
        ]
    
    
    def create(self, validated_data):
        packs = validated_data.pop("packs")
        units = validated_data.pop("packs",0)
        units_per_pack = validated_data["medicine"].units_per_pack
        total = units + (packs * units_per_pack) 
        validated_data["stock_units"] = total
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        packs = validated_data.pop("packs",None)
        units = validated_data.pop("packs",0)
        
        if packs is not None:
            
            total = units + (packs*instance.medicine.units_per_pack)
            validated_data["stock_units"] = total  
        return super().update(instance, validated_data)
    

class BatchOutSerializer(serializers.ModelSerializer):
    """ for manageing batch """
    medicine = serializers.StringRelatedField()
    class Meta:
        model = Batch
        fields = [
            "expiry_date",
            "medicine",
            "stock_packets",
        ]
    