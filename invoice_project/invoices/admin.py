from django.contrib import admin
from .models import Invoice

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'partner_name', 'quantity', 'unit_price', 'total_amount', 'date_created')
