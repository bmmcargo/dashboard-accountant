from django.db import models

class Akun(models.Model):
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
        if self.kategori in ['ASSET', 'EXPENSE']:
            return 'DEBIT'
        return 'CREDIT'

class Jurnal(models.Model):
    tanggal = models.DateField()
    uraian = models.CharField(max_length=255, help_text="Keterangan transaksi")
    akun_debit = models.ForeignKey(Akun, on_delete=models.CASCADE, related_name='debit_entries', verbose_name="Akun Debit")
    akun_kredit = models.ForeignKey(Akun, on_delete=models.CASCADE, related_name='kredit_entries', verbose_name="Akun Kredit")
    nominal = models.DecimalField(max_digits=15, decimal_places=0, help_text="Jumlah Rupiah")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-tanggal', '-created_at']
        verbose_name_plural = "Jurnal Umum"

    def __str__(self):
        return f"{self.tanggal} - {self.uraian} - Rp {self.nominal:,}"

# ============================================
# MODEL INBOUND (Barang Masuk) - Updated
# ============================================
class InboundTransaction(models.Model):
    # Kolom sesuai CSV INBOUND_2026 (1).csv - tanpa TANGGAL TERIMA CUST
    tanggal_stt = models.DateField(null=True, blank=True)
    tanggal_masuk_stt = models.DateField(null=True, blank=True)
    vendor = models.CharField(max_length=100, null=True, blank=True)
    no_resi = models.CharField(max_length=100, unique=True, verbose_name="No Resi")
    tujuan = models.CharField(max_length=100, null=True, blank=True)
    koli = models.IntegerField(default=0)
    kilo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tanggal_dooring = models.DateField(null=True, blank=True)
    tanggal_kembali = models.DateField(null=True, blank=True)
    keterangan = models.TextField(null=True, blank=True)
    tarif_per_kg = models.CharField(max_length=100, null=True, blank=True)
    total_biaya = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name="Total (Rp)")
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-tanggal_masuk_stt']
        verbose_name = "Transaksi Inbound"
        verbose_name_plural = "Daftar Inbound"

    def __str__(self):
        return f"{self.no_resi} - {self.vendor}"

# ============================================
# MODEL OUTBOUND (Barang Keluar) - Updated for Lap_outbond format
# ============================================
class OutboundTransaction(models.Model):
    # Kolom sesuai Lap_outbond_bmm_Agustus_2022.csv
    tanggal = models.DateField(null=True, blank=True, verbose_name="Tanggal")
    pengirim = models.CharField(max_length=200, null=True, blank=True)
    penerima = models.CharField(max_length=200, null=True, blank=True)
    no_hp = models.CharField(max_length=50, null=True, blank=True)
    no_resi_bmm = models.CharField(max_length=100, unique=True, verbose_name="No Resi BMM")
    koli = models.IntegerField(default=0)
    kg = models.CharField(max_length=50, null=True, blank=True)  # Bisa berisi "MOTOR", "SEPEDA", angka
    tarif = models.CharField(max_length=100, null=True, blank=True)
    total = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name="Total (Rp)")
    
    # Vendor info
    vendor1_tgl = models.DateField(null=True, blank=True)
    vendor1_resi = models.CharField(max_length=100, null=True, blank=True)
    vendor1_biaya = models.DecimalField(max_digits=15, decimal_places=0, default=0)
    
    vendor2_tgl = models.DateField(null=True, blank=True)
    vendor2_resi = models.CharField(max_length=100, null=True, blank=True)
    vendor2_biaya = models.DecimalField(max_digits=15, decimal_places=0, default=0)
    
    keterangan = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)  # COD, CASH, TRANSFER
    tgl_bayar = models.DateField(null=True, blank=True)
    nama_bayar = models.CharField(max_length=100, null=True, blank=True)
    profit = models.DecimalField(max_digits=15, decimal_places=0, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-tanggal']
        verbose_name = "Transaksi Outbound"
        verbose_name_plural = "Daftar Outbound"

    def __str__(self):
        return f"{self.no_resi_bmm} - {self.pengirim}"

# ============================================
# MODEL PENERIMAAN (Pendapatan Di Luar Piutang)
# ============================================
class Penerimaan(models.Model):
    tanggal = models.DateField()
    keterangan = models.CharField(max_length=255)
    nilai = models.DecimalField(max_digits=15, decimal_places=0, default=0)
    saldo = models.DecimalField(max_digits=15, decimal_places=0, default=0)
    catatan = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['tanggal']
        verbose_name = "Penerimaan"
        verbose_name_plural = "Daftar Penerimaan"

    def __str__(self):
        return f"{self.tanggal} - {self.keterangan} - Rp {self.nilai:,}"

# ============================================
# MODEL MANIFEST (Hutang ke Vendor)
# ============================================
class Manifest(models.Model):
    KATEGORI_CHOICES = [
        ('HULU', 'Hulu'),
        ('KETAPANG', 'Ketapang'),
        ('PANTURA', 'Pantura'),
        ('PUTUSSIBAU', 'Putussibau'),
        ('TRUK', 'Truk'),
        ('KALTENG', 'Kalteng'),
    ]
    
    kategori = models.CharField(max_length=50, choices=KATEGORI_CHOICES, default='HULU')
    tanggal_kirim = models.DateField(null=True, blank=True)
    no_resi = models.CharField(max_length=100)
    pengirim = models.CharField(max_length=200, null=True, blank=True)
    tujuan = models.CharField(max_length=200, null=True, blank=True)
    koli = models.IntegerField(default=0)
    kg = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    penerima = models.CharField(max_length=200, null=True, blank=True)
    tanggal_terima = models.DateField(null=True, blank=True)
    tarif = models.DecimalField(max_digits=15, decimal_places=0, default=0)
    total = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name="Total Hutang (Rp)")
    status_bayar = models.BooleanField(default=False, verbose_name="Sudah Dibayar")
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-tanggal_kirim', 'kategori']
        verbose_name = "Manifest"
        verbose_name_plural = "Daftar Manifest"
        unique_together = ['no_resi', 'kategori']

    def __str__(self):
        return f"{self.kategori} - {self.no_resi} - {self.pengirim}"