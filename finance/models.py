from django.db import models
from django.utils import timezone

class Akun(models.Model):
    KATEGORI_CHOICES = [
        ('ASSET', 'Harta (Aktiva)'),
        ('LIABILITY', 'Kewajiban (Utang)'),
        ('EQUITY', 'Modal (Ekuitas)'),
        ('REVENUE', 'Pendapatan'),
        ('EXPENSE', 'Biaya'),
    ]
    
    kode = models.CharField(max_length=20, unique=True, help_text="Contoh: 111 (Kas), 411 (Pendapatan)")
    nama = models.CharField(max_length=100, help_text="Contoh: Kas, Modal, Biaya Gaji")
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
# MODEL INVOICE TAGIHAN (Kolektif)
# ============================================
class InvoiceTagihan(models.Model):
    no_invoice = models.CharField(max_length=50, unique=True)
    customer = models.CharField(max_length=100) # Nama Customer (Vendor di Inbound)
    tanggal = models.DateField(default=timezone.now)
    jatuh_tempo = models.DateField(null=True, blank=True)
    total = models.DecimalField(max_digits=15, decimal_places=0, default=0)
    status = models.CharField(max_length=20, default='BELUM BAYAR') # BELUM BAYAR, LUNAS
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-tanggal', '-no_invoice']
    
    def __str__(self):
        return self.no_invoice

# ============================================
# MODEL INBOUND (Barang Masuk) - Updated
# ============================================
class InboundTransaction(models.Model):
    # Relasi ke Invoice Tagihan (bs null jika belum ditagihkan)
    invoice = models.ForeignKey(InvoiceTagihan, on_delete=models.SET_NULL, null=True, blank=True, related_name='inbound_items')
    
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

# --- SIGNALS FOR AUTO JOURNAL ---
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver(post_save, sender=InboundTransaction)
def create_or_update_jurnal_inbound(sender, instance, created, **kwargs):
    """
    Otomatis buat/update jurnal saat InboundTransaction disimpan.
    Debit: Piutang Usaha (112)
    Kredit: Pendapatan Jasa (402)
    """
    if instance.total_biaya <= 0:
        return

    # Cari Akun
    try:
        akun_piutang = Akun.objects.get(kode='112') # Piutang Usaha
    except Akun.DoesNotExist:
        # Fallback cari berdasarkan nama atau create dummy (sebaiknya jangan create dummy sembarangan)
        akun_piutang = Akun.objects.filter(nama__icontains='Piutang').first()
        if not akun_piutang: return # Abort if no account

    try:
        akun_pendapatan = Akun.objects.get(kode='402') # Pendapatan Jasa Inbound
    except Akun.DoesNotExist:
        try:
            akun_pendapatan = Akun.objects.get(kode='401') # Pendapatan Jasa Umum
        except Akun.DoesNotExist:
            return # Abort

    uraian_jurnal = f"Invoice Inbound: {instance.no_resi} - {instance.vendor}"
    tanggal_jurnal = instance.tanggal_masuk_stt or instance.created_at.date()

    # Cek apakah jurnal sudah ada (berdasarkan uraian unik ini)
    jurnal = Jurnal.objects.filter(uraian=uraian_jurnal).first()

    if jurnal:
        # Update existing
        jurnal.tanggal = tanggal_jurnal
        jurnal.akun_debit = akun_piutang
        jurnal.akun_kredit = akun_pendapatan
        jurnal.nominal = instance.total_biaya
        jurnal.save()
    else:
        # Create new
        Jurnal.objects.create(
            tanggal=tanggal_jurnal,
            uraian=uraian_jurnal,
            akun_debit=akun_piutang,
            akun_kredit=akun_pendapatan,
            nominal=instance.total_biaya
        )

@receiver(post_delete, sender=InboundTransaction)
def delete_jurnal_inbound(sender, instance, **kwargs):
    """Hapus jurnal jika transaksi inbound dihapus"""
    uraian_jurnal = f"Invoice Inbound: {instance.no_resi} - {instance.vendor}"
    Jurnal.objects.filter(uraian=uraian_jurnal).delete()


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

