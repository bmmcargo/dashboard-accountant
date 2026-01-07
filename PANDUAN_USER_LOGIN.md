# 🔐 Panduan Manajemen User Login

## Menghapus User Admin dan Membuat User Baru

Dokumentasi ini menjelaskan cara menghapus user admin yang sudah ada dan membuat user baru di Sistem Akuntansi BMM Cargo.

---

## 📋 Prasyarat

- Python virtual environment sudah aktif
- Berada di folder project `Dashboard_penjualan`

### Aktifkan Virtual Environment (Windows)

```bash
.venv\Scripts\activate
```

### Aktifkan Virtual Environment (Linux/Mac)

```bash
source venv/bin/activate
```

---

## 🗑️ 1. Menghapus User yang Sudah Ada

### Opsi A: Hapus user tertentu (misal: admin)

```bash
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username='admin').delete(); print('User admin dihapus!')"
```

### Opsi B: Hapus SEMUA user (hati-hati!)

```bash
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.all().delete(); print('Semua user dihapus!')"
```

### Opsi C: Hapus via Django Shell (interaktif)

```bash
python manage.py shell
```

Kemudian ketik:

```python
from django.contrib.auth.models import User

# Lihat semua user
User.objects.all()

# Hapus user tertentu
User.objects.get(username='admin').delete()

# Keluar dari shell
exit()
```

---

## ➕ 2. Membuat User Baru

### Opsi A: Buat Superuser (Admin) via Command

```bash
python manage.py createsuperuser
```

Kemudian ikuti prompt:

- Username: `(masukkan username baru)`
- Email: `(masukkan email)`
- Password: `(masukkan password, minimal 8 karakter)`

### Opsi B: Buat User dengan Username & Password Langsung

```bash
python manage.py shell -c "
from django.contrib.auth.models import User
user = User.objects.create_superuser(
    username='admin_baru',
    email='admin@bmm.com',
    password='password123'
)
print(f'User {user.username} berhasil dibuat!')
"
```

### Opsi C: Buat User Biasa (Non-Admin)

```bash
python manage.py shell -c "
from django.contrib.auth.models import User
user = User.objects.create_user(
    username='staff',
    email='staff@bmm.com',
    password='password123'
)
print(f'User {user.username} berhasil dibuat!')
"
```

---

## 🔄 3. Mengubah Password User yang Sudah Ada

### Via Command Line

```bash
python manage.py changepassword admin
```

Kemudian masukkan password baru.

### Via Shell

```bash
python manage.py shell -c "
from django.contrib.auth.models import User
user = User.objects.get(username='admin')
user.set_password('password_baru_123')
user.save()
print('Password berhasil diubah!')
"
```

---

## 📝 4. Melihat Daftar User

```bash
python manage.py shell -c "
from django.contrib.auth.models import User
for u in User.objects.all():
    print(f'- {u.username} ({u.email}) - Superuser: {u.is_superuser}')
"
```

---

## 🌐 5. Untuk PythonAnywhere

Jika Anda menggunakan PythonAnywhere, jalankan command yang sama di **Bash Console**:

1. Buka PythonAnywhere → **Consoles** → **Bash**
2. Masuk ke folder project:
   ```bash
   cd ~/Dashboard_penjualan
   source venv/bin/activate
   ```
3. Jalankan command di atas

---

## ⚠️ Catatan Penting

| ⚠️ Peringatan                                               |
| ----------------------------------------------------------- |
| Jangan lupa password yang Anda buat!                        |
| Gunakan password yang kuat (kombinasi huruf, angka, simbol) |
| Setelah membuat user baru, coba login di `/login/`          |

---

## 🔑 Kredensial Default

Jika Anda baru setup, kredensial default adalah:

| Field    | Value      |
| -------- | ---------- |
| Username | `admin`    |
| Password | `admin123` |

**Segera ganti password default setelah login pertama!**

---

_Dokumentasi ini dibuat untuk Sistem Informasi Akuntansi BMM Cargo_
