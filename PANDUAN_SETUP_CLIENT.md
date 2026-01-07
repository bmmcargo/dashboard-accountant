# 🚀 Panduan Instalasi & Penggunaan - Sistem Akuntansi BMM Cargo

Panduan ini ditujukan bagi pengguna baru untuk menjalankan aplikasi website akuntansi di komputer lokal (Windows).

---

## 🛠️ Langkah 1: Instalasi Python

Aplikasi ini membutuhkan **Python** untuk berjalan. Jika Anda belum memilikinya:

1.  **Download Python**: Buka link [python.org](https://www.python.org/downloads/windows/) dan download versi terbaru (misal: Python 3.12).
2.  **Instalasi**: Jalankan file `.exe` yang sudah didownload.
3.  **PENTING**: Saat muncul jendela instalasi, **WAJIB centang kotak "Add Python to PATH"** di bagian bawah sebelum klik "Install Now".
4.  Setelah selesai, buka **Command Prompt (CMD)** dan ketik `python --version` untuk memastikan Python sudah terpasang.

---

## 📂 Langkah 2: Menyiapkan Folder Project

1.  Dapatkan folder project (misal dari USB atau Download ZIP dari GitHub).
2.  Letakkan folder tersebut di lokasi yang mudah ditemukan, contohnya di: `D:\dashboard-accountant` atau di Desktop.
3.  Buka **Command Prompt (CMD)**, lalu masuk ke folder tersebut:
    ```cmd
    cd /d D:\dashboard-accountant
    ```

---

## 🐍 Langkah 3: Mengaktifkan Virtual Environment

Virtual Environment digunakan agar aplikasi berjalan dengan stabil tanpa mengganggu program lain.

1.  **Buat Virtual Env** (Hanya dilakukan satu kali saat pertama setup):
    ```cmd
    python -m venv venv
    ```
2.  **Aktifkan**:
    ```cmd
    venv\Scripts\activate
    ```
    _(Jika berhasil, akan muncul tanda `(venv)` di sebelah kiri baris perintah CMD)._

---

## 📦 Langkah 4: Install Library yang Dibutuhkan

Pastikan koneksi internet aktif, lalu jalankan perintah ini:

```cmd
pip install -r requirements.txt
```

---

## 💾 Langkah 5: Persiapan Database & Data

Jika Anda ingin menggunakan data yang sudah ada (misal dari file Excel yang diberikan klien):

1.  **Jalankan Migration** (Setup tabel database):
    ```cmd
    python manage.py migrate
    ```
2.  **Input Akun Standar BMM**:
    ```cmd
    python manage.py seed_accounts
    ```
3.  **Import Data dari Excel (CSV)**:
    ```cmd
    python manage.py import_excel
    ```

---

## 🚀 Langkah 6: Menjalankan Website

Setiap kali Anda ingin membuka website, jalankan perintah ini di CMD (pastikan di folder project):

```cmd
python manage.py runserver
```

Setelah itu, buka browser Anda (Chrome/Edge) dan ketik alamat berikut:
👉 **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## 🔐 Informasi Login Default

Gunakan akun berikut untuk masuk pertama kali:

- **Username**: `admin`
- **Password**: `admin123`

_(Anda bisa mengganti password ini melalui menu Admin atau panduan manajemen user)._

---

## ❓ Masalah Umum (Troubleshooting)

- **Error: 'python' is not recognized**: Artinya saat instalasi Python, Anda lupa mencentang "Add Python to PATH". Silakan instal ulang Python.
- **Tampilan Berantakan**: Pastikan semua file di folder `static` sudah ada dan pastikan server jalan tanpa error.
- **Data Tidak Muncul**: Pastikan Anda sudah menjalankan langkah nomor 5 (Seed & Import).

---

_© 2026 CV. Borneo Mega Mandiri - Sistem Informasi Akuntansi_
