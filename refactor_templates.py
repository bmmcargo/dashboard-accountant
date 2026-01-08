import os
import shutil

base_dir = r"d:\discord\web\Dashboard_penjualan\finance\templates\finance"

moves = {
    "inbound": ["inbound_list.html", "inbound_form.html", "invoice_inbound.html"],
    "outbound": ["outbound_list.html", "outbound_form.html", "invoice_outbound.html"],
    "tagihan": ["invoice_list.html", "tagihan_form.html", "invoice_tagihan_print.html"],
    "manifest": ["manifest_list.html", "manifest_form.html"],
    "akuntansi": ["akun_list.html", "akun_form.html", "jurnal_list.html", "jurnal_form.html", "buku_besar.html", "buku_pembantu_list.html"],
    "kas": ["kas_harian_list.html", "kas_harian_form.html"],
    "laporan": ["laporan.html", "neraca.html", "laba_rugi.html"]
}

for folder, files in moves.items():
    folder_path = os.path.join(base_dir, folder)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Created folder: {folder}")
    
    for file in files:
        src = os.path.join(base_dir, file)
        dst = os.path.join(folder_path, file)
        
        if os.path.exists(src):
            try:
                shutil.move(src, dst)
                print(f"Moved {file} to {folder}/")
            except Exception as e:
                print(f"Error moving {file}: {e}")
        else:
            print(f"Skipped {file} (not found)")
