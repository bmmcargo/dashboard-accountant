from django.db import models

class Akun(models.Model):
    # Pilihan Kategori Akun (Standar Akuntansi)
    KATEGORI_CHOICES = [
        ('ASSET', 'Harta (Aktiva)'),
        ('LIABILITY', 'Kewajiban (Utang)'),
        ('EQUITY', 'Modal (Ekuitas)'),
        ('REVENUE', 'Pendapatan'),
        ('EXPENSE', 'Beban'),
    ]
    
    kode = models.CharField(max_length=20, unique=True, help_text="Contoh: 111 (Kas), 411 (Pendapatan)")
    nama = models.CharField(max_length=100, help_text="Contoh: Kas, Modal, Beban Gaji")
    kategori = models.CharField(max_length=20, choices=KATEGORI_CHOICES)

    def __str__(self):
        return f"{self.kode} - {self.nama}"

    @property
    def saldo_normal(self):
        """Menentukan saldo normal akun (Debit/Kredit)."""
        if self.kategori in ['ASSET', 'EXPENSE']:
            return 'DEBIT'
        return 'CREDIT'

class Jurnal(models.Model):
    tanggal = models.DateField()
    uraian = models.CharField(max_length=255, help_text="Keterangan transaksi")
    
    # Relasi ke Tabel Akun
    akun_debit = models.ForeignKey(Akun, on_delete=models.CASCADE, related_name='debit_entries', verbose_name="Akun Debit")
    akun_kredit = models.ForeignKey(Akun, on_delete=models.CASCADE, related_name='kredit_entries', verbose_name="Akun Kredit")
    
    nominal = models.DecimalField(max_digits=15, decimal_places=0, help_text="Jumlah Rupiah")
    created_at = models.DateTimeField(auto_now_add=True) # Untuk sorting

    class Meta:
        ordering = ['-tanggal', '-created_at']
        verbose_name_plural = "Jurnal Umum"

    def __str__(self):
        return f"{self.tanggal} - {self.uraian} - Rp {self.nominal:,}"