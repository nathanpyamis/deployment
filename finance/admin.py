from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('application', 'amount', 'payment_date', 'status')
    list_filter = ('status', 'payment_date')
    search_fields = ('application__applicant__user__username', 'transaction_id')