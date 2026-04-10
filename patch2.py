import os

old_forms_path = '/Users/fakhridjmrs/Data_Fakhri/dashboard-accountant/finance/forms.py'
new_forms_path = '/Users/fakhridjmrs/Data_Fakhri/dashboard-accountant/repo-baru/finance/forms.py'

with open(old_forms_path, 'r') as f:
    old_content_forms = f.read()

marker = "# ============================================================\n# FORMS OPERASIONAL\n# ============================================================"
if marker in old_content_forms:
    ops_forms = old_content_forms[old_content_forms.index(marker):]
    ops_forms = ops_forms.replace('from .models import Inbound, Outbound, Manifest', 'from .models import Inbound, Outbound, ManifestPengiriman')
    ops_forms = ops_forms.replace('class ManifestForm', 'class ManifestPengirimanForm')
    ops_forms = ops_forms.replace('model = Manifest', 'model = ManifestPengiriman')

    with open(new_forms_path, 'a') as f:
        f.write('\n' + ops_forms)
    print("forms.py patched!")
