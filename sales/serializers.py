from rest_framework import serializers

from sales.models import Invoice, SaleItem
from medicine.models import Batch
from decimal import Decimal


class SaleItemSerializer(serializers.ModelSerializer):
    barcode = serializers.CharField(
        write_only=True
    )
    medicine = serializers.ReadOnlyField(source="batch.medicine.name")
    class Meta:
        model = SaleItem
        fields = [
            "barcode",
            "quantity",
            "batch",
            "medicine"
        ]
        read_only_fields = ["batch","medicine"]
    
    def validate(self, data):
        barcode = data.get("barcode")
        batch = Batch.objects.filter(barcode=barcode).first()
        if not batch:
            raise serializers.ValidationError(
                "This is not a valid batch barcode"
            )
        
        if not batch.has_amount:
            raise serializers.ValidationError(
                "This batch stock is zero"
            )
        if batch.is_expired:
            raise serializers.ValidationError(
                "This batch is expired"
            )
        
        quantity = data.get("quantity")
        if quantity > batch.stock_units:
            raise serializers.ValidationError(
                f"This quanatity you try to sell exceedes amount in or stocks,We only have {batch.stock_units}"
            )
        
        data["batch"] = batch

        return super().validate(data)
    def create(self, validated_data):
        validated_data.pop("barcode")
         
        return super().create(validated_data)

    def update(self, instance, validated_data):
        raise serializers.ValidationError("Updating sale items is not allowed.")




        
        
class InvoiceCreationSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True, allow_empty=False, write_only=True)
    sale_items = SaleItemSerializer(many=True, source="sales_items" ,read_only=True)
    class Meta:
        model = Invoice 
        fields = [
            "items",
            "sale_items",
            "payment_status",
            "discount",
            "total_before_discount",
            "total_after_discount"
        ]
        read_only_fields = [
            "total_before_discount",
            "total_after_discount",
         
        ]
        
       
    
    def create(self, validated_data):
        items_data = validated_data.pop("items")
        discount = validated_data.pop("discount",0)
        payment_status = validated_data.pop("payment_status")
        invoice = Invoice.objects.create(
            discount = discount,
            payment_status = payment_status
        )
        for item in items_data:
            serializer = SaleItemSerializer(
                data=item
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(invoice=invoice)
       
       
        return invoice


    def update(self, instance, validated_data):
        """ whole update """
        discount = validated_data.get("discount",instance.discount)
        validated_data["discount"] = discount
        items_data = validated_data.pop("items",None)
        if items_data:
            instance.sales_items.all().delete()
            for item in items_data:
                serializer = SaleItemSerializer(
                    data=item
                )
                serializer.is_valid(raise_exception=True)
                serializer.save(invoice=instance)
            
            
            
            
        return super().update(instance, validated_data)

        
        
class ReturnInvoiceSerializer(serializers.Serializer):
    invoice = serializers.CharField(
        write_only=True
    )
    
    
    def validate_invoice(self, value):
   
        try:
            invoice = Invoice.objects.get(id=value)
            return invoice
        except Invoice.DoesNotExist:
            raise serializers.ValidationError("This is not a valid invoice ID.")

