from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, FileResponse, JsonResponse
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from django.views.decorators.http import require_http_methods
import os

from .models import (
    DebitBankReceipt,
    CreditBankReceipt,
    WithdrawalCryptoReceipt,
    DepositCryptoReceipt,
    BankReceiptTemplate,
    ExchangeReceiptTemplate
)
from .forms import (
    DebitBankReceiptForm,
    CreditBankReceiptForm,
    WithdrawalCryptoReceiptForm,
    DepositCryptoReceiptForm
)

from playwright.sync_api import sync_playwright
import tempfile
from datetime import datetime

def generate_receipt_pdf(request, template_name, context):
    """Generate PDF from receipt template using Playwright with mobile viewport."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        # Create page with mobile viewport
        page = browser.new_page(viewport={'width': 390, 'height': 844})  # iPhone 12 Pro dimensions
        
        # Render the template to HTML
        html_content = render(request, template_name, context).content.decode()
        
        # Create temp file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            # Write HTML to temp file
            page.set_content(html_content)
            
            # Wait for any lazy-loaded content and animations
            page.wait_for_timeout(1000)
            
            # Generate PDF with mobile width
            page.pdf(path=tmp.name, width="390px", format='A4')
            tmp_path = tmp.name
        
        browser.close()
        
        return tmp_path

def generate_receipt_image(request, template_name, context):
    """Generate image from receipt template using Playwright with mobile viewport."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        # Create page with mobile viewport
        page = browser.new_page(viewport={'width': 390, 'height': 844})  # iPhone 12 Pro dimensions
        
        # Set mobile user agent
        page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1'
        })
        
        # Render the template to HTML
        html_content = render(request, template_name, context).content.decode()
        page.set_content(html_content)
        
        # Wait for images to load
        page.wait_for_load_state('networkidle')
        page.wait_for_selector('img')
        
        # Wait for any lazy-loaded content and animations
        page.wait_for_timeout(2000)
        
        # Create temp file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            # Generate image with mobile dimensions
            page.screenshot(path=tmp.name, full_page=True)
            tmp_path = tmp.name
        
        browser.close()
        
        return tmp_path

def get_receipt_urls(request, receipt_category, receipt_type, receipt_id):
    """Helper function to generate receipt URLs"""
    preview_url = reverse('receipts:preview_receipt', kwargs={
        'receipt_category': receipt_category,
        'receipt_type': receipt_type,
        'receipt_id': receipt_id
    })
    download_url = preview_url + '?download=true'
    return preview_url, download_url

def is_image_format(format_str):
    """Helper function to determine if the requested format is an image."""
    return format_str.lower() in ['img', 'image', 'png']

@login_required
def create_debit_bank_receipt(request):
    if request.method == 'POST':
        form = DebitBankReceiptForm(request.POST)
        if form.is_valid():
            receipt = form.save(commit=False)
            receipt.user = request.user
            # Check if user has enough XP
            template = receipt.your_bank
            if request.user.userprofile.xp_balance < template.xp_cost:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False, 
                        'error': f'Insufficient XP balance. This receipt costs {template.xp_cost} XP.'
                    })
                messages.error(request, f'Insufficient XP balance. This receipt costs {template.xp_cost} XP.')
                return redirect('receipts:create_debit_bank_receipt')
            receipt.save()
            
            # Deduct XP
            request.user.userprofile.xp_balance -= template.xp_cost
            request.user.userprofile.save()

            # Handle file generation for both AJAX and regular form submissions
            template_name = get_bank_template_path('debit', receipt.your_bank.type)
            context = {'receipt': receipt, 'request': request}
            format = request.POST.get('format', 'pdf').lower()
            
            if not is_image_format(format):
                # Generate PDF
                pdf_path = generate_receipt_pdf(request, template_name, context)
                with open(pdf_path, 'rb') as f:
                    response = HttpResponse(f.read(), content_type='application/pdf')
                    response['Content-Disposition'] = f'attachment; filename="debit_receipt_{receipt.id}.pdf"'
                os.unlink(pdf_path)  # Clean up temp file
                return response
            else:  # image
                # Generate image
                img_path = generate_receipt_image(request, template_name, context)
                with open(img_path, 'rb') as f:
                    response = HttpResponse(f.read(), content_type='image/png')
                    response['Content-Disposition'] = f'attachment; filename="debit_receipt_{receipt.id}.png"'
                os.unlink(img_path)  # Clean up temp file
                return response
    else:
        form = DebitBankReceiptForm()
    
    return render(request, 'receipts/bank_debit_receipt_form.html', {'form': form})

