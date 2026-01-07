from django import forms
from .models import Jurnal, Akun, InboundTransaction, OutboundTransaction, Penerimaan, Manifest

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
            'koli', 'kg', 'penerima', 'tanggal_terima', 'tarif', 'total', 'status_bayar'
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
            'tarif': 'Tarif (Rp)',
            'total': 'Total Hutang (Rp)',
            'status_bayar': 'Sudah Dibayar',
        }
