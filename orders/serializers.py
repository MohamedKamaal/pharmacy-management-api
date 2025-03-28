from rest_framework import serializers

from orders.models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            "medicine",
            "quantity",
            "discount"
        ]

class OrderCreationSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    
    class Meta:
        model = Order 
        fields = [
            "supplier",
            "items",
            "total_before",
            "total_after"
        ]
        read_only_field = [
            "total_before",
            "total_after",
        ]
    
    def create(self, validated_data):
        items_data = validated_data.pop("items")
        order = Order.objects.create(**validated_data)
        for item in items_data:
            OrderItem.objects.create(
                **item,
                order = order
            )
          
        return order


    def update(self, instance, validated_data):
        """ whole update """
        items_data = validated_data.pop("items",None)
        if items_data:
            instance.items.all().delete()
            for item in items_data:
                OrderItem.objects.create(
                    **item,
                    order = instance
                )
                
            
            
        return super().update(instance, validated_data)

