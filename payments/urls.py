from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('packages/', views.package_list, name='package_list'),
    path('details/', views.payment_details, name='payment_details'),
    path('confirm/', views.confirm_payment, name='confirm_payment'),
    path('success/<str:payment_id>/', views.payment_success, name='payment_success'),
]
