from django.contrib import admin
from .models import Payment_account, Cryptocurrency, XPPackage, Payment

@admin.register(Payment_account)
class PaymentAccountAdmin(admin.ModelAdmin):
    list_display = ('account_holder_name', 'bank_name', 'account_number')
    search_fields = ('account_holder_name', 'bank_name', 'account_number')

@admin.register(Cryptocurrency)
class CryptocurrencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol', 'wallet_address')
    search_fields = ('name', 'symbol')

@admin.register(XPPackage)
class XPPackageAdmin(admin.ModelAdmin):
    list_display = ('xp_amount', 'price')
    search_fields = ('xp_amount',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'user', 'xp_package', 'amount', 'payment_method', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('payment_id', 'user__username', 'user__email')
    readonly_fields = ('payment_id', 'created_at', 'updated_at')
    ordering = ('-created_at',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'xp_package')
