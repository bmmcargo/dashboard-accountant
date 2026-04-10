import os
import re

views_path = '/Users/fakhridjmrs/Data_Fakhri/dashboard-accountant/repo-baru/finance/views.py'

with open(views_path, 'r') as f:
    content = f.read()

ops_views = ['dashboard_ops', 'ops_manifest_list', 'ops_manifest_create', 'ops_manifest_detail', 
             'ops_manifest_edit', 'ops_manifest_delete', 'ops_inbound_list', 'ops_inbound_create', 
             'ops_inbound_edit', 'ops_inbound_delete', 'ops_outbound_list', 'ops_outbound_create', 
             'ops_outbound_edit', 'ops_outbound_delete']

# Add @owner_required to all functions EXCEPT ops_views
new_lines = []
lines = content.split('\n')

for i, line in enumerate(lines):
    if line.startswith('def '):
        func_name = line.split(' ')[1].split('(')[0]
        if func_name not in ops_views and i > 0 and lines[i-1].strip() == '@login_required':
            # Insert @owner_required before def if the prev line was @login_required
            new_lines.insert(len(new_lines), '@owner_required')
    
    new_lines.append(line)

new_content = '\n'.join(new_lines)

# Ensure owner_required is imported
if 'from .decorators import owner_required' not in new_content:
    new_content = 'from .decorators import owner_required\n' + new_content

with open(views_path, 'w') as f:
    f.write(new_content)

print("Protected all views with owner_required")
