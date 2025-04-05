from rest_framework import serializers

from sales.models import Invoice, SaleItem

class SaleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleItem
        fields = [
            "medicine",
            "quantity",
        ]

class InvoiceCreationSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True)
    
    class Meta:
        model = Invoice 
        fields = [
            "items",
            "payment_status",
            "discount_percentage",
            "total_after_discount"
        ]
        read_only_field = [
            "total_before_discount",
            "total_after_discount",
        ]
    
    def create(self, validated_data):
        items_data = validated_data.pop("items")
        invoice = Invoice.objects.create(**validated_data)
        for item in items_data:
            SaleItem.objects.create(
                **item,
                invoice=invoice
            )
          
        return invoice


    def update(self, instance, validated_data):
        """ whole update """
        items_data = validated_data.pop("items",None)
        if items_data:
            instance.items.all().delete()
            for item in items_data:
                SaleItem.objects.create(
                    **item,
                    invoice = instance
                )
                
            
            
        return super().update(instance, validated_data)