@login_required
def create_credit_bank_receipt(request):
    if request.method == 'POST':
        form = CreditBankReceiptForm(request.POST)
        if form.is_valid():
            receipt = form.save(commit=False)
            receipt.user = request.user
            # Check if user has enough XP
            template = receipt.your_bank
            if request.user.userprofile.xp_balance < template.xp_cost:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False, 
                        'error': f'Insufficient XP balance. This receipt costs {template.xp_cost} XP.'
                    })
                messages.error(request, f'Insufficient XP balance. This receipt costs {template.xp_cost} XP.')
                return redirect('receipts:create_credit_bank_receipt')
            
            receipt.save()
            
            # Deduct XP
            request.user.userprofile.xp_balance -= template.xp_cost
            request.user.userprofile.save()
            
            # Handle file generation for both AJAX and regular form submissions
            template_name = get_bank_template_path('credit', receipt.your_bank.type)
            context = {'receipt': receipt, 'request': request}
            # Get format from POST data
            format = request.POST.get('format', 'pdf').lower()
            print(f"Received format: {format}")  # Debug log
            
            if not is_image_format(format):
                # Generate PDF
                pdf_path = generate_receipt_pdf(request, template_name, context)
                with open(pdf_path, 'rb') as f:
                    response = HttpResponse(f.read(), content_type='application/pdf')
                    response['Content-Disposition'] = f'attachment; filename="credit_receipt_{receipt.id}.pdf"'
                os.unlink(pdf_path)  # Clean up temp file
                return response
            else:
                # Generate image
                img_path = generate_receipt_image(request, template_name, context)
                with open(img_path, 'rb') as f:
                    response = HttpResponse(f.read(), content_type='image/png')
                    response['Content-Disposition'] = f'attachment; filename="credit_receipt_{receipt.id}.png"'
                os.unlink(img_path)  # Clean up temp file
                return response
    else:
        form = CreditBankReceiptForm()
    
    return render(request, 'receipts/bank_credit_receipt_form.html', {'form': form})

@login_required
def create_crypto_withdrawal_receipt(request):
    if request.method == 'POST':
        form = WithdrawalCryptoReceiptForm(request.POST)
        if form.is_valid():
            receipt = form.save(commit=False)
            receipt.user = request.user
            # Check if user has enough XP  
            template = receipt.exchange
            if request.user.userprofile.xp_balance < template.xp_cost:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False, 
                        'error': f'Insufficient XP balance. This receipt costs {template.xp_cost} XP.'
                    })
                messages.error(request, f'Insufficient XP balance. This receipt costs {template.xp_cost} XP.')
                return redirect('receipts:create_crypto_withdrawal_receipt')
            
            receipt.save()
            
            # Deduct XP
            request.user.userprofile.xp_balance -= template.xp_cost
            request.user.userprofile.save()
            
            # Handle file generation for both AJAX and regular form submissions
            template_name = get_exchange_template_path('withdrawal', receipt.exchange.type)
            context = {'receipt': receipt, 'request': request}
            # Get format from POST data
            format = request.POST.get('format', 'pdf').lower()
            print(f"Received format: {format}")  # Debug log
            
            if not is_image_format(format):
                # Generate PDF
                pdf_path = generate_receipt_pdf(request, template_name, context)
                with open(pdf_path, 'rb') as f:
                    response = HttpResponse(f.read(), content_type='application/pdf')
                    response['Content-Disposition'] = f'attachment; filename="withdrawal_receipt_{receipt.id}.pdf"'
                os.unlink(pdf_path)  # Clean up temp file
                return response
            else:
                # Generate image
                img_path = generate_receipt_image(request, template_name, context)
                with open(img_path, 'rb') as f:
                    response = HttpResponse(f.read(), content_type='image/png')
                    response['Content-Disposition'] = f'attachment; filename="withdrawal_receipt_{receipt.id}.png"'
                os.unlink(img_path)  # Clean up temp file
                return response
    else:
        form = WithdrawalCryptoReceiptForm()
    
    return render(request, 'receipts/crypto_withdrawal_receipt_form.html', {'form': form})

