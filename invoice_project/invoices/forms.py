from django import forms
from django.forms import modelformset_factory
from .models import Invoice, InvoiceItem

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['partner_name']

class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['description', 'quantity', 'unit_price']

InvoiceItemFormSet = modelformset_factory(InvoiceItem, form=InvoiceItemForm, extra=1, can_delete=True)
