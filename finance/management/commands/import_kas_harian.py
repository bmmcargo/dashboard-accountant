import csv
import os
import re
from datetime import datetime
from django.core.management.base import BaseCommand
from finance.models import KasHarian

class Command(BaseCommand):
    help = 'Import data Kas Harian dari file CSV KAS_2026.csv'

    def handle(self, *args, **kwargs):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        file_path = os.path.join(base_dir, 'KAS_2026.csv')
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File tidak ditemukan: {file_path}'))
            return
        
        self.stdout.write(f"📥 Import Kas Harian dari: {file_path}")
        
        count = 0
        skip = 0
        
        with open(file_path, mode='r', encoding='utf-8-sig', errors='ignore') as csv_file:
            reader = csv.reader(csv_file)
            
            # Skip header rows (cari baris yang dimulai dengan tanggal)
            # Jika baris pertama adalah header (TANGGAL), skip 1 baris
            # Jika ada header perusahaan, skip sampai ketemu data
            first_row = next(reader, None)
            if first_row and first_row[0] and 'TANGGAL' in first_row[0].upper():
                pass  # Header row, lanjut ke data
            elif first_row and first_row[0] and '/' in first_row[0] and '2026' in first_row[0]:
                # Ini sudah data, proses langsung
                self.process_row(first_row)
            else:
                # Skip header lama (CV Borneo, dll)
                while True:
                    row = next(reader, None)
                    if row is None:
                        break
                    if row[0] and 'TANGGAL' in row[0].upper():
                        break  # Found header row
            
            for row in reader:
                # Minimal 4 kolom (TANGGAL, KETERANGAN, DEBET, KREDIT)
                if len(row) < 4:
                    continue
                
                tanggal_str = row[0].strip() if row[0] else ''
                keterangan = row[1].strip() if len(row) > 1 and row[1] else ''
                debit_str = row[2].strip() if len(row) > 2 and row[2] else ''
                kredit_str = row[3].strip() if len(row) > 3 and row[3] else ''
                
                # Skip jika tanggal kosong
                if not tanggal_str:
                    continue
                
                # Parse tanggal
                tanggal = self.parse_date(tanggal_str)
                if not tanggal:
                    skip += 1
                    continue
                
                # Parse nominal - boleh kosong (default 0)
                debit = self.parse_rupiah(debit_str)
                kredit = self.parse_rupiah(kredit_str)
                
                # Skip jika keduanya 0 (baris kosong)
                if debit == 0 and kredit == 0 and not keterangan:
                    skip += 1
                    continue
                
                try:

                    # Cek apakah data persis sama sudah ada (untuk menghindari duplikat saat run ulang)
                    # Kita cek tanggal, keterangan, debit, DAN kredit
                    exists = KasHarian.objects.filter(
                        tanggal=tanggal,
                        keterangan=keterangan if keterangan else f"Transaksi {tanggal_str}",
                        debit=debit,
                        kredit=kredit
                    ).exists()
                    
                    if not exists:
                        # Create new entry
                        KasHarian.objects.create(
                            tanggal=tanggal,
                            keterangan=keterangan if keterangan else f"Transaksi {tanggal_str}",
                            debit=debit,
                            kredit=kredit,
                            saldo=0
                        )
                        count += 1
                        self.stdout.write(f"  OK: {tanggal} - {keterangan[:30]} - D:{debit:,} K:{kredit:,}")
                    else:
                        skip += 1
                        self.stdout.write(f"  SKIP (Exists): {tanggal} - {keterangan[:30]}")
                        
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  Error: {e}"))
                    skip += 1
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Selesai! Import {count} data Kas Harian baru. Skip {skip} baris.'))

    def parse_date(self, date_str):
        """Parse berbagai format tanggal"""
        if not date_str:
            return None
        
        date_str = date_str.strip()
        
        # Coba berbagai format
        from datetime import datetime, date as dt_date
        
        # Coba parse manual untuk format dengan /
        if '/' in date_str:
            parts = date_str.split('/')
            if len(parts) == 3:
                try:
                    p0 = int(parts[0])
                    p1 = int(parts[1])
                    p2 = int(parts[2])
                    
                    # Fix 2 digit year
                    if p2 < 100:
                        p2 = 2000 + p2
                    
                    # Deteksi format: jika p2 > 31, itu adalah tahun
                    if p2 > 31:  # Year di posisi terakhir
                        # Cek apakah M/D/YYYY atau D/M/YYYY
                        if p1 > 12:  # p1 bukan bulan, maka M/D/YYYY
                            month, day, year = p0, p1, p2
                        elif p0 > 12:  # p0 bukan bulan, maka D/M/YYYY
                            day, month, year = p0, p1, p2
                        else:
                            # Asumsi M/D/YYYY (format US) karena data dari Excel
                            month, day, year = p0, p1, p2
                        
                        return dt_date(year, month, day)
                except Exception as e:
                    pass
        
        # Fallback ke format standar
        date_formats = [
            '%m/%d/%Y',      # 1/5/2026 (US)
            '%d/%m/%Y',      # 01/01/2026
            '%Y-%m-%d',      # 2026-01-01
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except:
                continue
        return None

    def parse_rupiah(self, val):
        """Parse format Rupiah: ' Rp126,313 ' -> 126313"""
        if not val:
            return 0
        
        val = str(val).strip()
        
        # Hapus Rp, spasi, koma, quotes
        val = re.sub(r'[Rp\s",]', '', val)
        
        # Handle kosong atau dash
        if not val or val == '-':
            return 0
        
        try:
            return int(float(val))
        except:
            return 0
