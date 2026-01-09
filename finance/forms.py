from django import forms
from .models import Jurnal, Akun, InboundTransaction, OutboundTransaction, Penerimaan, Manifest, KasHarian, InvoiceTagihan

class JurnalForm(forms.ModelForm):
    class Meta:
        model = Jurnal
        fields = ['tanggal', 'uraian', 'akun_debit', 'akun_kredit', 'nominal']
        widgets = {
            'tanggal': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'tanggal': 'Tanggal Transaksi',
            'uraian': 'Keterangan / Uraian',
            'akun_debit': 'Akun Debit',
            'akun_kredit': 'Akun Kredit',
            'nominal': 'Jumlah (Nominal)'
        }

class AkunForm(forms.ModelForm):
    class Meta:
        model = Akun
        fields = ['kode', 'nama', 'kategori']
        labels = {
            'kode': 'Kode Akun',
            'nama': 'Nama Akun',
            'kategori': 'Kategori Laporan'
        }

class InboundForm(forms.ModelForm):
    class Meta:
        model = InboundTransaction
        fields = [
            'tanggal_stt', 'tanggal_masuk_stt', 'vendor', 'no_resi', 'tujuan',
            'koli', 'kilo', 'tanggal_dooring', 'tanggal_kembali',
            'keterangan', 'tarif_per_kg', 'total_biaya'
        ]
        widgets = {
            'tanggal_stt': forms.DateInput(attrs={'type': 'date'}),
            'tanggal_masuk_stt': forms.DateInput(attrs={'type': 'date'}),
            'tanggal_dooring': forms.DateInput(attrs={'type': 'date'}),
            'tanggal_kembali': forms.DateInput(attrs={'type': 'date'}),
            'keterangan': forms.Textarea(attrs={'rows': 2}),
        }
        labels = {
            'tanggal_stt': 'Tanggal STT',
            'tanggal_masuk_stt': 'Tanggal Masuk STT',
            'vendor': 'Vendor',
            'no_resi': 'No Resi',
            'tujuan': 'Tujuan',
            'koli': 'Koli',
            'kilo': 'Berat (Kg)',
            'tanggal_dooring': 'Tanggal Dooring',
            'tanggal_kembali': 'Tanggal Kembali',
            'keterangan': 'Keterangan',
            'tarif_per_kg': 'Tarif per Kg',
            'total_biaya': 'Total Biaya (Rp)'
        }

class OutboundForm(forms.ModelForm):
    class Meta:
        model = OutboundTransaction
        fields = [
            'tanggal', 'pengirim', 'penerima', 'no_hp', 'no_resi_bmm',
            'koli', 'kg', 'tarif', 'total',
            'vendor1_tgl', 'vendor1_resi', 'vendor1_biaya',
            'vendor2_tgl', 'vendor2_resi', 'vendor2_biaya',
            'keterangan', 'status', 'tgl_bayar', 'nama_bayar', 'profit'
        ]
        widgets = {
            'tanggal': forms.DateInput(attrs={'type': 'date'}),
            'vendor1_tgl': forms.DateInput(attrs={'type': 'date'}),
            'vendor2_tgl': forms.DateInput(attrs={'type': 'date'}),
            'tgl_bayar': forms.DateInput(attrs={'type': 'date'}),
            'keterangan': forms.Textarea(attrs={'rows': 2}),
        }
        labels = {
            'tanggal': 'Tanggal',
            'pengirim': 'Pengirim',
            'penerima': 'Penerima',
            'no_hp': 'No HP',
            'no_resi_bmm': 'No Resi BMM',
            'koli': 'Koli',
            'kg': 'Berat (Kg)',
            'tarif': 'Tarif',
            'total': 'Total (Rp)',
            'vendor1_tgl': 'Vendor 1 - Tanggal',
            'vendor1_resi': 'Vendor 1 - No Resi',
            'vendor1_biaya': 'Vendor 1 - Biaya',
            'vendor2_tgl': 'Vendor 2 - Tanggal',
            'vendor2_resi': 'Vendor 2 - No Resi',
            'vendor2_biaya': 'Vendor 2 - Biaya',
            'keterangan': 'Keterangan',
            'status': 'Status Bayar',
            'tgl_bayar': 'Tanggal Bayar',
            'nama_bayar': 'Nama Pembayar',
            'profit': 'Profit (Rp)'
        }

class PenerimaanForm(forms.ModelForm):
    class Meta:
        model = Penerimaan
        fields = ['tanggal', 'keterangan', 'nilai', 'catatan']
        widgets = {
            'tanggal': forms.DateInput(attrs={'type': 'date'}),
            'keterangan': forms.Textarea(attrs={'rows': 2}),
            'catatan': forms.Textarea(attrs={'rows': 2}),
        }
        labels = {
            'tanggal': 'Tanggal',
            'keterangan': 'Keterangan Penerimaan',
            'nilai': 'Nilai (Rp)',
            'catatan': 'Catatan Tambahan'
        }

