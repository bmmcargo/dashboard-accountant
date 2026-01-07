import csv
import os
import re
from datetime import datetime
from django.core.management.base import BaseCommand
from finance.models import Jurnal, Akun

class Command(BaseCommand):
    help = 'Import data transaksi dari file CSV Kas Harian BMM'

    def handle(self, *args, **kwargs):
        self.stdout.write("Memulai Import Data Kas Harian BMM...")
        
        # Pastikan file ini ada di folder root (sejajar manage.py)
        file_path = 'kas_harian.csv' 
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File {file_path} tidak ditemukan!'))
            return

        # Pastikan Akun Kas (101) ada
        try:
            akun_kas = Akun.objects.get(kode='101')
        except Akun.DoesNotExist:
            self.stdout.write(self.style.ERROR('Akun Kas (101) belum ada. Jalankan: python manage.py seed_accounts'))
            return

        # Mapping Keyword -> Kode Akun Tujuan (Debit)
        keyword_map = {
            'gaji': '501', 'karyawan': '501', 'thr': '501',
            'bensin': '502', 'solar': '502', 'tol': '502', 'parkir': '502', 'bbm': '502',
            'bongkar': '503', 'muat': '503',
            'sangu': '504', 'jalan': '504',
            'service': '520', 'oli': '520', 'ban': '520', 'sparepart': '520', 'bengkel': '520', 'perbaikan': '520',
            'listrik': '513', 'pulsa': '513', 'kuota': '513',
            'atk': '114', 'kertas': '114', 'fotocopy': '114',
            'kasbon': '113', 'pinjaman': '113',
            'konsumsi': '514', 'makan': '514', 'minum': '514',
        }

        count_sukses = 0
        count_skip = 0
        
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            # Lewati header (4 baris awal: nama perusahaan, judul, periode, header kolom)
            for _ in range(4): 
                next(reader, None)
            
            for row in reader:
                # Struktur CSV: NO(0), TANGGAL(1), KETERANGAN(2), KREDIT/KELUAR(3), SALDO(4)
                if len(row) < 4: 
                    continue
                
                # Skip jika kolom tanggal atau nominal kosong
                if not row[1].strip() or not row[3].strip():
                    continue

                try:
                    # Format Tanggal: bisa DD/MM/YY, M/DD/YYYY, atau YYYY-MM-DD
                    tgl_str = row[1].strip()
                    tgl_obj = None
                    
                    # Coba berbagai format tanggal
                    date_formats = [
                        '%d/%m/%y',      # 01/09/22
                        '%d/%m/%Y',      # 01/09/2022
                        '%m/%d/%Y',      # 9/23/2022 (format US)
                        '%m/%d/%y',      # 9/23/22
                        '%Y-%m-%d',      # 2022-09-01
                    ]
                    
                    for fmt in date_formats:
                        try:
                            tgl_obj = datetime.strptime(tgl_str, fmt).date()
                            break
                        except:
                            continue
                    
                    if tgl_obj is None:
                        count_skip += 1
                        continue
                    
                    # Bersihkan Nominal: " Rp11,738,000 " -> 11738000
                    nominal_str = row[3].strip()
                    # Hapus Rp, spasi, koma, titik
                    nominal_str = re.sub(r'[Rp\s,.]', '', nominal_str)
                    
                    if not nominal_str or nominal_str == '-': 
                        continue
                    
                    nominal = int(nominal_str)
                    if nominal == 0: 
                        continue

                    uraian = row[2].strip()
                    uraian_lower = uraian.lower()

                    # Cari akun debit berdasarkan kata kunci
                    kode_debit = '514'  # Default ke Beban Lain-lain
                    for keyword, kode in keyword_map.items():
                        if keyword in uraian_lower:
                            kode_debit = kode
                            break
                    
                    # Get or Create Akun Debit
                    akun_debit, _ = Akun.objects.get_or_create(
                        kode=kode_debit, 
                        defaults={'nama': 'Auto Generated', 'kategori': 'EXPENSE'}
                    )

                    # Cek duplikasi sebelum simpan
                    if not Jurnal.objects.filter(tanggal=tgl_obj, uraian=uraian, nominal=nominal).exists():
                        Jurnal.objects.create(
                            tanggal=tgl_obj,
                            uraian=uraian,
                            akun_debit=akun_debit,
                            akun_kredit=akun_kas,
                            nominal=nominal
                        )
                        count_sukses += 1
                        self.stdout.write(f"OK: {tgl_obj} - {uraian[:30]} - Rp{nominal:,}")

                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Skip: {e}"))
                    count_skip += 1
                    continue
        
        self.stdout.write(self.style.SUCCESS(f'\nSelesai! Import {count_sukses} transaksi. Skip {count_skip} baris.'))