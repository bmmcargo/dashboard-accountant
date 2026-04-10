import os
import sys
import re

old_models_path = '/Users/fakhridjmrs/Data_Fakhri/dashboard-accountant/finance/models.py'
new_models_path = '/Users/fakhridjmrs/Data_Fakhri/dashboard-accountant/repo-baru/finance/models.py'

with open(old_models_path, 'r') as f:
    old_content = f.read()

# Extract the block starting from # ============================================================
# to the end
marker = "# ============================================================\n# MODEL OPERASIONAL (Inbound, Outbound, Manifest)\n# ============================================================"
if marker in old_content:
    ops_models = old_content[old_content.index(marker):]
    # Rename Manifest to ManifestPengiriman
    ops_models = ops_models.replace('class Manifest(models.Model):', 'class ManifestPengiriman(models.Model):')
    ops_models = ops_models.replace('Manifest, on_delete', 'ManifestPengiriman, on_delete')
    ops_models = ops_models.replace('Manifest Pengiriman —', 'Manifest Pengiriman (Baru) —')

    with open(new_models_path, 'a') as f:
        f.write('\n' + ops_models)
    print("models.py patched!")

# Update forms.py
old_forms_path = '/Users/fakhridjmrs/Data_Fakhri/dashboard-accountant/finance/forms.py'
new_forms_path = '/Users/fakhridjmrs/Data_Fakhri/dashboard-accountant/repo-baru/finance/forms.py'

with open(old_forms_path, 'r') as f:
    old_content_forms = f.read()

marker = "# ==========================================\n# FORMS OPERASIONAL (Inbound, Outbound, Manifest)\n# =========================================="
if marker in old_content_forms:
    ops_forms = old_content_forms[old_content_forms.index(marker):]
    ops_forms = ops_forms.replace('from .models import Inbound, Outbound, Manifest', 'from .models import Inbound, Outbound, ManifestPengiriman')
    ops_forms = ops_forms.replace('class ManifestForm', 'class ManifestPengirimanForm')
    ops_forms = ops_forms.replace('model = Manifest', 'model = ManifestPengiriman')

    with open(new_forms_path, 'a') as f:
        f.write('\n' + ops_forms)
    print("forms.py patched!")
