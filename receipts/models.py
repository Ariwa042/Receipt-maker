from django.db import models
import uuid
from django.utils import timezone
from decimal import Decimal
from django.core.exceptions import ValidationError

# Create your models here.
BANK_TEMPLATES= [
    ('first_bank', 'First Bank of Nigeria'),
    ('chase_bank', 'Chase Bank'),
    ('paypal', 'PayPal'),
    ('transfer_wise', 'Transfer Wise'),
    ('access_bank', 'Access Bank'),
    ('google_pay', 'Google Pay'),
    ('banco_popular', 'Banco Popular'),
    ('iptu', 'IPTU'),
    ('bank_of_america', 'Bank of America'),


]

CRYPTO_EXCHANGES = [
    ('binance', 'Binance'),
    ('coinbase', 'Coinbase'),
]

RECEIPT_TYPE_CHOICES = [
    ('debit', 'Debit'),
    ('credit', 'Credit'),
]


RECEIPT_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('completed', 'Completed'),
    ('failed', 'Failed'),
    ('reversed', 'Reversed'),
]


class BankReceiptTemplate(models.Model):
    type = models.CharField(max_length=20, choices=BANK_TEMPLATES)
    xp_cost = models.IntegerField(default=0)

    def __str__(self):
        return dict(BANK_TEMPLATES).get(self.type, self.type)

    class Meta:
        verbose_name = 'Bank Template'
        verbose_name_plural = 'Bank Templates'

class ExchangeReceiptTemplate(models.Model):
    type = models.CharField(max_length=20, choices=CRYPTO_EXCHANGES)
    xp_cost = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Exchange Template'
        verbose_name_plural = 'Exchange Templates'
    def __str__(self):
        return dict(CRYPTO_EXCHANGES).get(self.type, self.type)

class Country(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="Name of the country (e.g., Nigeria, United States)")
    currency_name = models.CharField(max_length=50, help_text="Name of the currency used in the country (e.g., Naira, Dollar)")
    currency_symbol = models.CharField(max_length=10, help_text="Symbol of the currency (e.g., ₦, $)")
    currency_code = models.CharField(max_length=10, unique=True, help_text="ISO code of the currency (e.g., NGN for Naira, USD for Dollar)")

    class Meta:
        verbose_name = 'Country and Currency'
        verbose_name_plural = 'Countries and Currencies'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.currency_code}) - {self.currency_name})"


class DebitBankReceipt(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='bank_receipts')
    country = models.ForeignKey(Country, on_delete=models.CASCADE, help_text="Country where the transaction is taking place")
    
    your_bank = models.ForeignKey(BankReceiptTemplate, on_delete=models.CASCADE)
    your_name = models.CharField(max_length=255, null=True, blank=True, help_text="Please type in the correct name in full")
    your_account_number = models.CharField(max_length=20, null=True, blank=True, help_text="Please type in the correct account number in full")
    beneficiary_name = models.CharField(max_length=255, null=True, blank=True, help_text="Please type in the correct name in full")
    beneficiary_account_number = models.CharField(max_length=20, null=True, blank=True, help_text="Please type in the correct account number in full")
    beneficiary_bank = models.CharField(max_length=50, null=True, blank=True, help_text="Please type in the correct bank name in full")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    receipt_status = models.CharField(max_length=20, choices=RECEIPT_STATUS_CHOICES, default='pending')
    transaction_date = models.DateTimeField()
    transaction_id = models.CharField(max_length=100, unique=True)
    session_id = models.CharField(max_length=100, unique=True)
    remarks = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    
    class Meta:
        verbose_name = ' Deposit Bank Receipt'
        verbose_name_plural = 'Deposit Bank Receipts'
        ordering = ['-created_at']
    def __str__(self):
        return f"{self.your_name} - {self.amount} - {self.transaction_id}"
    
    def generate_transaction_id(self):
        """Generate a unique transaction ID."""
        prefix = "DB"  # DB for Debit Bank
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        return f"{prefix}{timestamp}{unique_id}"

    def generate_session_id(self):
        """Generate a unique session ID."""
        return str(uuid.uuid4())

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()
        if not self.session_id:
            self.session_id = self.generate_session_id()
        super().save(*args, **kwargs)    
    @property
    def formatted_amount(self):
        """Return formatted amount with currency symbol."""
        return f"{self.country.currency_symbol}{self.amount:,.2f}"

