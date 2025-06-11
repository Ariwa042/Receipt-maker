from django import forms
from .models import (
    DebitBankReceipt,
    CreditBankReceipt,
    WithdrawalCryptoReceipt,
    DepositCryptoReceipt,
    BankReceiptTemplate,
    ExchangeReceiptTemplate
)

class BaseReceiptForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all form fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
                'placeholder': field.label or field_name.replace('_', ' ').title()
            })
            if isinstance(field.widget, forms.DateTimeInput):
                field.widget.attrs.update({
                    'type': 'datetime-local',
                })
            if field.required:
                field.widget.attrs['required'] = 'required'

class DebitBankReceiptForm(BaseReceiptForm):
    """Form for debit bank receipts"""
    transaction_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        required=False
    )
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'step': '0.01'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['your_bank'].queryset = BankReceiptTemplate.objects.all()

    class Meta:
        model = DebitBankReceipt
        fields = [
            'country',
            'your_name',
            'your_account_number', 
            'your_bank',
            'beneficiary_name',
            'beneficiary_account_number',
            'beneficiary_bank',
            'amount',
            'transaction_date',
            'receipt_status',
            'remarks'
        ]
        widgets = {
            'remarks': forms.Textarea(attrs={'rows': 3}),
        }

class CreditBankReceiptForm(BaseReceiptForm):
    """Form for credit bank receipts"""
    transaction_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        required=False
    )
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'step': '0.01'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['your_bank'].queryset = BankReceiptTemplate.objects.all()

    class Meta:
        model = CreditBankReceipt
        fields = [
            'country',
            'your_name',
            'your_account_number',
            'your_bank',
            'sender_name',
            'sender_account_number',
            'sender_bank',
            'amount',
            'transaction_date',
            'receipt_status',
            'remarks'
        ]
        widgets = {
            'remarks': forms.Textarea(attrs={'rows': 3}),
        }

class WithdrawalCryptoReceiptForm(BaseReceiptForm):
    """Form for crypto withdrawal receipts"""
    transaction_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        required=False
    )
    amount = forms.DecimalField(
        max_digits=20,
        decimal_places=8,
        widget=forms.NumberInput(attrs={'step': '0.00000001'})
    )
    amount_in_usd = forms.DecimalField(
        max_digits=20,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'step': '0.01'})
    )
    network_fee = forms.DecimalField(
        max_digits=20,
        decimal_places=8,
        widget=forms.NumberInput(attrs={'step': '0.00000001'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['exchange'].queryset = ExchangeReceiptTemplate.objects.all()

    class Meta:
        model = WithdrawalCryptoReceipt
        fields = [
            'exchange',
            'amount',
            'amount_in_usd',
            'network',
            'currency',
            'withdrawal_address',
            'network_fee',
            'transaction_date',
            'receipt_status'
        ]

class DepositCryptoReceiptForm(BaseReceiptForm):
    """Form for crypto deposit receipts"""
    transaction_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        required=False
    )
    amount = forms.DecimalField(
        max_digits=20,
        decimal_places=8,
        widget=forms.NumberInput(attrs={'step': '0.00000001'})
    )
    amount_in_usd = forms.DecimalField(
        max_digits=20,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'step': '0.01'})
    )
    network_fee = forms.DecimalField(
        max_digits=20,
        decimal_places=8,
        widget=forms.NumberInput(attrs={'step': '0.00000001'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['exchange'].queryset = ExchangeReceiptTemplate.objects.all()

    class Meta:
        model = DepositCryptoReceipt
        fields = [
            'exchange',
            'amount',
            'amount_in_usd',
            'network',
            'currency',
            'deposit_address',
            'network_fee',
            'transaction_date',
            'receipt_status'
        ]