class ManifestForm(forms.ModelForm):
    class Meta:
        model = Manifest
        fields = [
            'kategori', 'tanggal_kirim', 'no_resi', 'pengirim', 'tujuan',
            'koli', 'kg', 'penerima', 'tanggal_terima', 'total', 'dp', 'status_bayar'
        ]
        widgets = {
            'tanggal_kirim': forms.DateInput(attrs={'type': 'date'}),
            'tanggal_terima': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'kategori': 'Kategori/Rute',
            'tanggal_kirim': 'Tanggal Kirim',
            'no_resi': 'No Resi',
            'pengirim': 'Pengirim',
            'tujuan': 'Tujuan',
            'koli': 'Koli',
            'kg': 'Berat (Kg)',
            'penerima': 'Penerima',
            'tanggal_terima': 'Tanggal Terima',
            'total': 'Total Hutang (Rp)',
            'dp': 'Biaya Dibayar Dimuka (DP)',
            'status_bayar': 'Sudah Dibayar',
        }

class KasHarianForm(forms.ModelForm):
    class Meta:
        model = KasHarian
        fields = ['tanggal', 'keterangan', 'debit', 'kredit', 'catatan']
        widgets = {
            'tanggal': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'keterangan': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Keterangan transaksi'}),
            'debit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'kredit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'catatan': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Catatan tambahan (opsional)'}),
        }
        labels = {
            'tanggal': 'Tanggal',
            'keterangan': 'Keterangan',
            'debit': 'Debit / Kas Masuk (Rp)',
            'kredit': 'Kredit / Kas Keluar (Rp)',
            'catatan': 'Catatan',
        }

# ============================================
# FORMS GAJI & KARYAWAN
# ============================================
from .models import Karyawan, Cashbon, Penggajian

class KaryawanForm(forms.ModelForm):
    class Meta:
        model = Karyawan
        fields = ['nama', 'posisi', 'gaji_pokok', 'no_hp', 'tanggal_masuk', 'status']
        widgets = {
            'tanggal_masuk': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'nama': 'Nama Karyawan',
            'posisi': 'Jabatan / Posisi',
            'gaji_pokok': 'Gaji Pokok (Rp)',
            'no_hp': 'Nomor HP/WA',
            'tanggal_masuk': 'Tanggal Masuk',
            'status': 'Status Aktif',
        }

class CashbonForm(forms.ModelForm):
    class Meta:
        model = Cashbon
        fields = ['karyawan', 'tanggal', 'nominal', 'keterangan']
        widgets = {
            'tanggal': forms.DateInput(attrs={'type': 'date'}),
            'keterangan': forms.Textarea(attrs={'rows': 2}),
        }
        labels = {
            'karyawan': 'Nama Karyawan',
            'tanggal': 'Tanggal Pinjam',
            'nominal': 'Jumlah (Rp)',
            'keterangan': 'Keterangan Keperluan',
        }

class PenggajianForm(forms.ModelForm):
    class Meta:
        model = Penggajian
        fields = [
            'karyawan', 'bulan', 'tahun', 'tanggal_gaji', 
            'gaji_pokok', 'lembur', 'bonus', 
            'potongan_cashbon', 'potongan_absen', 'potongan_bpjs', 'potongan_lain', 'catatan', 'status'
        ]
        widgets = {
            'tanggal_gaji': forms.DateInput(attrs={'type': 'date'}),
            'catatan': forms.Textarea(attrs={'rows': 2}),
        }
        labels = {
            'potongan_cashbon': 'Potongan Cashbon (Rp)',
            'potongan_lain': 'Potongan Lain-lain (Hutang Kantin dll)',
        }

class InvoiceTagihanForm(forms.ModelForm):
    class Meta:
        model = InvoiceTagihan
        fields = ['no_invoice', 'customer', 'tanggal', 'jatuh_tempo', 'total', 'biaya_awb', 'biaya_handling', 'status']
        widgets = {
            'tanggal': forms.DateInput(attrs={'type': 'date'}),
            'jatuh_tempo': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'no_invoice': 'Nomor Invoice',
            'customer': 'Nama Customer',
            'tanggal': 'Tanggal Invoice',
            'jatuh_tempo': 'Jatuh Tempo',
            'total': 'Total Tagihan (Rp)',
            'biaya_awb': 'Biaya Kirim AWB (Rp)',
            'biaya_handling': 'Biaya Handling (Rp)',
            'status': 'Status Pembayaran'
        }
