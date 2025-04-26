"""
Serializers for handling invoice and sale item data in API requests.

This module defines serializers for creating, updating, and validating invoices
and their associated sale items, as well as handling invoice returns.
"""

from rest_framework import serializers
from sales.models import Invoice, SaleItem
from medicine.models import Batch
from decimal import Decimal


class SaleItemSerializer(serializers.ModelSerializer):
    """
    Serializer for SaleItem model.

    Handles the serialization and validation of sale items, including barcode-based
    batch lookup and stock/expiry checks.
    """
    barcode = serializers.CharField(
        write_only=True
    )
    medicine = serializers.ReadOnlyField(source="batch.medicine.name")

    class Meta:
        """Metadata for the SaleItemSerializer."""
        model = SaleItem
        fields = [
            "barcode",
            "quantity",
            "batch",
            "medicine"
        ]
        read_only_fields = ["batch", "medicine"]

    def validate(self, data):
        """Validate barcode, batch availability, and quantity."""
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
                f"This quantity you try to sell exceeds amount in our stocks, We only have {batch.stock_units}"
            )
        data["batch"] = batch
        return super().validate(data)

    def create(self, validated_data):
        """Create a new sale item, removing barcode from validated data."""
        validated_data.pop("barcode")
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Prevent updating sale items."""
        raise serializers.ValidationError("Updating sale items is not allowed.")


class InvoiceCreationSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating invoices.

    Handles the creation and updating of invoices, including their associated
    sale items.
    """
    items = SaleItemSerializer(many=True, allow_empty=False, write_only=True)
    sale_items = SaleItemSerializer(many=True, source="sales_items", read_only=True)

    class Meta:
        """Metadata for the InvoiceCreationSerializer."""
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
        """Create a new invoice with associated sale items."""
        items_data = validated_data.pop("items")
        discount = validated_data.pop("discount", 0)
        payment_status = validated_data.pop("payment_status")
        invoice = Invoice.objects.create(
            discount=discount,
            payment_status=payment_status
        )
        for item in items_data:
            serializer = SaleItemSerializer(
                data=item
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(invoice=invoice)
        return invoice

    def update(self, instance, validated_data):
        """Update an existing invoice, optionally replacing sale items."""
        discount = validated_data.get("discount", instance.discount)
        validated_data["discount"] = discount
        items_data = validated_data.pop("items", None)
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
    """
    Serializer for handling invoice returns.

    Validates the invoice ID and marks the invoice as refunded.
    """
    invoice = serializers.CharField(
        write_only=True
    )

    def validate_invoice(self, value):
        """Validate that the provided invoice ID exists."""
        try:
            invoice = Invoice.objects.get(id=value)
            return invoice
        except Invoice.DoesNotExist:
            raise serializers.ValidationError("This is not a valid invoice ID.")