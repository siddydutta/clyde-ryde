from django.contrib import admin
from customers.models import Wallet, Payment, Report


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



@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = (
        'report_id',
        'status',
        'vehicle_code',
        'location',
        'created_at',
        'updated_at',
        'description',
    )
    readonly_fields = ('report_id',)
