import pandas as pd
from datetime import date

from django.db.models import Sum, F, Value, DecimalField, Min as django_min, Max as django_max
from django.db.models.functions import Coalesce, ExtractMonth, ExtractYear


def extract_monthly_cashflow():
    """
    Mengekstrak dan mengagregasi data dari 6 tabel transaksi menjadi
    satu DataFrame bulanan yang konsisten.

    Returns:
        pd.DataFrame dengan kolom:
        - year, month (kunci waktu)
        - kas_masuk, kas_keluar (dari KasHarian)
        - total_pendapatan_jurnal, total_beban_jurnal (dari Jurnal)
        - total_manifest_hutang, jumlah_manifest, total_manifest_dp (dari Manifest)
        - total_inbound, jumlah_inbound (dari InboundTransaction)
        - total_gaji_bruto, total_gaji_netto, jumlah_slip_gaji (dari Penggajian)
        - total_cashbon, jumlah_cashbon (dari Cashbon)
    """
    from finance.models import (
        KasHarian, Jurnal, Manifest, InboundTransaction,
        Penggajian, Cashbon, Akun,
    )

    # -------------------------------------------------------
    # 1. Determine date range from all tables
    # -------------------------------------------------------
    all_dates = []

    kas_range = KasHarian.objects.aggregate(
        mn=Coalesce(
            django_min('tanggal'),
            Value(date.today()),
        ),
        mx=Coalesce(
            django_max('tanggal'),
            Value(date.today()),
        ),
    )
    all_dates.extend([kas_range['mn'], kas_range['mx']])

    jurnal_range = Jurnal.objects.aggregate(
        mn=Coalesce(
            django_min('tanggal'),
            Value(date.today()),
        ),
        mx=Coalesce(
            django_max('tanggal'),
            Value(date.today()),
        ),
    )
    all_dates.extend([jurnal_range['mn'], jurnal_range['mx']])

    manifest_range = Manifest.objects.aggregate(
        mn=Coalesce(
            django_min('tanggal_kirim'),
            Value(date.today()),
        ),
        mx=Coalesce(
            django_max('tanggal_kirim'),
            Value(date.today()),
        ),
    )
    all_dates.extend([manifest_range['mn'], manifest_range['mx']])

    inbound_range = InboundTransaction.objects.aggregate(
        mn=Coalesce(
            django_min('tanggal_masuk_stt'),
            Value(date.today()),
        ),
        mx=Coalesce(
            django_max('tanggal_masuk_stt'),
            Value(date.today()),
        ),
    )
    all_dates.extend([inbound_range['mn'], inbound_range['mx']])

    # Filter None values
    all_dates = [d for d in all_dates if d is not None]

    if not all_dates:
        return pd.DataFrame()

    min_date = min(all_dates)
    max_date = max(all_dates)

    # Build full month range
    months = []
    current = date(min_date.year, min_date.month, 1)
    end = date(max_date.year, max_date.month, 1)
    while current <= end:
        months.append({'year': current.year, 'month': current.month})
        # Next month
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)

    df = pd.DataFrame(months)

    # -------------------------------------------------------
    # 2. Kas Harian aggregation
    # -------------------------------------------------------
    kas_qs = (
        KasHarian.objects
        .values(y=ExtractYear('tanggal'), m=ExtractMonth('tanggal'))
        .annotate(
            kas_masuk=Coalesce(Sum('debit'), Value(0, output_field=DecimalField())),
            kas_keluar=Coalesce(Sum('kredit'), Value(0, output_field=DecimalField())),
        )
    )
    kas_df = pd.DataFrame(list(kas_qs))
    if not kas_df.empty:
        kas_df = kas_df.rename(columns={'y': 'year', 'm': 'month'})
        kas_df['kas_masuk'] = kas_df['kas_masuk'].astype(float)
        kas_df['kas_keluar'] = kas_df['kas_keluar'].astype(float)
        df = df.merge(kas_df[['year', 'month', 'kas_masuk', 'kas_keluar']],
                      on=['year', 'month'], how='left')
    else:
        df['kas_masuk'] = 0.0
        df['kas_keluar'] = 0.0

    # -------------------------------------------------------
    # 3. Jurnal aggregation (pendapatan & beban berdasarkan kategori Akun)
    # -------------------------------------------------------
    akun_revenue_ids = list(Akun.objects.filter(kategori='REVENUE').values_list('id', flat=True))
    akun_expense_ids = list(Akun.objects.filter(kategori='EXPENSE').values_list('id', flat=True))

    # Pendapatan = kredit ke akun REVENUE
    rev_qs = (
        Jurnal.objects
        .filter(akun_kredit_id__in=akun_revenue_ids)
        .values(y=ExtractYear('tanggal'), m=ExtractMonth('tanggal'))
        .annotate(
            total_pendapatan_jurnal=Coalesce(Sum('nominal'), Value(0, output_field=DecimalField()))
        )
    )
    rev_df = pd.DataFrame(list(rev_qs))
    if not rev_df.empty:
        rev_df = rev_df.rename(columns={'y': 'year', 'm': 'month'})
        rev_df['total_pendapatan_jurnal'] = rev_df['total_pendapatan_jurnal'].astype(float)
        df = df.merge(rev_df[['year', 'month', 'total_pendapatan_jurnal']],
                      on=['year', 'month'], how='left')
    else:
        df['total_pendapatan_jurnal'] = 0.0

    # Beban = debit ke akun EXPENSE
    exp_qs = (
        Jurnal.objects
        .filter(akun_debit_id__in=akun_expense_ids)
        .values(y=ExtractYear('tanggal'), m=ExtractMonth('tanggal'))
        .annotate(
            total_beban_jurnal=Coalesce(Sum('nominal'), Value(0, output_field=DecimalField()))
        )
    )
    exp_df = pd.DataFrame(list(exp_qs))
    if not exp_df.empty:
        exp_df = exp_df.rename(columns={'y': 'year', 'm': 'month'})
        exp_df['total_beban_jurnal'] = exp_df['total_beban_jurnal'].astype(float)
        df = df.merge(exp_df[['year', 'month', 'total_beban_jurnal']],
                      on=['year', 'month'], how='left')
    else:
        df['total_beban_jurnal'] = 0.0

    # -------------------------------------------------------
    # 4. Manifest aggregation
    # -------------------------------------------------------
    manifest_qs = (
        Manifest.objects
        .filter(tanggal_kirim__isnull=False)
        .values(y=ExtractYear('tanggal_kirim'), m=ExtractMonth('tanggal_kirim'))
        .annotate(
            total_manifest_hutang=Coalesce(Sum('total'), Value(0, output_field=DecimalField())),
            total_manifest_dp=Coalesce(Sum('dp'), Value(0, output_field=DecimalField())),
            jumlah_manifest=Coalesce(Sum(Value(1)), Value(0)),
        )
    )
    manifest_df = pd.DataFrame(list(manifest_qs))
    if not manifest_df.empty:
        manifest_df = manifest_df.rename(columns={'y': 'year', 'm': 'month'})
        for col in ['total_manifest_hutang', 'total_manifest_dp']:
            manifest_df[col] = manifest_df[col].astype(float)
        manifest_df['jumlah_manifest'] = manifest_df['jumlah_manifest'].astype(int)
        df = df.merge(
            manifest_df[['year', 'month', 'total_manifest_hutang', 'total_manifest_dp', 'jumlah_manifest']],
            on=['year', 'month'], how='left',
        )
    else:
        df['total_manifest_hutang'] = 0.0
        df['total_manifest_dp'] = 0.0
        df['jumlah_manifest'] = 0

    # -------------------------------------------------------
    # 5. Inbound aggregation
    # -------------------------------------------------------
    inbound_qs = (
        InboundTransaction.objects
        .filter(tanggal_masuk_stt__isnull=False)
        .values(y=ExtractYear('tanggal_masuk_stt'), m=ExtractMonth('tanggal_masuk_stt'))
        .annotate(
            total_inbound=Coalesce(Sum('total_biaya'), Value(0, output_field=DecimalField())),
            jumlah_inbound=Coalesce(Sum(Value(1)), Value(0)),
        )
    )
    inbound_df = pd.DataFrame(list(inbound_qs))
    if not inbound_df.empty:
        inbound_df = inbound_df.rename(columns={'y': 'year', 'm': 'month'})
        inbound_df['total_inbound'] = inbound_df['total_inbound'].astype(float)
        inbound_df['jumlah_inbound'] = inbound_df['jumlah_inbound'].astype(int)
        df = df.merge(
            inbound_df[['year', 'month', 'total_inbound', 'jumlah_inbound']],
            on=['year', 'month'], how='left',
        )
    else:
        df['total_inbound'] = 0.0
        df['jumlah_inbound'] = 0

    # -------------------------------------------------------
    # 6. Penggajian aggregation
    # -------------------------------------------------------
    gaji_qs = (
        Penggajian.objects
        .values(y=F('tahun'), m=F('bulan'))
        .annotate(
            total_gaji_bruto=Coalesce(
                Sum(F('gaji_pokok') + F('lembur') + F('bonus')),
                Value(0, output_field=DecimalField()),
            ),
            total_gaji_netto=Coalesce(Sum('total_diterima'), Value(0, output_field=DecimalField())),
            jumlah_slip_gaji=Coalesce(Sum(Value(1)), Value(0)),
        )
    )
    gaji_df = pd.DataFrame(list(gaji_qs))
    if not gaji_df.empty:
        gaji_df = gaji_df.rename(columns={'y': 'year', 'm': 'month'})
        for col in ['total_gaji_bruto', 'total_gaji_netto']:
            gaji_df[col] = gaji_df[col].astype(float)
        gaji_df['jumlah_slip_gaji'] = gaji_df['jumlah_slip_gaji'].astype(int)
        df = df.merge(
            gaji_df[['year', 'month', 'total_gaji_bruto', 'total_gaji_netto', 'jumlah_slip_gaji']],
            on=['year', 'month'], how='left',
        )
    else:
        df['total_gaji_bruto'] = 0.0
        df['total_gaji_netto'] = 0.0
        df['jumlah_slip_gaji'] = 0

    # -------------------------------------------------------
    # 7. Cashbon aggregation
    # -------------------------------------------------------
    cashbon_qs = (
        Cashbon.objects
        .values(y=ExtractYear('tanggal'), m=ExtractMonth('tanggal'))
        .annotate(
            total_cashbon=Coalesce(Sum('nominal'), Value(0, output_field=DecimalField())),
            jumlah_cashbon=Coalesce(Sum(Value(1)), Value(0)),
        )
    )
    cashbon_df = pd.DataFrame(list(cashbon_qs))
    if not cashbon_df.empty:
        cashbon_df = cashbon_df.rename(columns={'y': 'year', 'm': 'month'})
        cashbon_df['total_cashbon'] = cashbon_df['total_cashbon'].astype(float)
        cashbon_df['jumlah_cashbon'] = cashbon_df['jumlah_cashbon'].astype(int)
        df = df.merge(
            cashbon_df[['year', 'month', 'total_cashbon', 'jumlah_cashbon']],
            on=['year', 'month'], how='left',
        )
    else:
        df['total_cashbon'] = 0.0
        df['jumlah_cashbon'] = 0

    # -------------------------------------------------------
    # 8. Fill NaN and sort
    # -------------------------------------------------------
    df = df.fillna(0)
    df = df.sort_values(['year', 'month']).reset_index(drop=True)

    return df

