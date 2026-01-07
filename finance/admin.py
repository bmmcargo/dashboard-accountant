from django.contrib import admin
from .models import Akun, Jurnal

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