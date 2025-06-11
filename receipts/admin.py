from django.contrib import admin
from .models import (
    BankReceiptTemplate,
    ExchangeReceiptTemplate,
    Country,
    DebitBankReceipt,
    CreditBankReceipt,
    CryptoCurrency,
    CryptoNetwork,
    WithdrawalCryptoReceipt,
    DepositCryptoReceipt,
)

@admin.register(BankReceiptTemplate)
class BankReceiptTemplateAdmin(admin.ModelAdmin):
    list_display = ('type', 'xp_cost')
    list_editable = ('xp_cost',)
    ordering = ('type',)

@admin.register(ExchangeReceiptTemplate)
class ExchangeReceiptTemplateAdmin(admin.ModelAdmin):
    list_display = ('type', 'xp_cost')
    list_editable = ('xp_cost',)
    ordering = ('type',)

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'currency_name', 'currency_symbol', 'currency_code')
    search_fields = ('name', 'currency_code')
    ordering = ('name',)

class BaseBankReceiptAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'amount', 'formatted_amount', 'receipt_status', 'transaction_date', 'created_at')
    list_filter = ('receipt_status', 'created_at', 'transaction_date', 'country')
    search_fields = ('transaction_id', 'sender_name', 'beneficiary_name', 'remarks')
    readonly_fields = ('transaction_id', 'session_id', 'created_at')
    date_hierarchy = 'transaction_date'
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'country')
        }),
        ('Transaction Details', {
            'fields': ('amount', 'transaction_date', 'receipt_status', 'remarks')
        }),
        ('System Information', {
            'fields': ('transaction_id', 'session_id', 'created_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(DebitBankReceipt)
class DebitBankReceiptAdmin(BaseBankReceiptAdmin):
    fieldsets = BaseBankReceiptAdmin.fieldsets + (
        ('Sender Information', {
            'fields': ('your_name', 'your_bank', 'your_account_number')
        }),
        ('Beneficiary Information', {
            'fields': ('beneficiary_name', 'beneficiary_bank', 'beneficiary_account_number')
        }),
    )
    list_filter = BaseBankReceiptAdmin.list_filter + ('your_bank',)

@admin.register(CreditBankReceipt)
class CreditBankReceiptAdmin(BaseBankReceiptAdmin):
    fieldsets = BaseBankReceiptAdmin.fieldsets + (
        ('Beneficiary Information', {
            'fields': ('your_name', 'your_bank', 'your_account_number')
        }),
        ('Sender Information', {
            'fields': ('sender_name', 'sender_bank', 'sender_account_number')
        }),
    )
    list_filter = BaseBankReceiptAdmin.list_filter + ('your_bank',)

@admin.register(CryptoCurrency)
class CryptoCurrencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol')
    search_fields = ('name', 'symbol')
    ordering = ('name',)

@admin.register(CryptoNetwork)
class CryptoNetworkAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol')
    search_fields = ('name', 'symbol')
    ordering = ('name',)

class BaseCryptoReceiptAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'formatted_crypto_amount', 'formatted_usd_amount', 
                   'currency', 'network', 'receipt_status', 'transaction_date')
    list_filter = ('receipt_status', 'exchange', 'currency', 'network', 'created_at')
    search_fields = ('transaction_id', 'user__email', 'withdrawal_address', 'deposit_address')
    readonly_fields = ('transaction_id', 'created_at', 'updated_at')
    date_hierarchy = 'transaction_date'
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Transaction Details', {
            'fields': ('exchange', 'amount', 'amount_in_usd', 'currency', 'network', 
                      'network_fee', 'transaction_date', 'receipt_status')
        }),
        ('System Information', {
            'fields': ('transaction_id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(WithdrawalCryptoReceipt)
class WithdrawalCryptoReceiptAdmin(BaseCryptoReceiptAdmin):
    fieldsets = BaseCryptoReceiptAdmin.fieldsets[:-1] + (
        ('Withdrawal Information', {
            'fields': ('withdrawal_address',)
        }),
        BaseCryptoReceiptAdmin.fieldsets[-1],
    )

@admin.register(DepositCryptoReceipt)
class DepositCryptoReceiptAdmin(BaseCryptoReceiptAdmin):
    fieldsets = BaseCryptoReceiptAdmin.fieldsets[:-1] + (
        ('Deposit Information', {
            'fields': ('deposit_address',)
        }),
        BaseCryptoReceiptAdmin.fieldsets[-1],
    )
