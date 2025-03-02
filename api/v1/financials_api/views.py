from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from financials.models import Transaction,TransactionPayment
from services.models import Service, Category
from .serializers import TransactionSerializer, TransactionPaymentSerializer
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from django.db import transaction
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
import pandas as pd
import datetime
import io
from django.utils.dateparse import parse_date


@api_view(['GET'])
@permission_classes([AllowAny])
def transaction_list(request):
    transactions = Transaction.objects.all()
    serializer = TransactionSerializer(transactions, many=True)
 
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
@permission_classes([IsAuthenticated])
def create_transaction(request):
    print(request.data)
    transaction_type = request.data.get("transaction_type")
    if transaction_type not in ["sale", "purchase"]:
        return Response({"detail": "Invalid transaction type."}, status=status.HTTP_400_BAD_REQUEST)
   
    data = request.data.copy()
    data["created_by"] = request.user.id
    transaction_serializer = TransactionSerializer(data=data)  
   
    if transaction_serializer.is_valid():
        transaction = transaction_serializer.save()
        print(f"Transaction saved with ID: {transaction.id}")
        # Verify it exists in the database
        try:
            db_check = Transaction.objects.get(id=transaction.id)
            print(f"Verified transaction exists in DB: {db_check.id}")
        except Transaction.DoesNotExist:
            print("ERROR: Transaction not found in database after save!")
        return Response(transaction_serializer.data, status=status.HTTP_201_CREATED)
 
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
            
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    except ValidationError as e:
        return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['POST'])
