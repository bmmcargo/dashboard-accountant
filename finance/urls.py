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
]
