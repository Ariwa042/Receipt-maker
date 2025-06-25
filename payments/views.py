from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
import shortuuid
from .models import XPPackage, Payment, Payment_account, Cryptocurrency

@login_required
def package_list(request):
    """Display available XP packages and handle package/payment method selection"""
    packages = XPPackage.objects.all()
    
    if request.method == 'POST':
        package_id = request.POST.get('package_id')
        payment_method = request.POST.get('payment_method')
        
        # Validate selections
        try:
            package = XPPackage.objects.get(id=package_id)
        except XPPackage.DoesNotExist:
            messages.error(request, 'Invalid package selected.')
            return redirect('payments:package_list')
            
        if payment_method not in dict(Payment.PAYMENT_METHOD_CHOICES):
            messages.error(request, 'Invalid payment method selected.')
            return redirect('payments:package_list')
            
        # Create a new pending payment
        payment = Payment.objects.create(
            user=request.user,
            xp_package=package,
            payment_method=payment_method,
            status='pending'
        )
        
        # Store payment info in session
        request.session['payment_info'] = {            'payment_id': payment.payment_id,
            'package_id': package.id,
            'amount': str(package.price_in_naira),  # Use price_in_naira as default
            'payment_method': payment_method,
        }
        
        return redirect('payments:payment_details')
    
    return render(request, 'payments/package_list.html', {
        'packages': packages,
        'payment_methods': Payment.PAYMENT_METHOD_CHOICES,
    })

@login_required
def payment_details(request):
    """Show payment details based on selected method"""
    # Get payment info from session
    payment_info = request.session.get('payment_info')
    if not payment_info:
        messages.error(request, 'Please select a package first.')
        return redirect('payments:package_list')
    
    try:
        package = XPPackage.objects.get(id=payment_info['package_id'])
    except XPPackage.DoesNotExist:
        messages.error(request, 'Selected package is no longer available.')
        return redirect('payments:package_list')
    
    # Get payment details based on method
    if payment_info['payment_method'] == 'bank':
        payment_accounts = Payment_account.objects.all()
        template = 'payments/bank_payment_details.html'
        context = {'payment_accounts': payment_accounts}
    else:  # crypto
        cryptocurrencies = Cryptocurrency.objects.all()
        template = 'payments/crypto_payment_details.html'
        context = {'cryptocurrencies': cryptocurrencies}
    
    # Add common context
    context.update({
        'package': package,
        'payment_info': payment_info,
    })
    
    return render(request, template, context)

@login_required
def confirm_payment(request):
    """Handle payment confirmation"""
    if request.method != 'POST':
        return redirect('payments:package_list')
        
    payment_id = request.POST.get('payment_id')
    if not payment_id:
        messages.error(request, 'Invalid payment confirmation.')
        return redirect('payments:package_list')
        
    try:
        payment = Payment.objects.get(payment_id=payment_id, user=request.user)
    except Payment.DoesNotExist:
        messages.error(request, 'Payment not found.')
        return redirect('payments:package_list')
          # For bank transfers, set to completed (you might want to change this in production)
    if payment.payment_method == 'bank':
        payment.status = 'completed'
        payment.save()
    
    # Send email notification to admins about the new payment
    send_admin_notification(payment)
    
    # Clean up session
    if 'payment_info' in request.session:
        del request.session['payment_info']
    
    return redirect('payments:payment_success', payment_id=payment.payment_id)

@login_required
def payment_success(request, payment_id):
    """Show payment success page"""
    payment = get_object_or_404(Payment, payment_id=payment_id, user=request.user)
    return render(request, 'payments/payment_success.html', {
        'payment': payment
    })

def send_admin_notification(payment):
    """Send email notification to all admin users about a new payment"""
    User = get_user_model()
    admin_emails = User.objects.filter(is_staff=True, is_active=True).values_list('email', flat=True)
    
    # Filter out empty emails
    admin_emails = [email for email in admin_emails if email]
    
    if not admin_emails:
        # No admin emails found, nothing to send
        return False
    
    # Get the payment details
    payment_method = dict(Payment.PAYMENT_METHOD_CHOICES).get(payment.payment_method, payment.payment_method)
    amount = payment.xp_package.price_in_naira if payment.payment_method == 'bank' else payment.xp_package.price_in_usd
    currency = 'NGN' if payment.payment_method == 'bank' else 'USD'
    
    # Create the email subject and message
    subject = f'New {payment_method} Payment Received - Needs Verification'
    message = f"""
Hello Admin,

A new payment has been made and requires your attention:

Payment ID: {payment.payment_id}
User: {payment.user.username} ({payment.user.email})
Package: {payment.xp_package.name}
Amount: {amount} {currency}
Payment Method: {payment_method}
Status: {payment.status}
Date: {payment.created_at}

Please verify this payment as soon as possible.

This is an automated message. Please do not reply.
"""
    
    # Send the email
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@receipts.com',
            recipient_list=admin_emails,
            fail_silently=False,
        )
        return True
    except Exception as e:
        # Log the error but don't crash the view
        print(f"Failed to send admin notification email: {str(e)}")
        return False