@receiver(post_save, sender=Manifest)
def create_or_update_jurnal_manifest(sender, instance, created, **kwargs):
    """
    Otomatis buat/update jurnal saat Manifest disimpan.
    Debit: Beban Pengiriman/Logistik (5xx)
    Kredit: Hutang Usaha (211)
    """
    if instance.total <= 0:
        return

    # Cari Akun Hutang (211)
    try:
        akun_hutang = Akun.objects.get(kode='211') 
    except Akun.DoesNotExist:
        akun_hutang = Akun.objects.filter(nama__icontains='Hutang').first()
        if not akun_hutang: return 

    # Cari Akun Beban (5xx)
    # Gunakan akun Beban Operasional atau HPP tergantung kebijakan
    # Kita cari akun dengan kode awalan 5 (Beban)
    akun_beban = Akun.objects.filter(kode__startswith='5').first()
    if not akun_beban: return

    uraian_jurnal = f"Hutang Manifest: {instance.kategori} - {instance.no_resi}"
    tanggal_jurnal = instance.tanggal_kirim or instance.created_at.date()

    # Cek jurnal existing
    jurnal = Jurnal.objects.filter(uraian=uraian_jurnal).first()

    if jurnal:
        jurnal.tanggal = tanggal_jurnal
        jurnal.akun_debit = akun_beban
        jurnal.akun_kredit = akun_hutang
        jurnal.nominal = instance.total
        jurnal.save()
    else:
        Jurnal.objects.create(
            tanggal=tanggal_jurnal,
            uraian=uraian_jurnal,
            akun_debit=akun_beban,
            akun_kredit=akun_hutang,
            nominal=instance.total
        )

@receiver(post_delete, sender=Manifest)
def delete_jurnal_manifest(sender, instance, **kwargs):
    uraian_jurnal = f"Hutang Manifest: {instance.kategori} - {instance.no_resi}"
    Jurnal.objects.filter(uraian=uraian_jurnal).delete()

# ============================================
# MODEL KAS HARIAN (Standalone - Tidak Link ke Jurnal)
# ============================================
class KasHarian(models.Model):
    JENIS_CHOICES = [
        ('MASUK', 'Kas Masuk'),
        ('KELUAR', 'Kas Keluar'),
    ]
    
    tanggal = models.DateField()
    keterangan = models.CharField(max_length=255)
    jenis = models.CharField(max_length=10, choices=JENIS_CHOICES, default='KELUAR')
    debit = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name="Debit (Masuk)")
    kredit = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name="Kredit (Keluar)")
    saldo = models.DecimalField(max_digits=15, decimal_places=0, default=0)
    catatan = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['tanggal', 'created_at']
        verbose_name = "Kas Harian"
        verbose_name_plural = "Kas Harian"

    def __str__(self):
        return f"{self.tanggal} - {self.keterangan}"
    
    @property
    def bulan(self):
        return self.tanggal.month
    
    @property
    def tahun(self):
        return self.tanggal.year

@receiver(post_save, sender=InboundTransaction)
def update_invoice_total_on_save(sender, instance, **kwargs):
    """
    Update total tagihan invoice jika inbound diedit atau ditambahkan ke invoice.
    """
    if instance.invoice:
        from django.db.models import Sum
        total = instance.invoice.inbound_items.aggregate(Sum('total_biaya'))['total_biaya__sum'] or 0
        instance.invoice.total = total
        instance.invoice.save()

@receiver(post_delete, sender=InboundTransaction)
def update_invoice_total_on_delete(sender, instance, **kwargs):
    """
    Update total tagihan invoice jika inbound dihapus.
    """
    if instance.invoice:
        from django.db.models import Sum
        total = instance.invoice.inbound_items.aggregate(Sum('total_biaya'))['total_biaya__sum'] or 0
        instance.invoice.total = total
        instance.invoice.save()