from django.urls import path
from . import views

app_name = 'receipts'

urlpatterns = [    # Bank receipt URLs
    path('bank/debit/create/', views.create_debit_bank_receipt, name='create_debit_bank_receipt'),
    path('bank/credit/create/', views.create_credit_bank_receipt, name='create_credit_bank_receipt'),
    
    # Crypto receipt URLs
    path('crypto/withdrawal/create/', views.create_crypto_withdrawal_receipt, name='create_crypto_withdrawal_receipt'),
    path('crypto/deposit/create/', views.create_crypto_deposit_receipt, name='create_crypto_deposit_receipt'),
    
    # Receipt preview
    path('preview/<str:receipt_category>/<str:receipt_type>/<int:receipt_id>/',
         views.preview_receipt, name='preview_receipt'),
]
