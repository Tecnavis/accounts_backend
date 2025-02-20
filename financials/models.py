import datetime
from django.db import models
from services.models import Service
from users.models import CustomUser


import logging

logger = logging.getLogger(__name__)

class Transaction(models.Model):

    COUNTRY_CHOICES = (
        ("india", "India"),
        ("saudi", "Saudi Arabia"),
    )

    PAYMENT_STATUS_CHOICES = (
        ("unpaid", "Unpaid"),
        ("partially_paid", "Partially Paid"),
        ("completely_paid", "Completely Paid"),
        ("pending", "Pending"),
    )

    TRANSACTION_TYPE_CHOICES = (
        ("sale", "Sale"),
        ("purchase", "Purchase"),
    )

    VAT_CHOICES = (
        ("standard", "Standard VAT (15%)"),
        ("zero_rated", "Zero-Rated VAT (0%)"),
        ("exempt", "Exempt VAT (No VAT applied)"),
    )
    
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='transactions_created', blank=True, null=True)
    total_service_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)  
    transaction_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    billing_address = models.TextField(blank=True, null=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default="unpaid")
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    sale_date = models.DateField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)
    country = models.CharField(max_length=10, choices=COUNTRY_CHOICES, default="saudi")

    username = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)

    vat_type = models.CharField(max_length=20, choices=VAT_CHOICES)
    vat_rate = models.DecimalField(max_digits=5, decimal_places=2, default=15)  
    vat_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)


    def save(self, *args, **kwargs):

        logger.info(f"Saving Transaction: vat_type={self.vat_type}")
        """Auto-generate transaction ID and calculate VAT based on VAT type."""
        if not self.transaction_id:
            today = datetime.date.today()
            date_string = today.strftime('%Y%m%d')
            last_transaction = Transaction.objects.filter(
                transaction_id__startswith=f'TRN{date_string}'
            ).order_by('transaction_id').last()
            new_sequence = str(int(last_transaction.transaction_id[-4:]) + 1).zfill(4) if last_transaction else '0001'
            self.transaction_id = f'TRN{date_string}{new_sequence}'

        base_amount = self.service.total_price * self.quantity

        if self.vat_type == "standard":
            self.vat_rate = 15 
        elif self.vat_type == "zero_rated":
            self.vat_rate = 0   
        elif self.vat_type == "exempt":
            self.vat_rate = 0 

        if self.vat_type == "exempt":
            self.vat_amount = 0  
        else:
            self.vat_amount = round((self.vat_rate * base_amount) / 100, 2)

        self.total_service_amount = base_amount + self.vat_amount

        if not self.pk:  
            self.remaining_amount = self.total_service_amount

        super().save(*args, **kwargs)

    def update_payment_status(self):
        """Update payment status and remaining amount."""
        self.remaining_amount = self.total_service_amount - self.total_paid  
        if self.total_paid >= self.total_service_amount:
            self.payment_status = "completely_paid"
        elif self.total_paid > 0:
            self.payment_status = "partially_paid"
        else:
            self.payment_status = "unpaid"
        self.save()


    @property
    def total_paid(self):
        """Calculate the total amount paid for this transaction."""
        return sum(payment.amount for payment in self.payments.all())


class TransactionPayment(models.Model):
    """Tracks payments made for a transaction."""
    payment_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    transaction = models.ForeignKey(Transaction, related_name="payments", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)
    payment_mode = models.CharField(max_length=20, choices=[
        ("cash", "Cash"),
        ("upi", "UPI"),
        ("cheque", "Cheque"),
        ("other", "Other"),
    ])

    def save(self, *args, **kwargs):
        """Auto-generate payment ID and update transaction status."""
        if not self.payment_id:
            today = datetime.date.today()
            date_string = today.strftime('%Y%m%d')
            last_payment = TransactionPayment.objects.filter(
                payment_id__startswith=f'PAY{date_string}'
            ).order_by('payment_id').last()
            new_sequence = str(int(last_payment.payment_id[-4:]) + 1).zfill(4) if last_payment else '0001'
            self.payment_id = f'PAY{date_string}{new_sequence}'

        super().save(*args, **kwargs)
        self.transaction.update_payment_status()
