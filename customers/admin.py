from django.contrib import admin
from customers.models import Wallet, Payment


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'balance',
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'trip',
        'amount',
        'status',
    )
