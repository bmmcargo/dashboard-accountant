import random
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from finance.models import (
    KasHarian, Manifest, InboundTransaction,
    Penggajian, Cashbon, Karyawan, Akun,
)


class Command(BaseCommand):
    help = 'Seed 24 bulan data historis untuk training model ML'

    def add_arguments(self, parser):
        parser.add_argument(
            '--months', type=int, default=24,
            help='Jumlah bulan data historis (default: 24)',
        )
        parser.add_argument(
            '--clear', action='store_true',
            help='Hapus data seed sebelumnya (data dengan keterangan mengandung [SEED])',
        )

    def handle(self, *args, **options):
        num_months = options['months']

        if options['clear']:
            self.stdout.write(self.style.WARNING('🗑️  Menghapus data seed sebelumnya...'))
            KasHarian.objects.filter(catatan__contains='[SEED]').delete()
            InboundTransaction.objects.filter(keterangan__contains='[SEED]').delete()
            Manifest.objects.filter(catatan_ops__contains='[SEED]').delete()
            Cashbon.objects.filter(keterangan__contains='[SEED]').delete()
            Penggajian.objects.filter(catatan__contains='[SEED]').delete()
            self.stdout.write(self.style.SUCCESS('   ✅ Data seed lama dihapus.'))

        random.seed(42)  # Reproducible

        # Ensure we have accounts
        self._ensure_accounts()

        # Ensure we have employees
        employees = self._ensure_employees()

        # Calculate date range (num_months back from the earliest existing data or today)
        today = timezone.now().date()
        start_date = date(today.year - (num_months // 12), today.month, 1)
        if num_months % 12 > 0:
            m = start_date.month - (num_months % 12)
            y = start_date.year
            while m <= 0:
                m += 12
                y -= 1
            start_date = date(y, m, 1)

        # Actually just go num_months back from today
        start_date = self._months_back(today, num_months)

        self.stdout.write(f'\n📅 Generating {num_months} bulan data: {start_date} → {today}')
        self.stdout.write(f'   (Data riil yang sudah ada TIDAK akan dihapus)\n')

        # Seasonal multiplier for logistics company
        # Higher volume in Q3-Q4 (Aug-Dec)
        seasonal = {
            1: 0.75, 2: 0.70, 3: 0.80, 4: 0.85,
            5: 0.90, 6: 0.95, 7: 1.00, 8: 1.15,
            9: 1.10, 10: 1.20, 11: 1.25, 12: 1.30,
        }

        stats = {
            'kas_harian': 0, 'inbound': 0, 'manifest': 0,
            'penggajian': 0, 'cashbon': 0,
        }

        current = start_date
        while current <= today:
            y, m = current.year, current.month
            mult = seasonal.get(m, 1.0)

            # Skip months that already have sufficient data
            existing_kas = KasHarian.objects.filter(
                tanggal__year=y, tanggal__month=m,
            ).count()

            if existing_kas < 5:
                count = self._seed_kas_harian(y, m, mult)
                stats['kas_harian'] += count

            existing_inbound = InboundTransaction.objects.filter(
                tanggal_masuk_stt__year=y, tanggal_masuk_stt__month=m,
            ).count()

            if existing_inbound < 5:
                count = self._seed_inbound(y, m, mult)
                stats['inbound'] += count

            existing_manifest = Manifest.objects.filter(
                tanggal_kirim__year=y, tanggal_kirim__month=m,
            ).count()

            if existing_manifest < 2:
                count = self._seed_manifest(y, m, mult)
                stats['manifest'] += count

            existing_gaji = Penggajian.objects.filter(tahun=y, bulan=m).count()
            if existing_gaji == 0:
                count = self._seed_penggajian(y, m, employees)
                stats['penggajian'] += count

            existing_cashbon = Cashbon.objects.filter(
                tanggal__year=y, tanggal__month=m,
            ).count()

            if existing_cashbon == 0 and random.random() > 0.3:
                count = self._seed_cashbon(y, m, employees)
                stats['cashbon'] += count

            # Next month
            current = self._next_month(current)

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✅ Seed data selesai!'))
        self.stdout.write(f'   Kas Harian  : {stats["kas_harian"]} entri')
        self.stdout.write(f'   Inbound     : {stats["inbound"]} transaksi')
        self.stdout.write(f'   Manifest    : {stats["manifest"]} manifest')
        self.stdout.write(f'   Penggajian  : {stats["penggajian"]} slip')
        self.stdout.write(f'   Cashbon     : {stats["cashbon"]} entri')

    def _months_back(self, dt, n):
        m = dt.month - n
        y = dt.year
        while m <= 0:
            m += 12
            y -= 1
        return date(y, m, 1)

    def _next_month(self, dt):
        if dt.month == 12:
            return date(dt.year + 1, 1, 1)
        return date(dt.year, dt.month + 1, 1)

    def _days_in_month(self, y, m):
        import calendar
        return calendar.monthrange(y, m)[1]

    def _ensure_accounts(self):
        """Pastikan akun-akun dasar ada."""
        defaults = [
            ('101', 'Kas', 'ASSET'),
            ('112', 'Piutang Usaha', 'ASSET'),
            ('113', 'Piutang Karyawan', 'ASSET'),
            ('211', 'Hutang Usaha', 'LIABILITY'),
            ('301', 'Modal', 'EQUITY'),
            ('401', 'Pendapatan Jasa', 'REVENUE'),
            ('402', 'Pendapatan Jasa Inbound', 'REVENUE'),
            ('501', 'Biaya Gaji', 'EXPENSE'),
            ('505', 'Biaya Pengiriman Vendor', 'EXPENSE'),
            ('510', 'Biaya Operasional', 'EXPENSE'),
        ]
        for kode, nama, kat in defaults:
            Akun.objects.get_or_create(kode=kode, defaults={'nama': nama, 'kategori': kat})

    def _ensure_employees(self):
        """Pastikan minimal 5 karyawan ada."""
        names = [
            ('Budi Santoso', 'Staff Gudang', 3500000),
            ('Siti Rahayu', 'Admin', 3200000),
            ('Ahmad Fadli', 'Supir', 4000000),
            ('Dewi Lestari', 'Kasir', 3000000),
            ('Rudi Hartono', 'Staff Operasional', 3500000),
            ('Andi Pratama', 'Helper', 2800000),
            ('Maya Sari', 'CS', 3100000),
            ('Eko Prasetyo', 'Supir', 4000000),
            ('Nur Hidayah', 'Admin Keuangan', 3800000),
            ('Joko Widodo', 'Kepala Gudang', 4500000),
        ]
        employees = []
        for nama, posisi, gaji in names:
            emp, _ = Karyawan.objects.get_or_create(
                nama=nama,
                defaults={
                    'posisi': posisi,
                    'gaji_pokok': Decimal(str(gaji)),
                    'status': True,
                },
            )
            employees.append(emp)
        return employees

    def _seed_kas_harian(self, year, month, multiplier):
        """Seed Kas Harian untuk satu bulan."""
        import calendar
        days = calendar.monthrange(year, month)[1]
        count = 0

        base_masuk = 150_000_000 * multiplier
        base_keluar = 30_000_000 * multiplier

        for day in range(1, days + 1):
            if random.random() > 0.85:
                continue  # Skip some days

            tgl = date(year, month, day)

            # Kas Masuk (pendapatan harian)
            if random.random() > 0.3:
                masuk = int(base_masuk / days * random.uniform(0.5, 2.0))
                KasHarian.objects.create(
                    tanggal=tgl,
                    keterangan=f'Pendapatan harian {tgl.strftime("%d/%m/%Y")} [SEED]',
                    jenis='MASUK',
                    debit=Decimal(str(masuk)),
                    kredit=Decimal('0'),
                    saldo=Decimal('0'),
                    catatan='[SEED] Data historis untuk training ML',
                )
                count += 1

            # Kas Keluar (pengeluaran harian)
            if random.random() > 0.4:
                keluar = int(base_keluar / days * random.uniform(0.3, 2.5))
                keterangan_options = [
                    'BBM kendaraan', 'Biaya makan karyawan', 'ATK',
                    'Biaya parkir', 'Biaya tol', 'Perawatan kendaraan',
                    'Biaya listrik', 'Biaya internet', 'Uang jalan',
                ]
                KasHarian.objects.create(
                    tanggal=tgl,
                    keterangan=f'{random.choice(keterangan_options)} [SEED]',
                    jenis='KELUAR',
                    debit=Decimal('0'),
                    kredit=Decimal(str(keluar)),
                    saldo=Decimal('0'),
                    catatan='[SEED] Data historis untuk training ML',
                )
                count += 1

        return count

    def _seed_inbound(self, year, month, multiplier):
        """Seed InboundTransaction untuk satu bulan."""
        import calendar
        days = calendar.monthrange(year, month)[1]
        count = 0

        num_transactions = int(random.uniform(30, 80) * multiplier)
        vendors = ['JNE', 'J&T', 'SiCepat', 'Anteraja', 'POS Indonesia', 'TIKI', 'Wahana', 'Ninja']
        tujuan_list = ['Jakarta', 'Surabaya', 'Bandung', 'Semarang', 'Medan', 'Pontianak', 'Balikpapan']

        for i in range(num_transactions):
            day = random.randint(1, days)
            tgl = date(year, month, day)

            kilo = round(random.uniform(1, 150), 2)
            tarif = random.choice([5000, 7000, 8000, 10000, 12000, 15000])
            total = int(kilo * tarif)

            try:
                InboundTransaction.objects.create(
                    tanggal_masuk_stt=tgl,
                    tanggal_stt=tgl - timedelta(days=random.randint(0, 3)),
                    vendor=random.choice(vendors),
                    no_resi=f'SEED-IB-{year}{month:02d}-{i:04d}-{random.randint(1000,9999)}',
                    tujuan=random.choice(tujuan_list),
                    koli=random.randint(1, 10),
                    kilo=Decimal(str(kilo)),
                    tarif_per_kg=str(tarif),
                    total_biaya=Decimal(str(total)),
                    keterangan='[SEED] Data historis untuk training ML',
                )
                count += 1
            except Exception:
                pass  # Skip duplicates

        return count

    def _seed_manifest(self, year, month, multiplier):
        """Seed Manifest untuk satu bulan."""
        count = 0
        num_manifests = int(random.uniform(3, 10) * multiplier)
        kategori_list = ['HULU', 'KETAPANG', 'PANTURA', 'PUTUSSIBAU', 'TRUK', 'KALTENG']

        for i in range(num_manifests):
            day = random.randint(1, self._days_in_month(year, month))
            tgl = date(year, month, day)
            total = int(random.uniform(500_000, 15_000_000) * multiplier)
            dp = int(total * random.uniform(0, 0.3))

            kategori = random.choice(kategori_list)

            try:
                Manifest.objects.create(
                    kategori=kategori,
                    tanggal_kirim=tgl,
                    no_resi=f'SEED-MF-{year}{month:02d}-{i:04d}-{random.randint(1000,9999)}',
                    pengirim=f'Pengirim Seed {i}',
                    tujuan=random.choice(['Pontianak', 'Sintang', 'Putussibau', 'Ketapang']),
                    koli=random.randint(5, 50),
                    kg=Decimal(str(round(random.uniform(50, 500), 2))),
                    penerima=f'Penerima Seed {i}',
                    dp=Decimal(str(dp)),
                    total=Decimal(str(total)),
                    catatan_ops='[SEED] Data historis untuk training ML',
                    # Fill legacy NOT NULL fields for SQLite schema mismatch
                    nomor_manifest=f'LGCY-{year}{month:02d}-{i:04d}',
                    tanggal=tgl,
                    armada='Seed Armada',
                    rute='Seed Rute',
                    status='Seed Status',
                )
                count += 1
            except Exception:
                pass

        return count

    def _seed_penggajian(self, year, month, employees):
        """Seed Penggajian untuk satu bulan."""
        count = 0
        for emp in employees:
            lembur = int(random.uniform(0, 500_000))
            bonus = int(random.uniform(0, 200_000)) if month == 12 else 0
            pot_absen = int(random.uniform(0, 150_000))
            pot_bpjs = 50_000

            try:
                Penggajian.objects.create(
                    karyawan=emp,
                    bulan=month,
                    tahun=year,
                    tanggal_gaji=date(year, month, random.randint(25, self._days_in_month(year, month))),
                    gaji_pokok=emp.gaji_pokok,
                    lembur=Decimal(str(lembur)),
                    bonus=Decimal(str(bonus)),
                    potongan_cashbon=Decimal('0'),
                    potongan_absen=Decimal(str(pot_absen)),
                    potongan_bpjs=Decimal(str(pot_bpjs)),
                    potongan_lain=Decimal('0'),
                    catatan='[SEED] Data historis untuk training ML',
                    status='PAID',
                )
                count += 1
            except Exception:
                pass

        return count

    def _seed_cashbon(self, year, month, employees):
        """Seed Cashbon untuk satu bulan."""
        count = 0
        num_cashbons = random.randint(1, 4)

        for _ in range(num_cashbons):
            emp = random.choice(employees)
            day = random.randint(1, self._days_in_month(year, month))
            nominal = int(random.uniform(100_000, 1_000_000))

            try:
                Cashbon.objects.create(
                    karyawan=emp,
                    tanggal=date(year, month, day),
                    nominal=Decimal(str(nominal)),
                    keterangan=f'Cashbon {emp.nama} [SEED]',
                )
                count += 1
            except Exception:
                pass

        return count
