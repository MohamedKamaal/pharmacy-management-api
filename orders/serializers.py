from rest_framework import serializers
from orders.models import Order, OrderItem
from medicine.models import Batch, Medicine

class OrderItemSerializer(serializers.ModelSerializer):
    packs = serializers.IntegerField(write_only=True)
    units = serializers.IntegerField(write_only=True, required=False)
    expiry_date = serializers.DateField(
        format="%Y-%m",
        input_formats=["%Y-%m"],
        write_only=True
    )
    medicine = serializers.SlugRelatedField(
        queryset = Medicine.objects.all(),
        slug_field = "name",
        write_only=True
        
    )
  

    class Meta:
        model = OrderItem
        fields = ["medicine", "packs", "units", "discount","expiry_date"]

    def validate(self, data):
        medicine = data.get('medicine')
        packs = data.get('packs')
        units = data.get('units',0)
        units_per_pack = medicine.units_per_pack
        
        if units_per_pack == 1 and units > 0:
            raise serializers.ValidationError(
                "You can't set units for medicine which has only one unit per pack"
            )
        
        # Calculate and add the quantity to validated data
        data['quantity'] = units + (packs * units_per_pack)
        # Convert discount percentage to integer (e.g., 25.00 -> 2500)
     
        return data

    def create(self, validated_data):
        # check if batch exists or create it 
    
        medicine = validated_data.pop("medicine")
        packs = validated_data.pop("packs")
        units = validated_data.pop("units",None)
        expiry_date = validated_data.pop("expiry_date")
        quantity = validated_data.get("quantity")
        batch , created= Batch.objects.get_or_create(
            medicine=medicine,
            expiry_date = expiry_date,
            defaults={"stock_units":quantity}
        )
        if not created :
            batch.stock_units += quantity
            batch.save()
        validated_data["batch"] = batch
        return super().create(validated_data)

    def update(self, instance, validated_data):
        raise serializers.ValidationError("Updating order items is not allowed.")



class OrderCreationSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, allow_empty=False)

    class Meta:
        model = Order
        fields = ["supplier", "items", "total_before", "total_after"]
        read_only_fields = ["total_before", "total_after"]
    
    

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        order = Order.objects.create(**validated_data)
        
        for item_data in items_data:
        # Let the OrderItemSerializer handle the conversion and creation
            serializer = OrderItemSerializer(data=item_data)
            serializer.is_valid(raise_exception=True)
            serializer.save(order=order)
        order.save()
        return order

    def update(self, instance, validated_data):
        supplier = validated_data.get("supplier", instance.supplier)
        items_data = validated_data.pop("items", None)
        
        
        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                serializer = OrderItemSerializer(data=item_data)
                serializer.is_valid(raise_exception=True)
                serializer.save(order=instance)
        instance.save()
        return super().update(instance, validated_data)
    
class OrderItemReadSerializer(serializers.ModelSerializer):
    medicine_info = serializers.SerializerMethodField()

    batch_expiry = serializers.DateField(source="batch.expiry_date", format="%Y-%m")
    def get_medicine_info(self, obj):
        return obj.batch.medicine.name
    
    class Meta:
        model = OrderItem
        fields = ["medicine_info", "quantity", "discount", "batch_expiry"]

class OrderReadSerializer(serializers.ModelSerializer):
    items = OrderItemReadSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = [
            "id",  # important for retrieve
            "items",
            "total_before",
            "total_after",
        ]
