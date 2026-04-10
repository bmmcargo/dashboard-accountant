from django.core.management.base import BaseCommand
from finance.models import Akun

class Command(BaseCommand):
    help = 'Isi Daftar Akun (CoA) BMM Cargo'

    def handle(self, *args, **kwargs):
        akun_bmm = [
            ('101', 'Kas Operasional', 'ASSET'),
            ('113', 'Piutang Karyawan (Kasbon)', 'ASSET'),
            ('114', 'Perlengkapan (ATK)', 'ASSET'),
            ('301', 'Modal Pemilik', 'EQUITY'),
            ('401', 'Pendapatan Jasa', 'REVENUE'),
            ('501', 'Beban Gaji', 'EXPENSE'),
            ('502', 'Beban BBM & Tol', 'EXPENSE'),
            ('503', 'Beban Bongkar Muat', 'EXPENSE'),
            ('504', 'Beban Sangu Jalan', 'EXPENSE'),
            ('520', 'Beban Service & Sparepart', 'EXPENSE'), # Request Khusus Client
            ('513', 'Beban Listrik/Pulsa', 'EXPENSE'),
            ('514', 'Beban Lain-lain', 'EXPENSE'),
        ]

        for kode, nama, kategori in akun_bmm:
            Akun.objects.get_or_create(kode=kode, defaults={'nama': nama, 'kategori': kategori})
            
        self.stdout.write(self.style.SUCCESS('Akun BMM Berhasil Dibuat!'))