import os

file_path = r"d:\discord\web\Dashboard_penjualan\finance\views.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

replacements = {
    "'finance/jurnal.html'": "'finance/akuntansi/jurnal_list.html'",
    "'finance/jurnal_edit.html'": "'finance/akuntansi/jurnal_edit.html'",
    "'finance/buku_besar.html'": "'finance/akuntansi/buku_besar.html'",
    "'finance/laporan.html'": "'finance/laporan/laporan.html'",
    "'finance/akun_list.html'": "'finance/akuntansi/akun_list.html'",
    "'finance/akun_form.html'": "'finance/akuntansi/akun_form.html'",
    "'finance/inbound_list.html'": "'finance/inbound/inbound_list.html'",
    "'finance/outbound_list.html'": "'finance/outbound/outbound_list.html'",
    "'finance/inbound_form.html'": "'finance/inbound/inbound_form.html'",
    "'finance/outbound_form.html'": "'finance/outbound/outbound_form.html'",
    "'finance/manifest_list.html'": "'finance/manifest/manifest_list.html'",
    "'finance/manifest_form.html'": "'finance/manifest/manifest_form.html'",
    "'finance/kas_harian_list.html'": "'finance/kas/kas_harian_list.html'",
    "'finance/kas_harian_form.html'": "'finance/kas/kas_harian_form.html'",
    "'finance/invoice_inbound.html'": "'finance/inbound/invoice_inbound.html'",
    "'finance/buku_pembantu_list.html'": "'finance/akuntansi/buku_pembantu_list.html'",
    "'finance/tagihan_form.html'": "'finance/tagihan/tagihan_form.html'",
    "'finance/invoice_tagihan_print.html'": "'finance/tagihan/invoice_tagihan_print.html'",
    "'finance/invoice_list.html'": "'finance/tagihan/invoice_list.html'",
}

count = 0
for old, new in replacements.items():
    if old in content:
        content = content.replace(old, new)
        print(f"Replaced {old} -> {new}")
        count += 1
    else:
        print(f"Not found: {old}")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Total replacements: {count}")
