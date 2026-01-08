import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "akuntansi_app.settings")
django.setup()

from finance.models import InvoiceTagihan, InboundTransaction
from django.db.models import Sum

print("Checking Invoices...")
invoices = InvoiceTagihan.objects.all()
print(f"Total Invoices found: {invoices.count()}")

for inv in invoices:
    real_total = inv.inbound_items.aggregate(Sum('total_biaya'))['total_biaya__sum'] or 0
    print(f"Inv: {inv.no_invoice}, Stored Total: {inv.total}, Calculated Total: {real_total}")
    
    if inv.total != real_total:
        print(f"  -> Fixing total for {inv.no_invoice}...")
        inv.total = real_total
        inv.save()

# Check Aggregate
total_all = InvoiceTagihan.objects.aggregate(Sum('total'))['total__sum']
print(f"Aggregate All Total: {total_all}")
