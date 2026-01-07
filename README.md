# 📖 README - Cara Menjalankan Projek

Selamat datang di Sistem Dashboard Penjualan & Akuntansi. Panduan ini akan membantu Anda menjalankan aplikasi ini dari awal, bahkan jika komputer Anda belum terinstall Python.

---

## 🛠️ Tahap 1: Instalasi Python (Wajib)

Aplikasi ini dibuat menggunakan bahasa pemrograman **Python**. Anda harus menginstalnya terlebih dahulu agar aplikasi bisa berjalan.

1.  **Download Python**:

    - Kunjungi website resmi: [Download Python untuk Windows](https://www.python.org/downloads/)
    - Klik tombol kuning **"Download Python 3.x.x"**.

2.  **Instalasi Python**:

    - Buka file installer yang baru saja didownload.
    - ⚠️ **PENTING**: Pada tampilan awal instalasi, **WAJIB MENCENTANG** opsi `Add Python to PATH` di bagian bawah.
    - Klik **Install Now**.
    - Tunggu hingga proses selesai.

3.  **Cek Instalasi**:
    - Tekan tombol `Windows + R`, ketik `cmd`, lalu tekan Enter.
    - Ketik perintah berikut lalu Enter:
      ```cmd
      python --version
      ```
    - Jika muncul tulisan seperti `Python 3.12.0` (atau versi lain), berarti Python sudah siap.

---

## 📂 Tahap 2: Menyiapkan Folder Projek

1.  Pastikan Anda sudah memiliki folder projek ini (misalnya hasil ekstrak ZIP).
2.  Buka terminal (Command Prompt) di dalam folder ini. Caranya:
    - Buka folder projek di File Explorer.
    - Klik pada _address bar_ di atas (yang ada tulisan jalur folder), hapus semuanya, ketik `cmd`, lalu Enter.
    - Akan muncul layar hitam (Command Prompt) yang sudah mengarah ke folder ini.

---

## ⚡ Tahap 3: Instalasi Kode & Library

Sebelum aplikasi bisa jalan, kita perlu menginstall "jantung" dan "otak" aplikasi ini (library pendukung).

1.  **Buat Virtual Environment** (Ruang khusus agar sistem komputer Anda tetap bersih):
    Ketik perintah ini di CMD lalu Enter:

    ```cmd
    python -m venv venv
    ```

2.  **Aktifkan Virtual Environment**:
    Ketik perintah ini:

    ```cmd
    venv\Scripts\activate
    ```

    _(Tanda sukses: Akan muncul tulisan `(venv)` di bagian paling kiri baris perintah)._

3.  **Install Library**:
    Ketik perintah ini (pastikan internet lancar):
    ```cmd
    pip install -r requirements.txt
    ```

---

## 🗄️ Tahap 4: Setup Database

Karena database sudah disertakan (file `db_new.sqlite3`), Anda cukup memastikan sinkronisasi. Namun, jika Anda perlu membuat akun admin baru, ikuti langkah ke-2.

1.  **Cek Database**:

    ```cmd
    python manage.py migrate
    ```

2.  **Buat Akun Admin Baru** (Opsional / Jika database kosong):
    ```cmd
    python manage.py createsuperuser
    ```
    _(Ikuti instruksi di layar: Masukkan username `adminbmm` dan password sesuai keinginan)._

---

## 🚀 Tahap 5: Menjalankan Aplikasi

Sekarang semuanya sudah siap. Mari kita nyalakan mesinnya!

1.  Ketik perintah ini:

    ```cmd
    python manage.py runserver
    ```

2.  Akan muncul tulisan banyak, dan di bagian bawah ada tulisan seperti:
    `Starting development server at http://127.0.0.1:8000/`

3.  Buka browser Anda (Chrome, Edge, atau Firefox).
4.  Ketik alamat ini di bar: **`http://127.0.0.1:8000/`**

Selamat! Aplikasi sudah berjalan. 🎉

---

## 🔑 Akun Login Default

Jika menggunakan database yang sudah disediakan, gunakan akun administrator berikut:

- **Username**: `adminbmm`
- **Password**: `testing12345`

_(Password ini bisa diubah nanti di menu Admin)._

---

## ❌ Cara Mematikan Aplikasi

Jika sudah selesai menggunakan:

1.  Kembali ke layar hitam (CMD).
2.  Tekan tombol `Ctrl + C` di keyboard.
3.  Tutup jendela CMD.
