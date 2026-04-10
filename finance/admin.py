from django.contrib import admin
from .models import (
    Akun, Jurnal, InboundTransaction, OutboundTransaction, Manifest, 
    KasHarian, InvoiceTagihan, OpsInbound, OpsOutbound, OpsManifest
)

@admin.register(Akun)
class AkunAdmin(admin.ModelAdmin):
    list_display = ('kode', 'nama', 'kategori', 'saldo_normal')
    list_filter = ('kategori',)
    search_fields = ('kode', 'nama')

@admin.register(Jurnal)
class JurnalAdmin(admin.ModelAdmin):
    list_display = ('tanggal', 'uraian', 'akun_debit', 'akun_kredit', 'nominal')
    list_filter = ('tanggal', 'akun_debit', 'akun_kredit')
    search_fields = ('uraian',)
    date_hierarchy = 'tanggal'

@admin.register(InboundTransaction)
class InboundAdmin(admin.ModelAdmin):
    list_display = ('tanggal_masuk_stt', 'no_resi', 'vendor', 'tujuan', 'total_biaya')
    search_fields = ('no_resi', 'vendor', 'tujuan')

@admin.register(OutboundTransaction)
class OutboundAdmin(admin.ModelAdmin):
    list_display = ('tanggal', 'no_resi_bmm', 'pengirim', 'penerima', 'total')
    search_fields = ('no_resi_bmm', 'pengirim', 'penerima')

@admin.register(Manifest)
class ManifestAdmin(admin.ModelAdmin):
    list_display = ('tanggal_kirim', 'no_resi', 'kategori', 'pengirim', 'total', 'status_bayar')
    list_filter = ('kategori', 'status_bayar')
    search_fields = ('no_resi', 'pengirim')

@admin.register(KasHarian)
class KasHarianAdmin(admin.ModelAdmin):
    list_display = ('tanggal', 'keterangan', 'jenis', 'debit', 'kredit', 'saldo')
    list_filter = ('jenis', 'tanggal')

@admin.register(InvoiceTagihan)
class InvoiceTagihanAdmin(admin.ModelAdmin):
    list_display = ('no_invoice', 'tanggal', 'customer', 'total', 'status')
    list_filter = ('status', 'tanggal')
    search_fields = ('no_invoice', 'customer')

# --- Admin for NEW Operational Models ---

@admin.register(OpsInbound)
class OpsInboundAdmin(admin.ModelAdmin):
    list_display = ('nomor_resi', 'tanggal', 'pengirim', 'penerima', 'berat', 'status')
    list_filter = ('status', 'tanggal')
    search_fields = ('nomor_resi', 'pengirim', 'penerima')

@admin.register(OpsManifest)
class OpsManifestAdmin(admin.ModelAdmin):
    list_display = ('nomor_manifest', 'tanggal', 'armada', 'rute', 'status')
    list_filter = ('status', 'tanggal')
    search_fields = ('nomor_manifest', 'armada', 'rute')

@admin.register(OpsOutbound)
class OpsOutboundAdmin(admin.ModelAdmin):
    list_display = ('inbound', 'manifest', 'tanggal')
    list_filter = ('tanggal',)