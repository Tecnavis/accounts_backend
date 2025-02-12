from rest_framework import serializers
from financials.models import Transaction, TransactionPayment


class TransactionPaymentSerializer(serializers.ModelSerializer):
    """Serializer for payments made for a transaction"""
    class Meta:
        model = TransactionPayment
        fields = [
            "payment_id",
            "transaction",
            "amount",
            "payment_date", 
            "payment_mode"
            ]
        read_only_fields = [
            "payment_id", 
            "payment_date"]

    def create(self, validated_data):
        """Creates a new payment and updates transaction status"""
        payment = TransactionPayment.objects.create(**validated_data)
        payment.transaction.update_payment_status()
        return payment
    


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for Transactions with related payments"""
    service_name = serializers.CharField(source="service.name", read_only=True)
    service_price = serializers.CharField(source="service.total_price", read_only=True)
    # service_tax_rate = serializers.CharField(source="service.tax_rate", read_only=True)
    total_paid = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    remaining_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    payments = TransactionPaymentSerializer(many=True, required=False)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "transaction_id",
            "username",
            "billing_address",
            "service",
            "quantity",
            # "total_service_amount",
            "total_paid",
            "remaining_amount",
            "payment_status",
            "transaction_type",
            "sale_date",
            "remarks",
            "payments",
            "service_name",
            "service_price",
            # "service_tax_rate"
            "remaining_amount",

            "vat_amount",
            "vat_rate",
            "vat_type"
        ]
        read_only_fields = ["transaction_id", "total_service_amount", "total_paid", "remaining_amount", "payment_status"]

    def create(self, validated_data):
        """Create a transaction and handle payments"""
        payments_data = validated_data.pop("payments", [])  # Extract payments list
        transaction = Transaction.objects.create(**validated_data)

        # Create payment records if payments exist
        for payment_data in payments_data:
            TransactionPayment.objects.create(transaction=transaction, **payment_data)

        # Update payment status after adding payments
        transaction.update_payment_status()
        return transaction






# class TransactionSerializer(serializers.ModelSerializer):
#     service_name = serializers.CharField(source="service.name", read_only=True)
#     service_price = serializers.CharField(source="service.price", read_only=True)
#     total_service_amount = serializers.SerializerMethodField()
#     remaining_amount = serializers.SerializerMethodField()
#     class Meta:
#         model = Transaction
#         fields = [
#             "username","billing_address", "service", "amount_paid", "payment_status", 
#             "payment_mode", "tax_rate", "sale_date", 
#             "remarks","transaction_type","service_name", "id", "quantity", "service_price","transaction_id" ,"total_service_amount",
#             "remaining_amount",
#         ]
#     def get_total_service_amount(self, obj):
#         return obj.service.price * obj.quantity

#     def get_remaining_amount(self, obj):
#         return (obj.service.price * obj.quantity) - obj.amount_paid