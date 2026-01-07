# Dashboard Keuangan & Logistik - BMM Cargo

Aplikasi web berbasis Django untuk manajemen keuangan (Akuntansi) dan operasional logistik (Inbound, Outbound, Manifest Hutang) untuk CV Borneo Mega Mandiri.

## 🚀 Fitur Utama

### 1. Keuangan (Accounting)

- **Jurnal Umum**: Pencatatan transaksi debit/kredit harian.
- **Buku Besar**: Rekapitulasi transaksi per akun (CoA).
- **Laporan Keuangan**: Neraca (Balance Sheet) dan Laba Rugi (Income Statement) otomatis.
- **Manajemen Akun (CoA)**: Tambah, edit, hapus Chart of Accounts.

### 2. Logistik (Operasional)

- **Inbound (Barang Masuk)**:
  - Pencatatan resi masuk, vendor, berat (Kg), dan biaya ongkir.
  - Perhitungan otomatis Total Biaya.
  - Pencarian dan Filter data.
- **Outbound (Barang Keluar)**:
  - Manajemen pengiriman ke customer/tujuan.
  - Tracking biaya vendor (Vendor 1 & Vendor 2).
  - Analisis Profit per resi (Pendapatan - Biaya Vendor).
  - Status Pembayaran (COD/Transfer/Cash).
- **Manifest (Hutang Vendor)**:
  - **Import Otomatis**: Fitur import data manifest dari file CSV (format HULU, KETAPANG, dll) dengan penanganan format kolom dinamis.
  - **Monitoring Hutang**: Dashboard khusus untuk memantau tagihan vendor yang belum lunas.
  - **Kategori Rute**: Pengelompokan berdasarkan rute (Hulu, Ketapang, Pantura, dll).
  - **Smart Parsing**: Deteksi otomatis format mata uang (IDR/USD format) dari data mentah Excel/CSV untuk mencegah kesalahan input nominal.

## 🛠️ Instalasi

1. **Clone Repository**

   ```bash
   git clone https://github.com/bmmcargo/dashboard-accountant.git
   cd dashboard-accountant
   ```

2. **Buat Virtual Environment**

   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Migrasi Database**

   ```bash
   python manage.py migrate
   ```

5. **Buat Superuser (Admin)**
   ```bash
   python manage.py createsuperuser
   ```

## 📦 Import Data (Setup Awal)

Jika Anda memulai dengan database kosong atau ingin me-reset data dengan data Excel/CSV terbaru:

1. Pastikan file CSV (`Manifest_Bmm_Agustus_2022.csv`, `Ketapang.csv`, dll) ada di folder utama project.
2. Jalankan perintah custom import:
   ```bash
   python manage.py import_from_excel
   ```
   _Script ini akan otomatis membaca, membersihkan, dan memvalidasi data dari berbagai format CSV report._

## ▶️ Menjalankan Aplikasi

```bash
python manage.py runserver
```

Buka browser di `http://127.0.0.1:8000/`.

## 📂 Struktur Project

- `finance/`: App utama django.
  - `models.py`: Definisi struktur database (Jurnal, Akun, Inbound, Outbound, Manifest).
  - `views.py`: Logika bisnis dan controller tampilan.
  - `forms.py`: Validasi input form.
  - `urls.py`: Routing halaman.
  - `management/commands/`: Custom scripts (Import Data).
- `templates/finance/`: File HTML frontend (Bootstrap 5).

## 📝 Catatan Penting

- **Database**: Menggunakan SQLite (`db_new.sqlite3`).
- **Format Angka**: Menggunakan library `django.contrib.humanize` untuk format Rupiah di tampilan, namun data tersimpan sebagai Integer/Decimal di database.
- **Keamanan**: Seluruh fitur manipulasi data (Create/Edit/Delete) dilindungi login (`@login_required`).

---

**CV Borneo Mega Mandiri** - 2026