class CreditBankReceipt(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='credit_bank_receipts')
    country = models.ForeignKey(Country, on_delete=models.CASCADE, help_text="Country where the transaction is taking place")
    
    your_name = models.CharField(max_length=255, null=True, blank=True, help_text="Please type in your name in full")
    your_account_number = models.CharField(max_length=20, null=True, blank=True, help_text="Please type in your account number in full")
    your_bank = models.ForeignKey(BankReceiptTemplate, on_delete=models.CASCADE, help_text='this will be the bank template that will be used')

    sender_bank = models.CharField(max_length=50, null=True, blank=True, help_text='Ensure the bank name is written correctly')

    sender_name = models.CharField(max_length=255, null=True, blank=True, help_text="Please type in the correct name in full")
    sender_account_number = models.CharField(max_length=20, null=True, blank=True, help_text="Please type in the correct account number in full")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    receipt_status = models.CharField(max_length=20, choices=RECEIPT_STATUS_CHOICES, default='pending')
    transaction_date = models.DateTimeField()
    transaction_id = models.CharField(max_length=100, unique=True)
    session_id = models.CharField(max_length=100, unique=True)
    remarks = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = ' Credit Bank Receipt'
        verbose_name_plural = 'Credit Bank Receipts'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.sender_name} - {self.amount} - {self.transaction_id}"
    
    def generate_transaction_id(self):
        """Generate a unique transaction ID."""
        prefix = "CB"  # CB for Credit Bank
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        return f"{prefix}{timestamp}{unique_id}"

    def generate_session_id(self):
        """Generate a unique session ID."""
        return str(uuid.uuid4())

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()
        if not self.session_id:
            self.session_id = self.generate_session_id()
        super().save(*args, **kwargs)

    @property
    def formatted_amount(self):
        """Return formatted amount with currency symbol."""
        return f"{self.country.currency_symbol}{self.amount:,.2f}"
######################## Crypto Receipt Model #########################

class CryptoCurrency(models.Model):
    name = models.CharField(max_length=100, unique=True)
    symbol = models.CharField(max_length=10, unique=True)

    class Meta:
        verbose_name = 'Cryptocurrency'
        verbose_name_plural = 'Cryptocurrencies'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.symbol})"
    

class CryptoNetwork(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="Name of the crypto network (e.g., Ethereum, Binance Smart Chain, Solana)")
    symbol = models.CharField(max_length=10, unique=True, help_text="Symbol of the crypto network (e.g., ETH(ERC20), BSC(BEP20), SOL, XRP)")

    class Meta:
        verbose_name = 'Crypto Network'
        verbose_name_plural = 'Crypto Networks'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.symbol})"
    
