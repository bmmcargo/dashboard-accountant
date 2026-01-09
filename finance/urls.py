from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('jurnal/', views.jurnal_list, name='jurnal_list'),
    path('jurnal/edit/<int:pk>/', views.jurnal_edit, name='jurnal_edit'),
    path('jurnal/delete/<int:pk>/', views.jurnal_delete, name='jurnal_delete'),
    path('buku-besar/', views.buku_besar, name='buku_besar'),
    path('laporan/', views.laporan_keuangan, name='laporan_keuangan'),
    
    # Master Data Akun
    path('akun/', views.akun_list, name='akun_list'),
    path('akun/tambah/', views.akun_create, name='akun_create'),
    path('akun/edit/<int:pk>/', views.akun_update, name='akun_update'),
    path('akun/hapus/<int:pk>/', views.akun_delete, name='akun_delete'),

    # Inbound
    path('inbound/', views.inbound_list, name='inbound_list'),
    path('inbound/tambah/', views.inbound_create, name='inbound_create'),
    path('inbound/edit/<int:pk>/', views.inbound_edit, name='inbound_edit'),
    path('inbound/delete/<int:pk>/', views.inbound_delete, name='inbound_delete'),
    path('inbound/invoice/<int:pk>/', views.invoice_inbound, name='invoice_inbound'),

    # Outbound
    path('outbound/', views.outbound_list, name='outbound_list'),
    path('outbound/tambah/', views.outbound_create, name='outbound_create'),
    path('outbound/edit/<int:pk>/', views.outbound_edit, name='outbound_edit'),
    path('outbound/delete/<int:pk>/', views.outbound_delete, name='outbound_delete'),

    # Manifest (Hutang)
    path('manifest/', views.manifest_list, name='manifest_list'),
    path('manifest/tambah/', views.manifest_create, name='manifest_create'),
    path('manifest/edit/<int:pk>/', views.manifest_edit, name='manifest_edit'),
    path('manifest/delete/<int:pk>/', views.manifest_delete, name='manifest_delete'),

    # Kas Harian (Standalone per Bulan)
    path('kas-harian/', views.kas_harian_list, name='kas_harian_list'),
    path('kas-harian/tambah/', views.kas_harian_create, name='kas_harian_create'),
    path('kas-harian/edit/<int:pk>/', views.kas_harian_edit, name='kas_harian_edit'),
    path('kas-harian/delete/<int:pk>/', views.kas_harian_delete, name='kas_harian_delete'),
    
    
    # Tagihan Kolektif
    path('tagihan/', views.invoice_list, name='invoice_list'),
    path('tagihan/baru/', views.tagihan_create, name='tagihan_create'),
    path('tagihan/edit/<int:pk>/', views.tagihan_edit, name='tagihan_edit'),
    path('tagihan/print/<int:pk>/', views.invoice_tagihan_print, name='invoice_tagihan_print'),
    path('tagihan/delete/<int:pk>/', views.tagihan_delete, name='tagihan_delete'),

    # Buku Pembantu
    path('buku-piutang/', views.buku_piutang, name='buku_piutang'),
    path('buku-hutang/', views.buku_hutang, name='buku_hutang'),

    # Gaji & Karyawan
    path('karyawan/', views.karyawan_list, name='karyawan_list'),
    path('karyawan/tambah/', views.karyawan_create, name='karyawan_create'),
    path('karyawan/edit/<int:pk>/', views.karyawan_edit, name='karyawan_edit'),
    path('karyawan/hapus/<int:pk>/', views.karyawan_delete, name='karyawan_delete'),

    path('gaji/', views.gaji_list, name='gaji_list'),
    path('gaji/save/', views.gaji_save_all, name='gaji_save_all'),
    
    path('cashbon/', views.cashbon_list, name='cashbon_list'),
    path('cashbon/edit/<int:pk>/', views.cashbon_edit, name='cashbon_edit'),
    path('cashbon/delete/<int:pk>/', views.cashbon_delete, name='cashbon_delete'),
]
