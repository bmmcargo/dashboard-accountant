import numpy as np


def create_features(df):
    """
    Membuat fitur turunan dari DataFrame bulanan hasil data_extraction.

    Input:
        df: DataFrame dengan kolom dari extract_monthly_cashflow()

    Output:
        df: DataFrame yang sudah diperkaya dengan fitur tambahan

    Fitur yang dibuat:
    1. arus_kas_bersih: kas_masuk - kas_keluar (arus kas operasional bersih)
    2. rasio_piutang_hutang: total_inbound / total_manifest_hutang
    3. rasio_pendapatan_beban: total_pendapatan_jurnal / total_beban_jurnal
    4. indikator_bulan: one-hot encoding bulan 1-12 (pola musiman logistik)
    5. total_pengeluaran_operasional: beban + gaji + manifest dp
    """
    df = df.copy()

    # --------------------------------------------------
    # 1. Arus Kas Bersih (variabel utama)
    # --------------------------------------------------
    df['arus_kas_bersih'] = df['kas_masuk'] - df['kas_keluar']

    # --------------------------------------------------
    # 2. Rasio Piutang terhadap Hutang
    #    Proxy: total_inbound (piutang) / total_manifest_hutang (hutang)
    #    Menangkap keseimbangan cash flow perusahaan
    # --------------------------------------------------
    df['rasio_piutang_hutang'] = np.where(
        df['total_manifest_hutang'] > 0,
        df['total_inbound'] / df['total_manifest_hutang'],
        0.0,
    )

    # --------------------------------------------------
    # 3. Rasio Pendapatan terhadap Beban
    # --------------------------------------------------
    df['rasio_pendapatan_beban'] = np.where(
        df['total_beban_jurnal'] > 0,
        df['total_pendapatan_jurnal'] / df['total_beban_jurnal'],
        0.0,
    )

    # --------------------------------------------------
    # 4. Total Pengeluaran Operasional
    # --------------------------------------------------
    df['total_pengeluaran_ops'] = (
        df['total_beban_jurnal']
        + df['total_gaji_netto']
        + df['total_manifest_dp']
        + df['total_cashbon']
    )

    # --------------------------------------------------
    # 5. Indikator Bulan (One-Hot Encoding)
    #    Menangkap pola musiman volume pengiriman logistik
    # --------------------------------------------------
    for m in range(1, 13):
        df[f'bulan_{m}'] = (df['month'] == m).astype(int)

    return df


def create_target_label(df, target_col='arus_kas_bersih'):
    """
    Menggeser label ke bulan berikutnya (t+1) sebagai variabel target/prediksi.
    Row terakhir akan di-drop karena tidak memiliki label.

    Input:
        df: DataFrame hasil create_features()
        target_col: kolom yang akan dijadikan target

    Output:
        df: DataFrame dengan kolom 'target' (arus kas bersih bulan t+1)
    """
    df = df.copy()
    df['target'] = df[target_col].shift(-1)

    # Drop row terakhir (tidak ada target untuk bulan terakhir)
    df = df.dropna(subset=['target'])
    df['target'] = df['target'].astype(float)

    return df


def get_feature_columns():
    """
    Return daftar kolom yang digunakan sebagai fitur (X) untuk model.
    Kolom 'year', 'month', 'target' TIDAK termasuk sebagai fitur.
    """
    feature_cols = [
        # Fitur utama dari agregasi tabel
        'kas_masuk',
        'kas_keluar',
        'total_pendapatan_jurnal',
        'total_beban_jurnal',
        'total_manifest_hutang',
        'total_manifest_dp',
        'jumlah_manifest',
        'total_inbound',
        'jumlah_inbound',
        'total_gaji_bruto',
        'total_gaji_netto',
        'jumlah_slip_gaji',
        'total_cashbon',
        'jumlah_cashbon',
        # Fitur turunan
        'arus_kas_bersih',
        'rasio_piutang_hutang',
        'rasio_pendapatan_beban',
        'total_pengeluaran_ops',
        # Indikator bulan (seasonal)
        'bulan_1', 'bulan_2', 'bulan_3', 'bulan_4',
        'bulan_5', 'bulan_6', 'bulan_7', 'bulan_8',
        'bulan_9', 'bulan_10', 'bulan_11', 'bulan_12',
    ]
    return feature_cols


def handle_outliers(df, columns=None, method='clip', factor=3.0):
    """
    Deteksi dan penanganan outlier menggunakan metode IQR.
    Sesuai skripsi BAB III: "pemeriksaan nilai transaksi yang secara
    signifikan menyimpang dari pola umum"

    Args:
        df: DataFrame input
        columns: Kolom yang diperiksa (None = semua kolom numerik non-indikator)
        method: 'clip' (cap ke batas IQR) atau 'flag' (tandai saja)
        factor: IQR multiplier (default 3.0 — longgar untuk data keuangan)

    Returns:
        df: DataFrame yang sudah ditangani outlier-nya
    """
    df = df.copy()

    if columns is None:
        columns = [
            'kas_masuk', 'kas_keluar',
            'total_pendapatan_jurnal', 'total_beban_jurnal',
            'total_manifest_hutang', 'total_inbound',
            'total_gaji_bruto', 'total_cashbon',
        ]

    for col in columns:
        if col not in df.columns:
            continue

        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1

        lower = Q1 - factor * IQR
        upper = Q3 + factor * IQR

        if method == 'clip':
            df[col] = df[col].clip(lower=lower, upper=upper)

    return df
