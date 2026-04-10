import os
import glob

# Only update my copied files (the ops templates at root of finance templates)
template_dir = '/Users/fakhridjmrs/Data_Fakhri/dashboard-accountant/repo-baru/finance/templates/finance/'
files = []
for f in ['dashboard_ops.html', 'inbound_list.html', 'inbound_form.html', 'inbound_detail.html', 
          'outbound_list.html', 'outbound_form.html', 'outbound_detail.html', 
          'manifest_list.html', 'manifest_form.html', 'manifest_detail.html']:
    path = os.path.join(template_dir, f)
    if os.path.exists(path):
        files.append(path)

for path in files:
    with open(path, 'r') as f:
        content = f.read()
    
    # URL renaming
    content = content.replace("{% url 'inbound_", "{% url 'ops_inbound_")
    content = content.replace("{% url 'outbound_", "{% url 'ops_outbound_")
    content = content.replace("{% url 'manifest_", "{% url 'ops_manifest_")
    # Base renaming too
    content = content.replace("{% url 'ops_manifest_list_baru", "{% url 'ops_manifest_list")

    with open(path, 'w') as f:
        f.write(content)

print("Templates link patched!")