@permission_classes([AllowAny]) 
def create_transaction_payment(request, id):  
    try:
        transaction = Transaction.objects.get(id=id) 
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_excel(request):
    excel_file = request.FILES["excel_file"]

    try:       
        df = pd.read_excel(io.BytesIO(excel_file.read()))               
        column_mapping = {
            
            'Transaction ID': 'transaction_id',
            'Username': 'username',
            'Service': 'service_name',  
            'Service Name': 'service_name',
            'Payment Status': 'payment_status',
            'Purchase Date': 'sale_date',
            'Sale Date': 'sale_date',
            'Service Price': 'price', 
            'Price': 'price',
            'Quantity': 'quantity',
            'Tax Amount': 'vat_amount',
            'VAT Amount': 'vat_amount', 
            'Remaining Amount': 'remaining_amount',    
        }
        
        for excel_col, code_col in column_mapping.items():
            if excel_col in df.columns:
                df.rename(columns={excel_col: code_col}, inplace=True)
                print(f"Renamed column '{excel_col}' to '{code_col}'")
           
        transactions_data = []
        errors = []
        skipped_rows = 0

        for index, row in df.iterrows():
                
            service_name = row.get("service_name")  
            if not service_name:
                errors.append(f"Row {index + 1}: Missing service_name")
                skipped_rows += 1
                continue  
            
            service = Service.objects.filter(name=service_name).first()
            if not service:
                print(f"Row {index + 1}: Service '{service_name}' not found in database")
                errors.append(f"Row {index + 1}: Service '{service_name}' not found")
                skipped_rows += 1
                continue

            sale_date = row.get("sale_date", None)
            if sale_date:
                if isinstance(sale_date, str):
                    try:
                        sale_date = parse_date(sale_date)
                    except Exception as e:
                        print(f"Error parsing sale_date '{sale_date}': {str(e)}")
                        sale_date = datetime.date.today()
                elif not isinstance(sale_date, datetime.date):
                    sale_date = datetime.date.today()
            else:
                sale_date = datetime.date.today()

            transaction_data = {
                "total_service_amount": row.get("price", 0),
                "remaining_amount": row.get("remaining_amount", 0),
                "transaction_id": row.get("transaction_id"),
                "billing_address": row.get("billing_address"),
                "service": service.id,  
                "quantity": row.get("quantity", 1),
                "payment_status": row.get("payment_status", "unpaid"),
                "transaction_type": row.get("transaction_type", "sale"), 
                "sale_date": sale_date,
                "remarks": row.get("remarks"),
                "country": row.get("country", "saudi"),
                "username": row.get("username"),
                "email": row.get("email"),
                "contact_number": row.get("contact_number"),
                "vat_type": row.get("vat_type", "standard"),
                "vat_rate": row.get("vat_rate", 15),
                "vat_amount": row.get("vat_amount", 0),
            }
            
            transactions_data.append(transaction_data)
        
        if not transactions_data:
            return Response({
                "message": "No valid transactions to import", 
                "errors": errors[:10] if errors else None,
                "total_rows": len(df),
                "skipped_rows": skipped_rows
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = TransactionSerializer(data=transactions_data, many=True)
       
        if serializer.is_valid():
            instances = serializer.save()
            return Response({
                "message": "Transactions imported successfully", 
                "count": len(instances),
                "total_rows": len(df),
                "skipped_rows": skipped_rows,
                "errors": errors[:10] if errors else None
            }, status=status.HTTP_201_CREATED)
        else:
        
            return Response({
                "message": "Validation errors occurred",
                "serializer_errors": serializer.errors,
                "preprocessing_errors": errors[:10] if errors else None,
                "total_rows": len(df),
                "valid_rows": len(transactions_data),
                "skipped_rows": skipped_rows
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        import traceback
        print(f"Exception during import: {str(e)}")
        print(traceback.format_exc())
        return Response({
            "error": str(e),
            "type": type(e).__name__
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_excel_purchase(request):
    excel_file = request.FILES["excel_file"]

    try:       
        df = pd.read_excel(io.BytesIO(excel_file.read()))               
        column_mapping = {
            'Transaction ID': 'transaction_id',
            'Username': 'username',
            'Service': 'service_name',  
            'Service Name': 'service_name',
            'Payment Status': 'payment_status',
            'Purchase Date': 'sale_date',
            'Sale Date': 'sale_date',
            'Service Price': 'price', 
            'Price': 'price',
            'Quantity': 'quantity',
            'Tax Amount': 'vat_amount',
            'VAT Amount': 'vat_amount', 
            'Remaining Amount': 'remaining_amount',    
        }
        
        for excel_col, code_col in column_mapping.items():
            if excel_col in df.columns:
                df.rename(columns={excel_col: code_col}, inplace=True)
                print(f"Renamed column '{excel_col}' to '{code_col}'")
           
        transactions_data = []
        errors = []
        skipped_rows = 0

        for index, row in df.iterrows():
            service_name = row.get("service_name")  
            if not service_name:
                errors.append(f"Row {index + 1}: Missing service_name")
                skipped_rows += 1
                continue  
            
            service = Service.objects.filter(name=service_name).first()
            if not service:
                print(f"Row {index + 1}: Service '{service_name}' not found in database")
                errors.append(f"Row {index + 1}: Service '{service_name}' not found")
                skipped_rows += 1
                continue

            sale_date = row.get("sale_date", None)
            if sale_date:
                if isinstance(sale_date, str):
                    try:
                        sale_date = parse_date(sale_date)
                    except Exception as e:
                        print(f"Error parsing sale_date '{sale_date}': {str(e)}")
                        sale_date = datetime.date.today()
                elif not isinstance(sale_date, datetime.date):
                    sale_date = datetime.date.today()
            else:
                sale_date = datetime.date.today()

            transaction_data = {
                "total_service_amount": row.get("price", 0),
                "remaining_amount": row.get("remaining_amount", 0),
                "transaction_id": row.get("transaction_id"),
                "billing_address": row.get("billing_address"),
                "service": service.id,  
                "quantity": row.get("quantity", 1),
                "payment_status": row.get("payment_status", "unpaid"),
                "transaction_type": "purchase",  
                "sale_date": sale_date,
                "remarks": row.get("remarks"),
                "country": row.get("country", "saudi"),
                "username": row.get("username"),
                "email": row.get("email"),
                "contact_number": row.get("contact_number"),
                "vat_type": row.get("vat_type", "standard"),
                "vat_rate": row.get("vat_rate", 15),
                "vat_amount": row.get("vat_amount", 0),
            }
            
            transactions_data.append(transaction_data)
        
        if not transactions_data:
            return Response({
                "message": "No valid transactions to import", 
                "errors": errors[:10] if errors else None,
                "total_rows": len(df),
                "skipped_rows": skipped_rows
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = TransactionSerializer(data=transactions_data, many=True)      
        if serializer.is_valid():
            
            instances = serializer.save()
            return Response({
                "message": "Transactions imported successfully", 
                "count": len(instances),
                "total_rows": len(df),
                "skipped_rows": skipped_rows,
                "errors": errors[:10] if errors else None
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "message": "Validation errors occurred",
                "serializer_errors": serializer.errors,
                "preprocessing_errors": errors[:10] if errors else None,
                "total_rows": len(df),
                "valid_rows": len(transactions_data),
                "skipped_rows": skipped_rows
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        import traceback
        print(f"Exception during import: {str(e)}")
        print(traceback.format_exc())
        return Response({
            "error": str(e),
            "type": type(e).__name__
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




# import io
# import logging
# import pandas as pd
# from django.db.models import Sum, F
# from django.db.models.functions import Coalesce
# from django.shortcuts import get_object_or_404
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from rest_framework import status

# from .models import Transaction, TransactionPayment
# from .serializers import TransactionSerializer, TransactionPaymentSerializer

# logger = logging.getLogger(__name__)

# # Create a new transaction
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def create_transaction(request):
#     serializer = TransactionSerializer(data=request.data)
#     if serializer.is_valid():
#         transaction = serializer.save()
#         logger.info(f"Transaction created: {transaction.id}")
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# # Retrieve all transactions
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def list_transactions(request):
#     transactions = Transaction.objects.all()
#     serializer = TransactionSerializer(transactions, many=True)
#     return Response(serializer.data)

# # Retrieve a specific transaction by ID
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def transaction_detail(request, transaction_id):
#     transaction = get_object_or_404(Transaction, id=transaction_id)
#     serializer = TransactionSerializer(transaction)
#     return Response(serializer.data)

# # Update a transaction
# @api_view(['PUT'])
# @permission_classes([IsAuthenticated])
# def update_transaction(request, transaction_id):
#     transaction = get_object_or_404(Transaction, id=transaction_id)
#     serializer = TransactionSerializer(transaction, data=request.data, partial=True)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# # Delete a transaction
# @api_view(['DELETE'])
# @permission_classes([IsAuthenticated])
# def delete_transaction(request, transaction_id):
#     transaction = get_object_or_404(Transaction, id=transaction_id)
#     transaction.delete()
#     return Response({"message": "Transaction deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

# # Create a payment for a transaction
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def create_payment(request, transaction_id):
#     transaction = get_object_or_404(Transaction, id=transaction_id)
#     serializer = TransactionPaymentSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save(transaction=transaction)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# # Retrieve all payments for a transaction
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_transaction_payments(request, transaction_id):
#     payments = TransactionPayment.objects.filter(transaction__id=transaction_id)
#     serializer = TransactionPaymentSerializer(payments, many=True)
#     return Response(serializer.data)

# # Calculate total and remaining service amount
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def calculate_service_amount(request):
#     transactions = Transaction.objects.annotate(
#         total_service_amount=F('service__price') * F('quantity'),
#         remaining_amount=F('service__price') * F('quantity') - Coalesce(F('amount_paid'), 0)
#     ).values('id', 'total_service_amount', 'remaining_amount')

#     return Response(transactions)

# # Helper function for Excel import
# def process_excel_import(request, transaction_type):
#     try:
#         excel_file = request.FILES["excel_file"]
#         df = pd.read_excel(io.BytesIO(excel_file.read()))

#         for _, row in df.iterrows():
#             transaction_data = {
#                 "customer_name": str(row.get("customer_name", "")).strip(),
#                 "email": str(row.get("email", "")).strip(),
#                 "service": str(row.get("service", "")).strip(),
#                 "quantity": int(row.get("quantity", 1)),
#                 "price": float(row.get("price", 0)),
#                 "transaction_type": transaction_type,
#             }
#             serializer = TransactionSerializer(data=transaction_data)
#             if serializer.is_valid():
#                 serializer.save()
#             else:
#                 logger.warning(f"Invalid row: {serializer.errors}")

#         return Response({"message": "Excel data imported successfully"}, status=status.HTTP_201_CREATED)

#     except Exception as e:
#         logger.error(f"Error processing Excel import: {str(e)}")
#         return Response({"error": "Failed to process the file"}, status=status.HTTP_400_BAD_REQUEST)

# # Import transactions from an Excel file
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def import_excel(request):
#     return process_excel_import(request, "sale")

# # Import purchase transactions from an Excel file
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def import_excel_purchase(request):
#     return process_excel_import(request, "purchase")
