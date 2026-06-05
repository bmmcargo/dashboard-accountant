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