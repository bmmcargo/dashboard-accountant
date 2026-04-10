import os

def fix_block(filepath, marker, is_views=False, is_forms=False):
    with open(filepath, 'r') as f:
        content = f.read()
    
    if marker not in content:
        print(f"Marker not found in {filepath}")
        return

    idx = content.index(marker)
    top_part = content[:idx]
    ops_part = content[idx:]
    
    # Missing imports fix in forms.py
    if is_forms and 'from .models import OpsInbound, OpsOutbound, OpsManifest' not in ops_part:
        ops_part = ops_part.replace(marker, marker + '\nfrom .models import OpsInbound, OpsOutbound, OpsManifest\n')
    
    # Missing imports fix in views.py
    if is_views and 'from .models import OpsInbound, OpsOutbound, OpsManifest' not in ops_part:
        ops_part = ops_part.replace('from .models import Inbound, Outbound, ManifestPengirman', '')
        ops_part = ops_part.replace('from .models import Inbound, Outbound, ManifestPengiriman', '')
        ops_part = ops_part.replace(marker, marker + '\nfrom .models import OpsInbound, OpsOutbound, OpsManifest\nfrom .forms import OpsInboundForm, OpsOutboundForm, OpsManifestForm\n')

    # Rename models to Ops* to prevent ANY conflicts with their InboundTransaction etc.
    ops_part = ops_part.replace('class Inbound(', 'class OpsInbound(')
    ops_part = ops_part.replace('class Outbound(', 'class OpsOutbound(')
    ops_part = ops_part.replace('class ManifestPengiriman(', 'class OpsManifest(')
    # Reference changes within models / forms / views
    ops_part = ops_part.replace('Inbound.objects', 'OpsInbound.objects')
    ops_part = ops_part.replace('Outbound.objects', 'OpsOutbound.objects')
    ops_part = ops_part.replace('ManifestPengiriman.objects', 'OpsManifest.objects')
    
    ops_part = ops_part.replace('= Inbound', '= OpsInbound')
    ops_part = ops_part.replace('= Outbound', '= OpsOutbound')
    ops_part = ops_part.replace('= ManifestPengiriman', '= OpsManifest')
    
    ops_part = ops_part.replace('OpsInbound, on_delete', 'OpsInbound, on_delete') # Ensure safety
    ops_part = ops_part.replace('Inbound, on_delete', 'OpsInbound, on_delete')
    ops_part = ops_part.replace('ManifestPengiriman, on_delete', 'OpsManifest, on_delete')

    # Rename forms
    ops_part = ops_part.replace('class InboundForm', 'class OpsInboundForm')
    ops_part = ops_part.replace('class OutboundForm', 'class OpsOutboundForm')
    ops_part = ops_part.replace('class ManifestPengirimanForm', 'class OpsManifestForm')
    
    ops_part = ops_part.replace('InboundForm(', 'OpsInboundForm(')
    ops_part = ops_part.replace('OutboundForm(', 'OpsOutboundForm(')
    ops_part = ops_part.replace('ManifestPengirimanForm(', 'OpsManifestForm(')
    
    ops_part = ops_part.replace('from .forms import InboundForm, OutboundForm, ManifestPengirimanForm', '')
    
    with open(filepath, 'w') as f:
        f.write(top_part + ops_part)
    print(f"Fixed {filepath}")


fix_block('/Users/fakhridjmrs/Data_Fakhri/dashboard-accountant/repo-baru/finance/models.py', 
          '# MODEL OPERASIONAL (Inbound, Outbound, Manifest)')

fix_block('/Users/fakhridjmrs/Data_Fakhri/dashboard-accountant/repo-baru/finance/forms.py', 
          '# FORMS OPERASIONAL', is_forms=True)

fix_block('/Users/fakhridjmrs/Data_Fakhri/dashboard-accountant/repo-baru/finance/views.py', 
          '# VIEWS OPERASIONAL (UNTUK ADMIN & OWNER)', is_views=True)
