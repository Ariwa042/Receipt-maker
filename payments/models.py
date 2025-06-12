from django.db import models
from django.conf import settings
from decimal import Decimal
import shortuuid
from shortuuid.django_fields import ShortUUIDField


class Payment_account(models.Model):
    bank_name = models.CharField(max_length=100, null=True, blank=True)
    account_number = models.CharField(max_length=10, null=True, blank=True)
    account_holder_name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f'Payment Account of {self.account_holder_name}'
  
    class Meta:
        verbose_name = 'Payment Account'
        verbose_name_plural = 'Payment Accounts'

class Cryptocurrency(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    wallet_address = models.CharField(max_length=255, null=True, blank=True)
    symbol = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return f'{self.name} ({self.symbol})'
    
    class Meta:
        verbose_name = 'Crypto currency'
        verbose_name_plural = 'Crypto currencies'


class XPPackage(models.Model):
    xp_amount = models.PositiveIntegerField()
    price_in_naira = models.DecimalField(max_digits=10, decimal_places=2)
    price_in_usdt = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f"{self.xp_amount}XP for {self.price_in_naira} Naira or {self.price_in_usdt} USDT"

    class Meta:
        ordering = ['price_in_naira']

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded')
    ]

    PAYMENT_METHOD_CHOICES = [
        ('bank', 'Bank Transfer'),
        ('crypto', 'Cryptocurrency')
    ]

    payment_id = ShortUUIDField(unique=True, max_length=50, length=18, prefix='py', alphabet='abcdefghijklmnopqrstuvwxyz0123456789')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    xp_package = models.ForeignKey(XPPackage, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.xp_package} - {self.status}"

    def save(self, *args, **kwargs):
        # Generate a short UUID if not set
        if not self.payment_id:
            self.payment_id = shortuuid.uuid()
              # Set the amount from the XP package if not already set
        if not self.amount and self.xp_package:
            if self.payment_method == 'crypto' and self.xp_package.price_in_usdt:
                self.amount = self.xp_package.price_in_usdt
            else:
                self.amount = self.xp_package.price_in_naira
        super().save(*args, **kwargs)

        # Credit XP to user's account when payment is completed
        if self.status == 'completed':
            self.user.userprofile.xp_balance += self.xp_package.xp_amount
            self.user.userprofile.save()

    class Meta:
        ordering = ['-created_at']
