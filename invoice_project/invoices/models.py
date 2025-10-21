from django.db import models
from django.utils import timezone


class Invoice(models.Model):
    invoice_number = models.AutoField(primary_key=True)  # Auto-increment number
    partner_name = models.CharField(max_length=200)
    date_created = models.DateTimeField(default=timezone.now)

    @property
    def total_amount(self):
        return sum(item.total_amount for item in self.items.all())

    def __str__(self):
        return f"Invoice #{self.invoice_number} - {self.partner_name}"


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='items', on_delete=models.CASCADE)
    description = models.TextField()
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        # Automatically calculate total before saving
        self.total_amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.description} - {self.quantity} x {self.unit_price}"
