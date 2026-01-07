from django import forms
from .models import Jurnal, Akun

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
