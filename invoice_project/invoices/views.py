from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from .models import Invoice, InvoiceItem
from .forms import InvoiceForm, InvoiceItemFormSet
import io
import os
from decimal import Decimal


def invoice_list(request):
    invoices = Invoice.objects.all().order_by('-date_created')
    return render(request, 'invoices/invoice_list.html', {'invoices': invoices})


def create_invoice(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        formset = InvoiceItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            invoice = form.save()
            items = formset.save(commit=False)
            for item in items:
                item.invoice = invoice
                item.save()
            messages.success(request, f'Invoice #{invoice.invoice_number} created successfully!')
            return redirect('invoice_detail', invoice.invoice_number)
    else:
        form = InvoiceForm()
        formset = InvoiceItemFormSet(queryset=InvoiceItem.objects.none())
    return render(request, 'invoices/create_invoice.html', {'form': form, 'formset': formset})


def invoice_detail(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    vat_rate =Decimal('0.075')
    vat = invoice.total_amount * vat_rate
    grand_total = invoice.total_amount + vat

    context = {
        'invoice': invoice,
        'vat': vat,
        'grand_total' : grand_total
    }
    return render(request, 'invoices/invoice_details.html', context)


def invoice_pdf(request, invoice_id):
    # Fetch the invoice from the database
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    vat = invoice.total_amount * Decimal('0.075')
    grand_total = invoice.total_amount + vat

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    title_style = styles["Heading1"]

    # Create centered styles
    centered_style = styles["Normal"].clone('centered')
    centered_style.alignment = 1  # TA_CENTER
    title_centered = styles["Heading1"].clone('title_centered')
    title_centered.alignment = 1

    # Path to your company logo
    logo_path = os.path.join(os.getcwd(), "invoice_project", "invoices", "static", "luztow logo.jpg")

    # Add company logo (centered)
    if os.path.exists(logo_path):
        logo_table = Table([[Image(logo_path, width=100, height=60)]], colWidths=[doc.width])
        logo_table.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')]))
        elements.append(logo_table)

    # Add company name (Green) and address (Red) centered
    elements.append(Paragraph("<font color='green'><b>Luztow Resources Ltd</b></font>", title_centered))
    elements.append(Paragraph("<font color='red'>22 Bornu Crescent, Apapa, Lagos</font>", centered_style))
    elements.append(Paragraph("support@luztowresources.com | +234 903 292 4589", centered_style))
    elements.append(Spacer(1, 12))

    # Invoice details
    elements.append(Paragraph(f"<b>Invoice No:</b> INV{invoice.invoice_number:03d}", styles["Normal"]))
    elements.append(Paragraph(f"<b>TIN NO: 33563692-0001</b>", styles["Normal"]))
    elements.append(Paragraph(f"<b>VAT NO: SLV: 090028864666</b>", styles["Normal"]))
    elements.append(Paragraph(f"<b>Partner:</b> {invoice.partner_name}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Date:</b> {invoice.date_created.strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Table data
    subtotal = invoice.total_amount
    vat = subtotal * Decimal('0.075')
    grand_total = subtotal + vat

    data = [["S/N", "Description", "Qty", "Unit Price (₦)", "Total (₦)"]]
    for i, item in enumerate(invoice.items.all(), start=1):
        data.append([i, item.description, item.quantity, f"{item.unit_price:,.2f}", f"{item.total_amount:,.2f}"])

    table = Table(data, colWidths=[40, 200, 50, 100, 100])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 12))

    # Totals
    elements.append(Paragraph(f"<b>Subtotal:</b> ₦{subtotal:,.2f}", styles["Normal"]))
    elements.append(Paragraph(f"<b>VAT (7.5%):</b> ₦{vat:,.2f}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Grand Total:</b> ₦{grand_total:,.2f}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Signature section
    elements.append(Paragraph("<b>Authorized Signature</b>", styles["Normal"]))
    elements.append(Paragraph("(For Luztow Resources Ltd.)", styles["Normal"]))
    elements.append(Spacer(1, 24))

    elements.append(Paragraph("<b>Thank you for your business!</b>", styles["Normal"]))

    doc.build(elements)

    buffer.seek(0)
    response = HttpResponse(buffer, content_type="application/pdf")
    response['Content-Disposition'] = f'attachment; filename="INV{invoice.invoice_number:03d}_{invoice.partner_name.replace(" ", "_")}.pdf"'
    return response
