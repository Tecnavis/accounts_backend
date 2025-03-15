from django.urls import path
from . import views

app_name = 'financials_api'


urlpatterns = [
    path("transactions_list/", views.transaction_list, name="transaction_list"),
    path('transactions/<int:id>/', views.transaction_detail, name="transaction_list"),
    path("transactions/", views.create_transaction, name="create_transaction"),
    path("transactions/<int:transaction_id>/", views.update_transaction, name="update_transaction"),
    path("transactions/<int:transaction_id>/delete/", views.delete_transaction, name="delete_transaction"),
   
    path('payments/create/', views.create_payment, name='create-payment'),
    path('payments/<int:id>/', views.create_transaction_payment, name='create_transaction_payment'),
    path('transactions/<int:transaction_id>/payments/', views.get_transaction_payments, name='transaction-payments'),
 
    path("import-excel/", views.import_excel, name="import-excel"),
    path("import_excel_purchase/", views.import_excel_purchase, name="import_excel_purchase"),

    path("expenses/", views.expense_list, name="expense_list"),
    path("expenses/create/", views.create_expense, name="create_expense"),
    path("expenses/<int:id>/update/", views.update_expense, name="update_expense"),
    path("expenses/<int:id>/delete/", views.delete_expense, name="delete_expense"),
     
]