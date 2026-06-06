# 📘 CLAUDE.md - Universal Project & Learning Guide

## 🎯 Hub Belajar & Profil Projek
- **Misi Pengguna:** Saya menggunakan Claude Pro untuk **belajar** dan memahami konsep koding secara mendalam (bukan sekadar copy-paste kode jadi).
- **Pendekatan:** Bantu saya memahami *best practice*, pola desain (design patterns), dan logika di balik kode yang ditulis.
- **Teknologi:** Multi-stack (bisa bervariasi tergantung folder proyek yang sedang dibuka: Swift/SwiftUI, Python, PHP/Laravel, atau JavaScript/TypeScript).

---

## 🦾 Panduan Perilaku Agen (Learning & Token-Saving Mode)

Setiap kali berinteraksi dengan saya di proyek ini, kamu **WAJIB** mematuhi aturan berikut demi efisiensi kuota token dan efektivitas proses belajar saya:

1. **Gaya Penjelasan Edukatif:** Jangan langsung menuliskan seluruh blok kode baru yang panjang. Berikan penjelasan konsepnya secara ringkas terlebih dahulu, jelaskan *kenapa* pendekatan itu dipilih, lalu berikan potongan kode (*snippet*) yang relevan saja.
2. **Prinsip Modular & Kode Efisien:** Saat menyarankan perubahan, tunjukkan baris atau fungsi yang perlu diubah saja (gunakan komentar seperti `// ... kode yang sudah ada ...` atau `# ... kode lainnya ...`). Jangan menulis ulang seluruh isi file yang besar agar menghemat token output.
3. **Validasi Sebelum Eksekusi:** Selalu berikan rencana perubahan taktis dalam bentuk poin-poin sebelum kamu mengedit file secara mandiri. Tunggu konfirmasi "Eksekusi" dari saya.
4. **Format Respons:** Jangan gunakan garis pemisah horizontal (`---`) dalam setiap respons.

---

## 🛠️ Perintah & Framework (Deteksi Otomatis)
*Sebelum menjalankan perintah, deteksi file manifest di root folder (seperti `Package.swift`, `Package.json`, `composer.json`, atau `requirements.txt`) untuk menentukan perintah yang tepat:*

- **Ekosistem Apple (Swift):** Build menggunakan Xcode/xcodebuild, atau `swift build`.
- **Ekosistem Node.js/Web:** Gunakan `npm run dev` / `npm run build` dan `npm test`.
- **Ekosistem PHP (Laravel):** Gunakan `php artisan serve` dan `php artisan test`.
- **Ekosistem Python:** Gunakan perintah `pytest` untuk testing atau perintah eksekusi sesuai micro-framework yang digunakan.

---

## 🚫 Batasan File (PENTING - Hemat Token)
- **Abaikan Folder Sampah:** Jangan pernah membaca, memindai, atau menganalisis folder `.git`, `node_modules`, `vendor`, `.venv`, file cache build, turunan Xcode (`DerivedData`), atau aset gambar/video berukuran besar.
- Fokus hanya pada file logika bisnis, arsitektur data, dan file kode sumber utama yang sedang kita diskusikan.

---

## 📝 Panduan Penulisan Skripsi BSI 2026 (WAJIB DIPATUHI)

Proyek ini sekaligus merupakan bahan skripsi dengan judul:
**"Pengembangan Sistem Informasi Akuntansi Berbasis Web dengan Immutable Audit Trail Menggunakan Blockchain dan Role-Based Access Control pada CV Borneo Mega Mandiri"**

**Identitas Akademik:**
- Nama Mahasiswa: Andre Wahyu Prasetyo | NIM: 15220517
- Program Studi: S1 Teknik Informatika
- Fakultas: Teknik dan Informatika
- Universitas: Bina Sarana Informatika (UBSI) | Kampus: Pontianak
- Kode Outline: 169 (Implementasi Sistem Informasi) — Program Sarjana, Individu

### ✍️ Aturan Format Penulisan (Pedoman BSI 2026)

| Elemen | Ketentuan |
|--------|-----------|
| Ukuran Kertas | A4 |
| Font | Times New Roman |
| Ukuran Font Isi | 12pt |
| Ukuran Font Judul Bab | 14pt, Huruf Kapital, Tebal, Rata Tengah |
| Spasi Isi | 2 spasi |
| Spasi Abstrak | 1 spasi |
| Spasi Tabel/Gambar | Disesuaikan |
| Margin Atas | 3 cm |
| Margin Kiri | 4 cm |
| Margin Bawah | 2,5 cm |
| Margin Kanan | 2,5 cm |
| Judul Sub Bab | 12pt, Tebal, Huruf Kapital di awal kata |
| Minimal Halaman | 30 halaman (tidak termasuk cover, daftar isi, lampiran) |

