"""
Order Serializers

Defines serializers for order-related API endpoints.
"""

from rest_framework import serializers
from orders.models import Order, OrderItem
from medicine.models import Batch, Medicine


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating OrderItems."""
    packs = serializers.IntegerField(write_only=True)
    units = serializers.IntegerField(write_only=True, required=False)
    expiry_date = serializers.DateField(
        format="%Y-%m",
        input_formats=["%Y-%m"],
        write_only=True
    )
    medicine = serializers.SlugRelatedField(
        queryset=Medicine.objects.all(),
        slug_field="name",
        write_only=True
    )

    class Meta:
        model = OrderItem
        fields = ["medicine", "packs", "units", "discount", "expiry_date"]

    def validate(self, data):
        """Validate item data and calculate quantity."""
        medicine = data.get('medicine')
        packs = data.get('packs')
        units = data.get('units', 0)
        units_per_pack = medicine.units_per_pack
        
        if units_per_pack == 1 and units > 0:
            raise serializers.ValidationError(
                "You can't set units for medicine which has only one unit per pack"
            )
        
        data['quantity'] = units + (packs * units_per_pack)
        return data

    def create(self, validated_data):
        """Create or update batch when creating order item."""
        medicine = validated_data.pop("medicine")
        packs = validated_data.pop("packs")
        units = validated_data.pop("units", None)
        expiry_date = validated_data.pop("expiry_date")
        quantity = validated_data.get("quantity")
        
        batch, created = Batch.objects.get_or_create(
            medicine=medicine,
            expiry_date=expiry_date,
            defaults={"stock_units": quantity}
        )
        
        if not created:
            batch.stock_units += quantity
            batch.save()
            
        validated_data["batch"] = batch
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Prevent updates to order items."""
        raise serializers.ValidationError("Updating order items is not allowed.")


class OrderCreationSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating Orders."""
    items = OrderItemSerializer(many=True, allow_empty=False)

    class Meta:
        model = Order
        fields = ["supplier", "items", "total_before", "total_after"]
        read_only_fields = ["total_before", "total_after"]
    
    def create(self, validated_data):
        """Create order with its items."""
        items_data = validated_data.pop("items")
        order = Order.objects.create(**validated_data)
        
        for item_data in items_data:
            serializer = OrderItemSerializer(data=item_data)
            serializer.is_valid(raise_exception=True)
            serializer.save(order=order)
            
        order.save()
        return order

    def update(self, instance, validated_data):
        """Update order by replacing all items."""
        supplier = validated_data.get("supplier", instance.supplier)
        items_data = validated_data.pop("items", None)
        
        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                serializer = OrderItemSerializer(data=item_data)
                serializer.is_valid(raise_exception=True)
                serializer.save(order=instance)
                
        instance.save()
        return instance


class OrderItemReadSerializer(serializers.ModelSerializer):
    """Serializer for reading OrderItems."""
    medicine_info = serializers.SerializerMethodField()
    batch_expiry = serializers.DateField(source="batch.expiry_date", format="%Y-%m")

    def get_medicine_info(self, obj):
        return obj.batch.medicine.name
    
    class Meta:
        model = OrderItem
        fields = ["medicine_info", "quantity", "discount", "batch_expiry"]


class OrderReadSerializer(serializers.ModelSerializer):
    """Serializer for reading Orders."""
    items = OrderItemReadSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ["id", "items", "total_before", "total_after"]