from rest_framework import serializers
from orders.models import Order, OrderItem
from medicine.models import Batch, Medicine

class OrderItemSerializer(serializers.ModelSerializer):
    discount = serializers.DecimalField(max_digits=4, decimal_places=2, write_only=True)
    packs = serializers.IntegerField(write_only=True)
    units = serializers.IntegerField(write_only=True)
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
        units = data.get('units')
        units_per_pack = medicine.units_per_pack
        
        if units_per_pack == 1 and units > 0:
            raise serializers.ValidationError(
                "You can't set units for medicine which has only one unit per pack"
            )
        
        # Calculate and add the quantity to validated data
        data['quantity'] = units + (packs * units_per_pack)
        # Convert discount percentage to integer (e.g., 25.00 -> 2500)
        data['discount_integer'] = int(data['discount'] * 100)
        return data

    def create(self, validated_data):
        # check if batch exists or create it 
        validated_data.pop("discount")
        medicine = validated_data.pop("medicine")
        packs = validated_data.pop("packs")
        units = validated_data.pop("units")
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
    items = OrderItemSerializer(many=True)

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
        items_data = validated_data.pop("items", None)
        
        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                serializer = OrderItemSerializer(data=item_data)
                serializer.is_valid(raise_exception=True)
                serializer.save(order=instance)
        instance.save()
        return super().update(instance, validated_data)