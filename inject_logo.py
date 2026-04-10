import os

file_path = '/Users/fakhridjmrs/Data_Fakhri/dashboard-accountant/repo-baru/finance/templates/finance/tagihan/invoice_tagihan_print.html'
base64_path = '/Users/fakhridjmrs/Data_Fakhri/dashboard-accountant/repo-baru/logo_base64.txt'

with open(base64_path, 'r') as b_file:
    b64_data = b_file.read().strip()

with open(file_path, 'r') as h_file:
    content = h_file.read()

# Logic to find where to inject the base64 logo in the cloned container
injection_script = f"""
        // Injeksi logo base64 khusus untuk Excel
        var logoImg = container.querySelector('.logo');
        if (logoImg) {{
            logoImg.src = 'data:image/png;base64,{b64_data}';
            logoImg.style.width = '100px';
        }}
"""

# Place it inside exportToExcel, right after cloning
target_mark = "var container = document.querySelector('.container').cloneNode(true);"
new_content = content.replace(target_mark, target_mark + injection_script)

with open(file_path, 'w') as h_file:
    h_file.write(new_content)

print("Logo base64 successfully injected into the export script!")
