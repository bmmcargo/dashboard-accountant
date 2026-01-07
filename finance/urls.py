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
]