class WithdrawalCryptoReceipt(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='crypto_receipts')
    exchange = models.ForeignKey(ExchangeReceiptTemplate, on_delete=models.CASCADE, help_text='The exchange platform used for the transaction')
    amount = models.DecimalField(max_digits=20, decimal_places=8, help_text="Amount of cryptocurrency involved in the transaction")
    amount_in_usd = models.DecimalField(max_digits=20, decimal_places=2, help_text="Equivalent amount in USD at the time of the transaction")
    network = models.ForeignKey(CryptoNetwork, on_delete=models.CASCADE, help_text="The network on which the transaction occurred")
    currency = models.ForeignKey(CryptoCurrency, on_delete=models.CASCADE, help_text="The cryptocurrency involved in the transaction")
    withdrawal_address = models.CharField(max_length=255, help_text="The recipient's wallet address")
    network_fee = models.DecimalField(max_digits=20, decimal_places=8)
    transaction_id = models.CharField(max_length=100, unique=True, help_text="Unique identifier for the transaction")
    transaction_date = models.DateTimeField(help_text="Date and time when the transaction occurred")
    receipt_status = models.CharField(max_length=20, choices=RECEIPT_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Crypto Receipt'
        verbose_name_plural = 'Crypto Receipts'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.receipt_type} - {self.amount} {self.currency.symbol} - {self.transaction_id}"


    def generate_transaction_id(self):
        """Generate a unique transaction ID."""
        prefix = "WC"  # WC for Withdrawal Crypto
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        return f"{prefix}{timestamp}{unique_id}"



    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()
        super().save(*args, **kwargs)

    @property
    def formatted_crypto_amount(self):
        """Return formatted cryptocurrency amount with symbol."""
        return f"{self.amount:.8f} {self.currency.symbol}"

    @property
    def formatted_usd_amount(self):
        """Return formatted USD amount."""
        return f"${self.amount_in_usd:,.2f}"

    def clean(self):
        """Validate the model fields."""
        if not self.withdrawal_address:
            raise ValidationError({'withdrawal_address': 'Withdrawal address is required'})
        if self.amount <= 0:
            raise ValidationError({'amount': 'Amount must be greater than zero'})
        if self.amount_in_usd <= 0:
            raise ValidationError({'amount_in_usd': 'USD amount must be greater than zero'})

    def validate_unique(self, *args, **kwargs):
        """Ensure transaction_id and session_id are unique."""
        super().validate_unique(*args, **kwargs)
        if self.transaction_id:
            if WithdrawalCryptoReceipt.objects.filter(transaction_id=self.transaction_id).exclude(id=self.id).exists():
                raise ValidationError({'transaction_id': 'This transaction ID already exists'})
        if self.session_id:
            if WithdrawalCryptoReceipt.objects.filter(session_id=self.session_id).exclude(id=self.id).exists():
                raise ValidationError({'session_id': 'This session ID already exists'})


class DepositCryptoReceipt(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='deposit_crypto_receipts')
    exchange = models.ForeignKey(ExchangeReceiptTemplate, on_delete=models.CASCADE, help_text='The exchange platform used for the transaction')
    amount = models.DecimalField(max_digits=20, decimal_places=8, help_text="Amount of cryptocurrency involved in the transaction")
    amount_in_usd = models.DecimalField(max_digits=20, decimal_places=2, help_text="Equivalent amount in USD at the time of the transaction")
    network = models.ForeignKey(CryptoNetwork, on_delete=models.CASCADE, help_text="The network on which the transaction occurred")
    currency = models.ForeignKey(CryptoCurrency, on_delete=models.CASCADE, help_text="The cryptocurrency involved in the transaction")
    deposit_address = models.CharField(max_length=255, help_text="The recipient's wallet address")
    network_fee = models.DecimalField(max_digits=20, decimal_places=8)
    transaction_id = models.CharField(max_length=100, unique=True, help_text="Unique identifier for the transaction")
    transaction_date = models.DateTimeField(help_text="Date and time when the transaction occurred")
    receipt_status = models.CharField(max_length=20, choices=RECEIPT_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Crypto Deposit Receipt'
        verbose_name_plural = 'Crypto Deposit Receipts'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.receipt_type} - {self.amount} {self.currency.symbol} - {self.transaction_id}"
    
    def generate_transaction_id(self):
        """Generate a unique transaction ID."""
        prefix = "DC"  # DC for Deposit Crypto
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        return f"{prefix}{timestamp}{unique_id}"
    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()
        super().save(*args, **kwargs)
    @property
    def formatted_crypto_amount(self):
        """Return formatted cryptocurrency amount with symbol."""
        return f"{self.amount:.8f} {self.currency.symbol}"
    @property
    def formatted_usd_amount(self):
        """Return formatted USD amount."""
        return f"${self.amount_in_usd:,.2f}"
    def clean(self):
        """Validate the model fields."""
        if not self.deposit_address:
            raise ValidationError({'deposit_address': 'Deposit address is required'})
        if self.amount <= 0:
            raise ValidationError({'amount': 'Amount must be greater than zero'})
        if self.amount_in_usd <= 0:
            raise ValidationError({'amount_in_usd': 'USD amount must be greater than zero'})