@login_required
def create_crypto_deposit_receipt(request):
    if request.method == 'POST':
        form = DepositCryptoReceiptForm(request.POST)
        if form.is_valid():
            receipt = form.save(commit=False)
            receipt.user = request.user
            # Check if user has enough XP
            template = receipt.exchange
            if request.user.userprofile.xp_balance < template.xp_cost:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False, 
                        'error': f'Insufficient XP balance. This receipt costs {template.xp_cost} XP.'
                    })
                messages.error(request, f'Insufficient XP balance. This receipt costs {template.xp_cost} XP.')
                return redirect('receipts:create_crypto_deposit_receipt')
            
            receipt.save()
            
            # Deduct XP
            request.user.userprofile.xp_balance -= template.xp_cost
            request.user.userprofile.save()
            
            # Handle file generation for both AJAX and regular form submissions
            template_name = get_exchange_template_path('deposit', receipt.exchange.type)
            context = {'receipt': receipt, 'request': request}
            # Get format from POST data
            format = request.POST.get('format', 'pdf').lower()
            print(f"Received format: {format}")  # Debug log
            
            if not is_image_format(format):
                # Generate PDF
                pdf_path = generate_receipt_pdf(request, template_name, context)
                with open(pdf_path, 'rb') as f:
                    response = HttpResponse(f.read(), content_type='application/pdf')
                    response['Content-Disposition'] = f'attachment; filename="deposit_receipt_{receipt.id}.pdf"'
                os.unlink(pdf_path)  # Clean up temp file
                return response
            else:
                # Generate image
                img_path = generate_receipt_image(request, template_name, context)
                with open(img_path, 'rb') as f:
                    response = HttpResponse(f.read(), content_type='image/png')
                    response['Content-Disposition'] = f'attachment; filename="deposit_receipt_{receipt.id}.png"'
                os.unlink(img_path)  # Clean up temp file
                return response
    else:
        form = DepositCryptoReceiptForm()
    
    return render(request, 'receipts/crypto_deposit_receipt_form.html', {'form': form})

def get_bank_template_path(receipt_type, bank_type):
    """Get path to bank-specific receipt template."""
    return f'receipts/banks/{bank_type.lower()}/{receipt_type}_receipt.html'

def get_exchange_template_path(receipt_type, exchange_type):
    """Get path to exchange-specific receipt template."""
    return f'receipts/exchanges/{exchange_type.lower()}/{receipt_type}_receipt.html'

@login_required
def preview_receipt(request, receipt_category, receipt_type, receipt_id):
    """Preview and handle download requests for receipts."""
    # Get the appropriate receipt model and template
    if receipt_category == 'bank':
        if receipt_type == 'debit':
            receipt = get_object_or_404(DebitBankReceipt, id=receipt_id, user=request.user)
            template_name = get_bank_template_path(receipt_type, receipt.your_bank.type)
        else:  # credit
            receipt = get_object_or_404(CreditBankReceipt, id=receipt_id, user=request.user)
            template_name = get_bank_template_path(receipt_type, receipt.your_bank.type)
    else:  # crypto
        if receipt_type == 'withdrawal':
            receipt = get_object_or_404(WithdrawalCryptoReceipt, id=receipt_id, user=request.user)
            template_name = get_exchange_template_path('withdrawal', receipt.exchange.type)
        else:  # deposit
            receipt = get_object_or_404(DepositCryptoReceipt, id=receipt_id, user=request.user)
            template_name = 'receipts/crypto_deposit_receipt.html'

    # Handle download request
    if request.GET.get('download'):
        # Get format from query params and handle case-insensitively
        format = request.GET.get('format', 'pdf').lower()
        print(f"Received format: {format}")  # Debug log
        context = {'receipt': receipt, 'request': request}
        
        if not is_image_format(format):
            # Generate PDF
            pdf_path = generate_receipt_pdf(request, template_name, context)
            with open(pdf_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{receipt_type}_receipt_{receipt.id}.pdf"'
            os.unlink(pdf_path)  # Clean up temp file
            return response
        else:
            # Generate image
            img_path = generate_receipt_image(request, template_name, context)
            with open(img_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='image/png')
                response['Content-Disposition'] = f'attachment; filename="{receipt_type}_receipt_{receipt.id}.png"'
            os.unlink(img_path)  # Clean up temp file
            return response

    # Preview the receipt
    context = {'receipt': receipt, 'request': request}
    return render(request, template_name, context)