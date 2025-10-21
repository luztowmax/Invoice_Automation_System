from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from datetime import datetime
import os, json

# -------------------------------------------------------------
# Function to load and update invoice number
# -------------------------------------------------------------
def get_next_invoice_number():
    counter_file = "invoice_counter.json"

    if os.path.exists(counter_file):
        with open(counter_file, "r") as f:
            data = json.load(f)
            invoice_num = data.get("last_invoice", 0) + 1
    else:
        invoice_num = 1

    # Save updated number
    with open(counter_file, "w") as f:
        json.dump({"last_invoice": invoice_num}, f)

    return f"INV{invoice_num:03d}"  # e.g. INV001, INV002


# -------------------------------------------------------------
# Main invoice generator
# -------------------------------------------------------------
def generate_invoice(customer_name, items):
    invoice_number = get_next_invoice_number()
    filename = f"{invoice_number}_{customer_name.replace(' ', '_')}.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # --- COMPANY LOGO ---
    logo_path = "luztow logo.jpg"
    if os.path.exists(logo_path):
        try:
            logo = ImageReader(logo_path)
            c.drawImage(logo, 50, 760, width=80, height=80, mask='auto')
        except Exception as e:
            print(f"⚠️ Could not load logo: {e}")
    else:
        print("⚠️ Logo not found, skipping...")

    # --- COMPANY HEADER ---
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(colors.green)
    c.drawString(200, 820, "Luztow Resources Ltd.")

    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.red)
    c.drawString(200, 805, "22 Bornu Crescent, Apapa, Lagos")
    c.setFont("Helvetica", 12)
    c.drawString(200, 790, "support@luztowresources.com | +234 903 292 4589")

    c.setFillColor(colors.black)
    c.drawString(50, 750, f"Invoice No: {invoice_number}")
    c.drawString(50, 735, f"Customer: {customer_name}")
    c.drawString(50, 720, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # --- TABLE HEADER ---
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 700, "S/N")
    c.drawString(90, 700, "Description")
    c.drawString(300, 700, "Qty")
    c.drawString(370, 700, "Amount (₦)")
    c.drawString(480, 700, "Total (₦)")
    c.line(50, 695, 550, 695)

    # --- TABLE CONTENT ---
    c.setFont("Helvetica", 12)
    y = 680
    total_amount = 0
    sn = 1

    for desc, qty, price in items:
        total = qty * price
        total_amount += total
        c.drawString(50, y, str(sn))
        c.drawString(90, y, desc)
        c.drawString(310, y, str(qty))
        c.drawString(380, y, f"{price:,.2f}")
        c.drawString(490, y, f"{total:,.2f}")
        y -= 20
        sn += 1

    # --- VAT (7.5%) ---
    vat = total_amount * 0.075
    grand_total = total_amount + vat

    c.setStrokeColor(colors.grey)
    c.line(50, y + 10, 550, y + 10)

    # --- TOTALS ---
    c.setFont("Helvetica-Bold", 12)
    c.drawString(400, y - 20, f"Subtotal: ₦{total_amount:,.2f}")
    c.drawString(400, y - 40, f"VAT (7.5%): ₦{vat:,.2f}")
    c.drawString(400, y - 60, f"Total: ₦{grand_total:,.2f}")

    # --- SIGNATURE / STAMP SECTION ---
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.black)
    c.drawString(60, 120, "_____________________________")
    c.drawString(60, 105, "Authorized Signature")
    c.drawString(60, 90, "(For Luztow Resources Ltd.)")

    # Optional: Add company stamp image if available
    stamp_path = "company_stamp.jpg"  # Add your stamp image here
    if os.path.exists(stamp_path):
        try:
            stamp = ImageReader(stamp_path)
            c.drawImage(stamp, 400, 80, width=100, height=100, mask='auto')
        except Exception as e:
            print(f"⚠️ Could not load stamp: {e}")
    else:
        print("ℹ️ No company stamp image found (optional)")

    # --- FOOTER ---
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(colors.green)
    c.drawString(200, 50, "Thank you for your business!")

    c.save()
    print(f"✅ Invoice {invoice_number} generated successfully: {filename}")


# -------------------------------------------------------------
# User input section
# -------------------------------------------------------------
if __name__ == "__main__":
    customer = input("Enter customer name: ")
    items = []

    while True:
        desc = input("Item description (or 'done' to finish): ")
        if desc.lower() == "done":
            break
        qty = int(input("Quantity: "))
        price = float(input("Price per unit: "))
        items.append((desc, qty, price))

    generate_invoice(customer, items)
