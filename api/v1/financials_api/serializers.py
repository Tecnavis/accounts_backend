from rest_framework import serializers
from financials.models import Transaction, TransactionPayment,Expense
from users.models import CustomUser
from partner.models import PartnerProfile
from api.v1.partner_api.serializers import PartnerProfileSerializer

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
    total_paid = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    remaining_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    payments = TransactionPaymentSerializer(many=True, required=False)
    created_by = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), required=False)
    partner = PartnerProfileSerializer(read_only=True)
    partner_id = serializers.PrimaryKeyRelatedField(
        queryset=PartnerProfile.objects.all(),
        source='partner',
        write_only=True,
        required=False
    )

   
    class Meta:
        model = Transaction
        fields = [
            "id",
            "transaction_id",
            "service",
            "quantity",
            "total_service_amount",
            "total_paid",
            "remaining_amount",
            "payment_status",
            "transaction_type",
            "sale_date",
            "remarks",
            "payments",
            "service_name",
            "service_price",
            "remaining_amount",
            "vat_amount",
            "vat_rate",
            "vat_type",
            "created_by",
            "discount_amount",
            "billing_address",
            "partner",
            "partner_id",
            
        ]
        read_only_fields = ["transaction_id", "total_service_amount", "total_paid", "remaining_amount", "payment_status",]

    def create(self, validated_data):
        """Create a transaction and handle payments"""
        payments_data = validated_data.pop("payments", [])
        partner_id = validated_data.get("partner")  # Get the partner ID but don't pop it
        transaction = Transaction.objects.create(**validated_data)
        
        for payment_data in payments_data:
            TransactionPayment.objects.create(transaction=transaction, **payment_data)
        transaction.update_payment_status()
        return transaction
    
    
class ExpenseSerializer(serializers.ModelSerializer):
    date = serializers.DateField(format="%d/%m/%Y", input_formats=["%d/%m/%Y", "%Y-%m-%d"])
    class Meta:
        model = Expense
        fields = "__all__"
        read_only_fields = ["user", "created_at"]

