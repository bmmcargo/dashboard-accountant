import os
import re

old_views_path = '/Users/fakhridjmrs/Data_Fakhri/dashboard-accountant/finance/views.py'
new_views_path = '/Users/fakhridjmrs/Data_Fakhri/dashboard-accountant/repo-baru/finance/views.py'

with open(old_views_path, 'r') as f:
    old_content = f.read()

with open(new_views_path, 'r') as f:
    new_content = f.read()

# Extract old laporan_keuangan
match_old = re.search(r'def laporan_keuangan\(request\):.*?(?=\n@|\ndef |\Z)', old_content, re.DOTALL)
if match_old:
    old_laporan = match_old.group(0)

# Replace new laporan_keuangan
match_new = re.search(r'def laporan_keuangan\(request\):.*?(?=\n@|\ndef |\Z)', new_content, re.DOTALL)
if match_new:
    new_content = new_content.replace(match_new.group(0), old_laporan)
    
    with open(new_views_path, 'w') as f:
        f.write(new_content)
    print("laporan_keuangan patched!")
else:
    print("Could not find new laporan_keuangan")