### 🖼️ Aturan Penomoran Gambar & Tabel
- **Gambar:** Judul di bawah gambar, rata tengah. Format: `Gambar III.1` (artinya gambar ke-1 di Bab III)
- **Tabel:** Judul di atas tabel, rata tengah. Format: `Tabel II.1` (artinya tabel ke-1 di Bab II)
- Sumber gambar ditulis di bawah judul gambar jika bukan karya sendiri

### 📑 Nomor Halaman
- Bagian awal (cover s.d. daftar isi): angka romawi kecil (i, ii, iii...), posisi tengah bawah
- Bagian isi (Bab I dst.): angka latin, awal bab di tengah bawah, halaman lain di pojok kanan atas
- Bagian akhir (daftar pustaka, lampiran): angka latin lanjutan, tengah bawah

### 🗂️ Struktur Bab Skripsi (Outline 169 — Implementasi Sistem Informasi)

```
BAB I   PENDAHULUAN
  1.1.  Latar Belakang Masalah
  1.2.  Identifikasi Masalah
  1.3.  Perumusan Masalah
  1.4.  Tujuan dan Manfaat Penelitian
  1.5.  Metode Penelitian
  1.6.  Ruang Lingkup

BAB II  LANDASAN TEORI
  2.1.  Tinjauan Pustaka (Kajian Literatur)
  2.2.  Teori Pendukung (konsep-konsep utama yang digunakan)

BAB III ANALISA SISTEM BERJALAN
  3.1.  Tinjauan Institusi/Perusahaan
  3.2.  Proses Bisnis Sistem Berjalan
  3.3.  Spesifikasi Dokumen Sistem Berjalan (opsional)

BAB IV  RANCANGAN SISTEM DAN PROGRAM USULAN
  4.1.  Analisis Kebutuhan
  4.2.  Perancangan Perangkat Lunak
        4.2.1. Rancangan Antar Muka (UI)
        4.2.2. Rancangan Basis Data (ERD, LRS, Spesifikasi File)
        4.2.3. Rancangan Struktur Navigasi
  4.3.  Implementasi dan Pengujian Unit
        4.3.1. Implementasi
        4.3.2. Pengujian Unit (Black Box Testing)

BAB V   PENUTUP
  5.1.  Kesimpulan
  5.2.  Saran

DAFTAR PUSTAKA
DAFTAR RIWAYAT HIDUP
SURAT KETERANGAN PKL/RISET
BUKTI HASIL PENGECEKAN PLAGIARISME (Turnitin ≤ 25%)
LAMPIRAN
```

### 📚 Aturan Sitasi & Referensi
- **Gaya sitasi WAJIB:** APA Style V.7 menggunakan software **Mendeley**
- **Jurnal/paper:** Minimal **10 jurnal OJS** (bereputasi nasional/internasional) untuk Skripsi S1
- **Batasan tahun referensi:** Jurnal/paper maksimal **5 tahun terakhir (2021–2026)**; buku maksimal 10 tahun (2016–2026)
- **Dilarang:** Blogspot, Wordpress, Wikipedia sebagai sumber
- Format sitasi dalam teks: `(Nama Pengarang, Tahun)` — contoh: `(Romney & Steinbart, 2021)`
- Format kutipan < 5 baris: gunakan tanda kutip `"..."` dengan 2 spasi
- Format kutipan ≥ 5 baris: tanpa tanda kutip, 1 spasi, indent dari kiri

### 📌 Panduan Penulisan Skripsi (Mode Interaktif)
Saat membantu menulis konten skripsi, kamu WAJIB:
1. Kerjakan **per sub-bab**, jangan langsung tulis seluruh bab sekaligus
2. Gunakan **bahasa ilmiah akademis** — ubah gaya PKL menjadi teoritis dan analitis
3. Setiap klaim/teori harus diikuti **sitasi APA** yang valid (tahun 2021–2026)
4. Ingatkan jika ada referensi yang melewati batas 5 tahun
5. Teks skripsi menggunakan **bahasa Indonesia baku** sesuai KBBI, istilah asing dicetak miring