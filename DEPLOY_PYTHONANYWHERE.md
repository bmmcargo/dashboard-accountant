# Cara Deploy ke PythonAnywhere via GitHub

Panduan langkah demi langkah untuk menaruh website akuntansi anda online menggunakan PythonAnywhere (Gratis).

## Tahap 1: Upload Kode ke GitHub

1.  Buka **[GitHub.com](https://github.com)** dan buat repository baru (Misal: `dashboard-accountant`).
2.  Jangan centang "Add README", "Add .gitignore", biarkan kosong.
3.  Di terminal project anda (VS Code), jalankan perintah berikut satu per satu:

```bash
# Inisialisasi Git (jika belum)
git init
git add .
git commit -m "Upload pertama aplikasi akuntansi"

# Ganti URL_GITHUB_ANDA dengan link repository yang barusan anda buat
# Contoh: git remote add origin https://github.com/username/dashboard-accountant.git
git remote add origin URL_GITHUB_ANDA

# Upload
git branch -M main
git push -u origin main
```

## Tahap 2: Setup PythonAnywhere

1.  Login ke **[PythonAnywhere.com](https://www.pythonanywhere.com/)**.
2.  Buka menu **"Consoles"** -> Klik **"Bash"**.
3.  Di terminal hitam yang muncul, ketik perintah ini untuk mendownload kode anda:

```bash
# Ganti URL_GITHUB_ANDA dengan link repo anda
# Contoh: git clone https://github.com/username/dashboard-accountant.git
git clone URL_GITHUB_ANDA
```

## Tahap 3: Setup Virtual Environment & Database (Di Console PythonAnywhere)

Masih di terminal "Bash" yang sama, jalankan:

```bash
# Masuk ke folder project (sesuaikan nama folder jika beda)
cd dashboard-accountant

# Buat virtual environment (GUNAKAN python3.10 agar cocok dengan setting Web App)
python3.10 -m venv .venv

# Aktifkan virtual environment
source .venv/bin/activate

# Install library yang dibutuhkan
pip install -r requirements.txt

# Setup Database
python manage.py migrate

# Masukkan Data Akun Awal (PENTING!)
python manage.py loaddata initial_data.json

# Buat Superuser (untuk login admin)
python manage.py createsuperuser
```

(Ingat username & password yang anda buat barusan).

## Tahap 4: Konfigurasi Web App

1.  Klik menu **"Web"** (kanan atas) -> **"Add a new web app"**.
2.  Klik **Next** -> Pilih **Manual Configuration** -> Pilih **Python 3.10** (atau versi terbaru) -> Next.
3.  Scroll ke bawah cari bagian **Virtualenv**:

    - Klik tulisan merah "Enter path to a virtualenv".
    - Ketik: `/home/bmmcargo/dashboard-accountant/.venv`
    - (Ganti `bmmcargo` dengan username PythonAnywhere anda).
    - Klik centang/OK.

4.  Scroll ke bagian **Code**:

    - Di **Source code**, masukkan: `/home/bmmcargo/dashboard-accountant`
    - Klik file **WSGI configuration file** (link biru). Editor akan terbuka.

5.  **Edit File WSGI**:
    - Hapus semua isi file tersebut.
    - Ganti dengan kode di bawah ini:

```python
import os
import sys

# Path ke project folder
path = '/home/bmmcargo/dashboard-accountant'
if path not in sys.path:
    sys.path.append(path)

# Set environment variable settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'akuntansi_app.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

    *   **PENTING**: Ganti `bmmcargo` dengan username asli anda.
    *   Klik **Save** (pojok kanan atas).

## Tahap 5: Static Files (Agar Tampilan Rapi)

1.  Kembali ke menu **"Web"**.
2.  Scroll ke bagian **Static files**:
    - Di kolom **URL**, ketik: `/static/`
    - Di kolom **Directory**, ketik: `/home/bmmcargo/dashboard-accountant/static`
    - (Folder `static` ini belum ada, nanti Django buat otomatis, atau kita arahkan ke folder static admin jika perlu. Untuk awal, ini cukup).

## Tahap Terakhir

1.  Scroll ke paling atas halaman "Web".
2.  Klik tombol hijau **"Reload <username>.pythonanywhere.com"**.
3.  Buka link website anda. Selesai!

---

**Tips:** Jika ada "DisallowedHost" error:

1.  Buka tab "Files".
2.  Edit `dashboard-accountant/akuntansi_app/settings.py`.
3.  Cari `ALLOWED_HOSTS = ['*']`. Pastikan sudah ada tanda bintang `*` atau masukkan nama domain anda `'username.pythonanywhere.com'`.
