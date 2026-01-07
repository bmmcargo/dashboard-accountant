from django.core.management.base import BaseCommand
import csv
import os
import re
from datetime import datetime
from finance.models import InboundTransaction, OutboundTransaction, Penerimaan, Jurnal, Akun

class Command(BaseCommand):
    help = 'Import data Inbound, Outbound, dan Penerimaan dari CSV + Buat Jurnal Pendapatan'

    def handle(self, *args, **kwargs):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        
        # 1. IMPORT INBOUND (file baru)
        path_inbound = os.path.join(base_dir, 'INBOUND_2026 (1).csv')
        if os.path.exists(path_inbound):
            self.import_inbound(path_inbound)
        else:
            self.stdout.write(self.style.WARNING(f'File tidak ditemukan: {path_inbound}'))

        # 2. IMPORT OUTBOUND (format baru - Lap_outbond)
        path_outbound = os.path.join(base_dir, 'Lap_outbond_bmm_Agustus_2022.csv')
        if os.path.exists(path_outbound):
            self.import_outbound_lap(path_outbound)
        else:
            self.stdout.write(self.style.WARNING(f'File tidak ditemukan: {path_outbound}'))

        # 3. IMPORT PENERIMAAN (Pendapatan Diluar Piutang)
        path_penerimaan = os.path.join(base_dir, 'Lap_outbond_bmm_penerimaan_diluar_piutang.csv')
        if os.path.exists(path_penerimaan):
            self.import_penerimaan(path_penerimaan)
        else:
            self.stdout.write(self.style.WARNING(f'File tidak ditemukan: {path_penerimaan}'))

    # ==========================
    # LOGIKA IMPORT INBOUND (Format Baru - tanpa Tanggal Terima Cust)
    # ==========================
    def import_inbound(self, filepath):
        self.stdout.write(f"\nMulai Import INBOUND dari: {filepath}...")
        
        # Pastikan akun pendapatan inbound ada
        akun_pendapatan, _ = Akun.objects.get_or_create(
            kode='402', 
            defaults={'nama': 'Pendapatan Jasa Inbound', 'kategori': 'REVENUE'}
        )
        akun_kas, _ = Akun.objects.get_or_create(
            kode='101',
            defaults={'nama': 'Kas', 'kategori': 'ASSET'}
        )
        
        with open(filepath, mode='r', encoding='utf-8-sig') as csv_file:
            reader = csv.DictReader(csv_file)
            count = 0
            jurnal_count = 0
            
            for row in reader:
                no_resi = row.get('NO RESI', '').strip()
                if not no_resi:
                    continue

                try:
                    tgl_stt = self.parse_date(row.get('TANGGAL STT'))
                    tgl_masuk = self.parse_date(row.get('TANGGAL MASUK STT'))
                    tgl_door = self.parse_date(row.get('TANGGAL DOORING'))
                    tgl_kembali = self.parse_date(row.get('TANGGAL KEMBALI'))
                    
                    koli_val = self.parse_int(row.get('KOLI'))
                    kilo_val = self.parse_float(row.get('KILO'))
                    total_val = self.parse_rupiah(row.get('TOTAL', ''))
                    
                    obj, created = InboundTransaction.objects.update_or_create(
                        no_resi=no_resi,
                        defaults={
                            'tanggal_stt': tgl_stt,
                            'tanggal_masuk_stt': tgl_masuk,
                            'vendor': row.get('VENDOR'),
                            'tujuan': row.get('TUJUAN'),
                            'koli': koli_val,
                            'kilo': kilo_val,
                            'tanggal_dooring': tgl_door,
                            'tanggal_kembali': tgl_kembali,
                            'keterangan': row.get('KETERANGAN'),
                            'tarif_per_kg': row.get('TARIF/KG'),
                            'total_biaya': total_val,
                        }
                    )
                    count += 1
                    
                    # Buat Jurnal Pendapatan otomatis jika ada total
                    if total_val > 0 and tgl_masuk:
                        uraian = f"Pendapatan Inbound: {no_resi} - {row.get('VENDOR', '')} ke {row.get('TUJUAN', '')}"
                        if not Jurnal.objects.filter(tanggal=tgl_masuk, uraian=uraian[:255], nominal=total_val).exists():
                            Jurnal.objects.create(
                                tanggal=tgl_masuk,
                                uraian=uraian[:255],
                                akun_debit=akun_kas,
                                akun_kredit=akun_pendapatan,
                                nominal=total_val
                            )
                            jurnal_count += 1
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error di Resi {no_resi}: {e}"))

            self.stdout.write(self.style.SUCCESS(f"Sukses Import {count} data Inbound + {jurnal_count} Jurnal Pendapatan."))

    # ==========================
    # LOGIKA IMPORT OUTBOUND (Format Lap_outbond_bmm)
    # ==========================
    def import_outbound_lap(self, filepath):
        self.stdout.write(f"\nMulai Import OUTBOUND dari: {filepath}...")
        
        with open(filepath, mode='r', encoding='utf-8-sig') as csv_file:
            reader = csv.reader(csv_file)
            # Skip header (5 baris: judul, periode, alamat, telepon, header kolom)
            for _ in range(6):
                next(reader, None)
            
            count = 0
            
            for row in reader:
                if len(row) < 10:
                    continue
                
                # Kolom: NO, TGL, PENGIRIM, PENERIMA, NO HP, No resi BMM, Koli, KG, Tarif, Total, ...
                no_resi = row[5].strip() if len(row) > 5 else ''
                if not no_resi or no_resi == '':
                    continue

                try:
                    tgl = self.parse_date(row[1])
                    koli_val = self.parse_int(row[6]) if len(row) > 6 else 0
                    total_val = self.parse_rupiah(row[9]) if len(row) > 9 else 0
                    
                    # Vendor 1
                    v1_tgl = self.parse_date(row[10]) if len(row) > 10 else None
                    v1_resi = row[11].strip() if len(row) > 11 else ''
                    v1_biaya = self.parse_rupiah(row[12]) if len(row) > 12 else 0
                    
                    # Vendor 2
                    v2_tgl = self.parse_date(row[13]) if len(row) > 13 else None
                    v2_resi = row[14].strip() if len(row) > 14 else ''
                    v2_biaya = self.parse_rupiah(row[15]) if len(row) > 15 else 0
                    
                    # Status & Payment
                    ket = row[19].strip() if len(row) > 19 else ''
                    status = row[20].strip() if len(row) > 20 else ''
                    tgl_bayar = self.parse_date(row[21]) if len(row) > 21 else None
                    nama_bayar = row[22].strip() if len(row) > 22 else ''
                    profit = self.parse_rupiah(row[23]) if len(row) > 23 else 0
                    
                    obj, created = OutboundTransaction.objects.update_or_create(
                        no_resi_bmm=no_resi,
                        defaults={
                            'tanggal': tgl,
                            'pengirim': row[2].strip() if len(row) > 2 else '',
                            'penerima': row[3].strip() if len(row) > 3 else '',
                            'no_hp': row[4].strip() if len(row) > 4 else '',
                            'koli': koli_val,
                            'kg': row[7].strip() if len(row) > 7 else '',
                            'tarif': row[8].strip() if len(row) > 8 else '',
                            'total': total_val,
                            'vendor1_tgl': v1_tgl,
                            'vendor1_resi': v1_resi,
                            'vendor1_biaya': v1_biaya,
                            'vendor2_tgl': v2_tgl,
                            'vendor2_resi': v2_resi,
                            'vendor2_biaya': v2_biaya,
                            'keterangan': ket,
                            'status': status,
                            'tgl_bayar': tgl_bayar,
                            'nama_bayar': nama_bayar,
                            'profit': profit,
                        }
                    )
                    count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error Outbound: {e}"))

            self.stdout.write(self.style.SUCCESS(f"Sukses Import {count} data Outbound."))

    # ==========================
    # LOGIKA IMPORT PENERIMAAN
    # ==========================
    def import_penerimaan(self, filepath):
        self.stdout.write(f"\nMulai Import PENERIMAAN dari: {filepath}...")
        
        # Pastikan akun pendapatan lain-lain ada
        akun_pendapatan, _ = Akun.objects.get_or_create(
            kode='403', 
            defaults={'nama': 'Pendapatan Lain-lain', 'kategori': 'REVENUE'}
        )
        akun_kas, _ = Akun.objects.get_or_create(
            kode='101',
            defaults={'nama': 'Kas', 'kategori': 'ASSET'}
        )
        
        with open(filepath, mode='r', encoding='utf-8-sig') as csv_file:
            reader = csv.reader(csv_file)
            # Skip header (5 baris: nama, judul, periode, kosong, header kolom)
            for _ in range(5):
                next(reader, None)
            
            count = 0
            jurnal_count = 0
            
            for row in reader:
                if len(row) < 4:
                    continue
                
                # Kolom: NO, TANGGAL, PENERIMAAN, NILAI, SALDO
                keterangan = row[2].strip() if len(row) > 2 else ''
                if not keterangan:
                    continue

                try:
                    tgl = self.parse_date(row[1])
                    nilai = self.parse_rupiah(row[3]) if len(row) > 3 else 0
                    saldo = self.parse_rupiah(row[4]) if len(row) > 4 else 0
                    catatan = row[5].strip() if len(row) > 5 else ''
                    
                    if not tgl or nilai == 0:
                        continue
                    
                    obj, created = Penerimaan.objects.update_or_create(
                        tanggal=tgl,
                        keterangan=keterangan,
                        defaults={
                            'nilai': nilai,
                            'saldo': saldo,
                            'catatan': catatan,
                        }
                    )
                    count += 1
                    
                    # Buat Jurnal Pendapatan otomatis
                    uraian = f"Penerimaan: {keterangan}"
                    if not Jurnal.objects.filter(tanggal=tgl, uraian=uraian[:255], nominal=nilai).exists():
                        Jurnal.objects.create(
                            tanggal=tgl,
                            uraian=uraian[:255],
                            akun_debit=akun_kas,
                            akun_kredit=akun_pendapatan,
                            nominal=nilai
                        )
                        jurnal_count += 1
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error Penerimaan: {e}"))

            self.stdout.write(self.style.SUCCESS(f"Sukses Import {count} data Penerimaan + {jurnal_count} Jurnal Pendapatan."))

    # ============ UTILITIES ============
    def parse_date(self, date_str):
        if not date_str or date_str.strip() == '':
            return None
        date_str = date_str.strip()
        
        date_formats = [
            '%m/%d/%Y', '%d/%m/%Y', '%m/%d/%y', '%d/%m/%y',
            '%Y-%m-%d', '%d-%m-%Y'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except:
                continue
        return None

    def parse_int(self, val):
        if not val: 
            return 0
        try:
            return int(str(val).replace(',', '').replace('.', '').strip())
        except:
            return 0

    def parse_float(self, val):
        if not val: 
            return 0.0
        val = str(val).strip()
        if '/' in val:  # Handle "38/100" case
            return 0.0
        try:
            return float(val.replace(',', '').replace('"', ''))
        except:
            return 0.0

    def parse_rupiah(self, val):
        """Parse format Rupiah: ' Rp56,000 ' atau ' 90,000 ' -> 56000"""
        if not val:
            return 0
        val = str(val).strip()
        # Hapus Rp, spasi, koma, tanda kutip
        val = re.sub(r'[Rp\s",]', '', val)
        val = val.replace('.', '')  # Hapus titik ribuan jika ada
        try:
            return int(float(val)) if val and val != '-' else 0
        except:
            return 0
