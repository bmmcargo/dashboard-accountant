import os
import re

old_views_path = '/Users/fakhridjmrs/Data_Fakhri/dashboard-accountant/finance/views.py'
new_views_path = '/Users/fakhridjmrs/Data_Fakhri/dashboard-accountant/repo-baru/finance/views.py'

with open(old_views_path, 'r') as f:
    old_content = f.read()

marker = "# ============================================================\n# VIEWS OPERASIONAL (UNTUK ADMIN & OWNER)\n# ============================================================"
if marker in old_content:
    ops_views = old_content[old_content.index(marker):]
    # Rename Manifest to ManifestPengiriman
    ops_views = ops_views.replace('from .models import Akun, Jurnal, Inbound, Outbound, Manifest', "")
    ops_views = ops_views.replace('from .models import Inbound, Outbound, Manifest', 'from .models import Inbound, Outbound, ManifestPengiriman')
    ops_views = ops_views.replace('from .forms import InboundForm, OutboundForm, ManifestForm', 'from .forms import InboundForm, OutboundForm, ManifestPengirimanForm')
    ops_views = ops_views.replace('ManifestForm', 'ManifestPengirimanForm')
    ops_views = ops_views.replace('Manifest.objects', 'ManifestPengiriman.objects')
    ops_views = ops_views.replace('def manifest_list', 'def ops_manifest_list')
    ops_views = ops_views.replace('def manifest_create', 'def ops_manifest_create')
    ops_views = ops_views.replace('def manifest_detail', 'def ops_manifest_detail')
    ops_views = ops_views.replace('def manifest_edit', 'def ops_manifest_edit')
    ops_views = ops_views.replace('def manifest_delete', 'def ops_manifest_delete')
    ops_views = ops_views.replace('def inbound_list', 'def ops_inbound_list')
    ops_views = ops_views.replace('def inbound_create', 'def ops_inbound_create')
    ops_views = ops_views.replace('def inbound_edit', 'def ops_inbound_edit')
    ops_views = ops_views.replace('def inbound_delete', 'def ops_inbound_delete')
    ops_views = ops_views.replace('def outbound_list', 'def ops_outbound_list')
    ops_views = ops_views.replace('def outbound_create', 'def ops_outbound_create')
    ops_views = ops_views.replace('def outbound_edit', 'def ops_outbound_edit')
    ops_views = ops_views.replace('def outbound_delete', 'def ops_outbound_delete')

    with open(new_views_path, 'a') as f:
        f.write('\n\nfrom .decorators import owner_required\n' + ops_views)
    print("views.py apps patched!")
