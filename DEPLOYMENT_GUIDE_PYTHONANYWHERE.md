# Panduan Deployment & Manajemen PythonAnywhere

Dokumen ini berisi panduan langkah demi langkah untuk mengelola aplikasi Django "Dashboard Penjualan" di server PythonAnywhere. Panduan ini dibuat khusus untuk mempermudah transisi dari penggunaan offline (XAMPP/Localhost) ke server online (Cloud).

---

## 🔑 Informasi Akses (Credentials)

- **Panel Login**: [https://www.pythonanywhere.com/login/](https://www.pythonanywhere.com/login/)
- **Username**: `bmmcargo`
- **Password**: `akuntansi3421`
- **Domain Publik**: [https://bmmcargo.pythonanywhere.com/](https://bmmcargo.pythonanywhere.com/)

---

## 🛠️ Langkah 1: Login ke Dashboard

1. Buka link login di atas.
2. Masukkan username dan password.
3. Setelah berhasil, Anda akan masuk ke **Dashboard Utama** yang berisi tab menu: `Consoles`, `Files`, `Web`, `Tasks`, `Databases`.

---

## 📂 Langkah 2: Upload Project (File Manager)

Jika di XAMPP Anda biasa copy-paste folder ke `htdocs`, di sini kita menggunakan menu **Files**.

### Opsi A: Upload Manual (Mirip XAMPP)

1. Klik tab **Files** di pojok kanan atas.
2. Anda akan melihat direktori (folder). Root folder Anda biasanya `/home/bmmcargo`.
3. Klik tombol **"Upload a file"** untuk mengupload file individu.
   > **Tips**: PythonAnywhere tidak bisa upload folder sekaligus via browser.
   > **Solusi**:
   >
   > 1. Zip folder project Anda di komputer (`dashboard-accountant-bmmcargo(update).zip`).
   > 2. Upload file `.zip` tersebut ke menu Files.
   > 3. Buka **Bash Console** (lihat Langkah 3), lalu ketik `unzip dashboard-accountant-bmmcargo(update).zip`.

### Opsi B: Menggunakan Git (Disarankan)

Jika codingan ada di GitHub, cukup buka **Bash Console** (Menu Consoles -> Bash) dan ketik:

```bash
git pull origin main
```

Ini akan otomatis mengambil update terbaru tanpa perlu upload manual.

---

## 💻 Langkah 3: Setup Virtual Environment (Console)

Ini adalah "ruang mesin" aplikasi Python agar library tidak bentrok.

1. Ke menu **Consoles** -> Klik **Bash** (di bawah "Start a new console").
2. Layar hitam (terminal) akan muncul.
3. Buat/Aktifkan virtual environment (hanya perlu dilakukan sekali diawal):

   ```bash
   # Masuk ke folder project
   cd dashboard-accountant

   # Buat virtual env (jika belum ada)
   mkvirtualenv --python=/usr/bin/python3 myvenv

   # Install library yang dibutuhkan
   pip install -r requirements.txt
   ```

---

## ⚙️ Langkah 4: Konfigurasi Database & Superuser

Langkah ini untuk me-reset atau update database dan membuat user admin.

### 1. Update Database (Migrate)

Setiap ada perubahan struktur data (tambah tabel/kolom), jalankan ini di **Bash Console**:

```bash
# Pastikan env aktif
workon myvenv

# Masuk folder project
cd dashboard-accountant

# Jalankan migrasi
python manage.py migrate
```

### 2. Membuat Superuser (Admin Login)

Untuk login ke halaman admin, Anda butuh akun superuser.

```bash
python manage.py createsuperuser
```

- Masukkan **Username** (bebas, misal: `admin`).
- Masukkan **Email** (boleh kosong, enter saja).
- Masukkan **Password** (ketik password, **tidak akan muncul hurufnya di layar**, lalu Enter).
- Masukkan Password sekali lagi konfirmasi.

---

## 🌐 Langkah 5: Konfigurasi Web (Web Tab)

Ini adalah langkah terakhir untuk "menghidupkan" website.

1. Klik tab **Web** di menu atas.
2. Scroll ke bawah ke bagian **Virtualenv**:
   - Pastikan path mengarah ke env kita: `/home/bmmcargo/.virtualenvs/myvenv`
3. Bagian **Code**:
   - Source code: `/home/bmmcargo/dashboard-accountant-bmmcargo(update)`
   - WSGI configuration file: Klik file tersebut lalu pastikan settingan project Django sudah benar (biasanya sudah disetup diawal).
4. Bagian **Static files**:
   - URL: `/static/`
   - Directory: `/home/bmmcargo/dashboard-accountant-bmmcargo(update)/finance/static` (sesuaikan path folder static asli).

---

## 🔄 Langkah 6: Reload (Restart Server)

**SANGAT PENTING**: Berbeda dengan XAMPP yang langsung berubah saat file di-save. Di PythonAnywhere, setiap kali Anda:

- Mengedit file coding (Python).
- Mengupload file baru.
- Mengubah setting.

Anda **WAJIB** melakukan Reload:

1. Klik tab **Web**.
2. Klik tombol hijau besar **"Reload bmmcargo.pythonanywhere.com"**.
3. Tunggu loading selesai, lalu cek website Anda.

---

**Catatan Tambahan:**
File `.sqlite3` (Database) ada di folder project. Hati-hati jangan menimpa file ini saat upload ulang project jika tidak ingin data transaksi hilang.
