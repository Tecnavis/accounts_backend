from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from financials.models import Transaction,TransactionPayment
from .serializers import TransactionSerializer, TransactionPaymentSerializer
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from django.db import transaction
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404


@api_view(['GET'])
@permission_classes([AllowAny])
def transaction_list(request):
    transactions = Transaction.objects.all()
    serializer = TransactionSerializer(transactions, many=True)
    print(serializer.data,".......") 
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def transaction_detail(request, id):
    try:
        transaction = Transaction.objects.get(id=id)
    except Transaction.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    serializer = TransactionSerializer(transaction)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny]) 
def create_transaction(request):
    print(request.data)
    transaction_type = request.data.get("transaction_type")

    if transaction_type not in ["sale", "purchase"]:
        return Response({"detail": "Invalid transaction type."}, status=status.HTTP_400_BAD_REQUEST)

    transaction_serializer = TransactionSerializer(data=request.data)
   

    if transaction_serializer.is_valid():
        transaction_serializer.save()
        return Response(transaction_serializer.data, status=status.HTTP_201_CREATED)
    print(transaction_serializer.errors) 
    return Response(transaction_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([AllowAny]) 
def update_transaction(request, transaction_id):
    try:
        transaction = Transaction.objects.get(id=transaction_id)
    except Transaction.DoesNotExist:    
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    transaction_serializer = TransactionSerializer(transaction, data=request.data)
    if transaction_serializer.is_valid():
        transaction_serializer.save()
        return Response(transaction_serializer.data, status=status.HTTP_200_OK)
    return Response(transaction_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([AllowAny]) 
def delete_transaction(request, transaction_id):
    try:    
        transaction = Transaction.objects.get(id=transaction_id)
    except Transaction.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    transaction.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([AllowAny]) 
def create_payment(request):
    """
    Create a new payment for a transaction.
    """
    try:
        with transaction.atomic():
            transaction_id = request.data.get('transaction')
            if not transaction_id:
                raise ValidationError({'transaction': 'Transaction ID is required'})

            transaction_instance = get_object_or_404(Transaction, transaction_id=transaction_id)
            
            payment_amount = request.data.get('amount')
            if not payment_amount:
                raise ValidationError({'amount': 'Payment amount is required'})
            
            try:
                payment_amount = float(payment_amount)
            except ValueError:
                raise ValidationError({'amount': 'Invalid payment amount'})
            
            if payment_amount > transaction_instance.remaining_amount:
                raise ValidationError({'amount': f'Payment exceeds remaining balance (${transaction_instance.remaining_amount})'})
            
            serializer = TransactionPaymentSerializer(data={**request.data, 'transaction': transaction_instance.id})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            print(serializer.data,".hi payment")
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    except ValidationError as e:
        return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['POST'])
@permission_classes([AllowAny]) 
def create_transaction_payment(request, id):  # Accepts ID directly
    try:
        transaction = Transaction.objects.get(id=id)  # Lookup by `id` instead of `transaction_id`
    except Transaction.DoesNotExist:
        return Response({"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND)

    data = request.data
    data['transaction'] = transaction.id  

    serializer = TransactionPaymentSerializer(data=data)
    if serializer.is_valid():
        payment_amount = serializer.validated_data['amount']

        if payment_amount > transaction.remaining_amount:
            return Response({"error": "Payment exceeds the remaining balance"}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        transaction.update_payment_status()
        print(serializer.data),"hi payment"

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_transaction_payments(request, transaction_id):
    """Fetch all payments for a given transaction."""
    try:
        payments = TransactionPayment.objects.filter(transaction__id=transaction_id)
        serializer = TransactionPaymentSerializer(payments, many=True)
        return Response(serializer.data)
    except TransactionPayment.DoesNotExist:
        return Response({"error": "Transaction not found"}, status=404)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from django.db.models import F
@api_view(['GET'])
@permission_classes([AllowAny])
def calculate_service_amount(request):
    transactions = Transaction.objects.annotate(
        total_service_amount=F('service__price') * F('quantity'),
        remaining_amount=F('service__price') * F('quantity') - F('amount_paid')
    ).values(
        'id', 'username', 'service__name', 'service__price', 'quantity', 
        'total_service_amount', 'amount_paid', 'remaining_amount'
    )

    return Response(transactions, status=status.HTTP_200_OK)





