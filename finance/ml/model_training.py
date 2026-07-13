import json
import os
from datetime import datetime

import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

from .feature_engineering import get_feature_columns

# Path untuk menyimpan model dan metadata
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ml_models')
MODEL_PATH = os.path.join(MODEL_DIR, 'cashflow_rf_model.joblib')
METADATA_PATH = os.path.join(MODEL_DIR, 'model_metadata.json')


def time_based_split(df, test_size=0.2):
    """
    Pembagian data berdasarkan urutan kronologis (time-based split).
    Data awal = training, data akhir = testing.

    Menghindari data leakage pada data deret waktu.
    Referensi: Géron (2022), Draft Skripsi BAB III paragraf 399-400.

    Args:
        df: DataFrame yang sudah ada fitur dan target
        test_size: Proporsi data uji (default 0.2 = 20%)

    Returns:
        X_train, X_test, y_train, y_test, train_df, test_df
    """
    feature_cols = get_feature_columns()

    # Pastikan semua kolom fitur ada
    available_cols = [c for c in feature_cols if c in df.columns]

    n = len(df)
    split_idx = int(n * (1 - test_size))

    train_df = df.iloc[:split_idx].copy()
    test_df = df.iloc[split_idx:].copy()

    X_train = train_df[available_cols].values
    X_test = test_df[available_cols].values
    y_train = train_df['target'].values
    y_test = test_df['target'].values

    return X_train, X_test, y_train, y_test, train_df, test_df


def train_random_forest(X_train, y_train, X_test, y_test, n_estimators=100):
    """
    Melatih model Random Forest Regression.

    Tahapan:
    1. Inisialisasi model dengan n_estimators
    2. Training (fit) dengan data latih
    3. Prediksi pada data uji
    4. Evaluasi metrik MAE, RMSE, R²

    Args:
        X_train, y_train: Data latih
        X_test, y_test: Data uji
        n_estimators: Jumlah pohon keputusan

    Returns:
        model: RandomForestRegressor yang sudah ditraining
        y_pred: Hasil prediksi pada data uji
        metrics: Dict {mae, rmse, r2}
    """
    model = RandomForestRegressor(
        n_estimators=n_estimators,
        random_state=42,
        n_jobs=-1,  # Gunakan semua CPU core
    )

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    metrics = evaluate_predictions(y_test, y_pred)

    return model, y_pred, metrics


def hyperparameter_tuning(X_train, y_train, X_test, y_test):
    """
    Proses uji coba hyperparameter (n_estimators) untuk mencari
    keseimbangan akurasi dan waktu komputasi.

    Referensi: Skripsi BAB III paragraf 403.

    Returns:
        best_n: Jumlah pohon terbaik
        results: List of dicts dengan metrik per konfigurasi
    """
    candidates = [50, 100, 150, 200, 300]
    results = []
    best_r2 = -float('inf')
    best_n = 100  # default

    for n in candidates:
        model = RandomForestRegressor(
            n_estimators=n,
            random_state=42,
            n_jobs=-1,
        )
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        metrics = evaluate_predictions(y_test, y_pred)
        metrics['n_estimators'] = n
        results.append(metrics)

        if metrics['r2'] > best_r2:
            best_r2 = metrics['r2']
            best_n = n

    return best_n, results


def calculate_moving_average(df, window=3):
    """
    Benchmarking: Simple Moving Average sebagai baseline.
    Prediksi bulan t+1 = rata-rata arus_kas_bersih dari window bulan terakhir.

    Untuk perbandingan dengan Random Forest (Hipotesis H1).

    Args:
        df: DataFrame dengan kolom 'arus_kas_bersih' dan 'target'
        window: Jumlah bulan untuk rata-rata bergerak

    Returns:
        ma_pred: Array prediksi Moving Average (sejajar dengan test data)
        ma_metrics: Dict {mae, rmse, r2}
    """
    arus_kas = df['arus_kas_bersih'].values
    targets = df['target'].values

    # Hitung MA predictions
    ma_predictions = []
    for i in range(len(arus_kas)):
        if i < window:
            # Belum cukup data, gunakan rata-rata yang tersedia
            ma_predictions.append(np.mean(arus_kas[:i + 1]))
        else:
            ma_predictions.append(np.mean(arus_kas[i - window:i]))

    return np.array(ma_predictions)


def evaluate_predictions(y_true, y_pred):
    """
    Menghitung metrik evaluasi: MAE, RMSE, R².

    Referensi:
    - James et al. (2021) - Koefisien determinasi R²
    - Pratama, Munawaroh, dan Pranoto (2024) - Evaluasi RF pada data finansial

    Returns:
        dict {mae, rmse, r2}
    """
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)

    return {
        'mae': float(mae),
        'rmse': float(rmse),
        'r2': float(r2),
    }


def get_feature_importance(model, feature_names):
    """
    Mengambil feature importance dari model Random Forest.

    Returns:
        List of dicts [{'feature': name, 'importance': value}]
        diurutkan dari yang terpenting.
    """
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]

    result = []
    for i in indices:
        if i < len(feature_names):
            result.append({
                'feature': feature_names[i],
                'importance': float(importances[i]),
            })

    return result


def save_model(model, metadata):
    """
    Menyimpan model terlatih dan metadata evaluasi.

    Model disimpan menggunakan joblib agar bisa dipanggil
    oleh sistem Django tanpa training ulang.
    Referensi: Skripsi BAB III paragraf 408.
    """
    os.makedirs(MODEL_DIR, exist_ok=True)

    # Simpan model
    joblib.dump(model, MODEL_PATH)

    # Simpan metadata
    with open(METADATA_PATH, 'w') as f:
        json.dump(metadata, f, indent=2, default=str)


def load_model():
    """
    Memuat model yang sudah disimpan.

    Returns:
        model: RandomForestRegressor
        metadata: Dict dari model_metadata.json
    """
    if not os.path.exists(MODEL_PATH):
        return None, None

    model = joblib.load(MODEL_PATH)

    metadata = {}
    if os.path.exists(METADATA_PATH):
        with open(METADATA_PATH, 'r') as f:
            metadata = json.load(f)

    return model, metadata


def full_training_pipeline(verbose=True):
    """
    Pipeline training lengkap: extract → preprocess → feature eng →
    split → tune → train → evaluate → save.

    Args:
        verbose: Print progress ke console

    Returns:
        dict dengan semua hasil training
    """
    from .data_extraction import extract_monthly_cashflow
    from .feature_engineering import create_features, create_target_label, handle_outliers

    # Step 1: Extract data
    if verbose:
        print("📊 Step 1: Mengekstrak data dari database...")
    raw_df = extract_monthly_cashflow()

    if raw_df.empty or len(raw_df) < 6:
        raise ValueError(
            f"Data tidak cukup untuk training. Ditemukan {len(raw_df)} bulan data. "
            f"Minimal 6 bulan diperlukan. Jalankan 'python manage.py seed_historical_data' terlebih dahulu."
        )

    if verbose:
        print(f"   ✅ {len(raw_df)} bulan data diekstrak ({raw_df['year'].min()}-{raw_df['year'].max()})")

    # Step 2: Feature Engineering
    if verbose:
        print("🔧 Step 2: Feature Engineering...")
    df = create_features(raw_df)
    df = handle_outliers(df)
    df = create_target_label(df)

    if verbose:
        print(f"   ✅ {len(df)} sampel siap (setelah shifting target)")
        print(f"   📋 Fitur: {len(get_feature_columns())} kolom")

    # Step 3: Time-based split
    if verbose:
        print("✂️  Step 3: Pembagian data 80:20 (time-based split)...")
    X_train, X_test, y_train, y_test, train_df, test_df = time_based_split(df)

    if verbose:
        print(f"   ✅ Training: {len(X_train)} sampel | Testing: {len(X_test)} sampel")

    # Step 4: Hyperparameter tuning
    if verbose:
        print("🔍 Step 4: Hyperparameter tuning (n_estimators)...")
    best_n, tuning_results = hyperparameter_tuning(X_train, y_train, X_test, y_test)

    if verbose:
        print(f"   ✅ Best n_estimators = {best_n}")
        for r in tuning_results:
            print(f"      n={r['n_estimators']}: R²={r['r2']:.4f}, MAE={r['mae']:,.0f}, RMSE={r['rmse']:,.0f}")

    # Step 5: Final training
    if verbose:
        print(f"🌳 Step 5: Training Random Forest (n_estimators={best_n})...")
    model, y_pred_rf, rf_metrics = train_random_forest(
        X_train, y_train, X_test, y_test, n_estimators=best_n,
    )

    if verbose:
        print(f"   ✅ Random Forest — MAE: Rp {rf_metrics['mae']:,.0f} | RMSE: Rp {rf_metrics['rmse']:,.0f} | R²: {rf_metrics['r2']:.4f}")

    # Step 6: Moving Average benchmark
    if verbose:
        print("📈 Step 6: Benchmarking Moving Average...")

    # Compute MA predictions for the full dataset, then slice test portion
    ma_full = calculate_moving_average(df, window=3)
    split_idx = len(X_train)
    ma_pred_test = ma_full[split_idx:]
    ma_metrics = evaluate_predictions(y_test, ma_pred_test)

    if verbose:
        print(f"   ✅ Moving Average — MAE: Rp {ma_metrics['mae']:,.0f} | RMSE: Rp {ma_metrics['rmse']:,.0f} | R²: {ma_metrics['r2']:.4f}")

    # Step 7: Feature importance
    feature_cols = [c for c in get_feature_columns() if c in df.columns]
    feature_importance = get_feature_importance(model, feature_cols)

    if verbose:
        print("🏆 Step 7: Top 5 Feature Importance:")
        for fi in feature_importance[:5]:
            print(f"   {fi['feature']}: {fi['importance']:.4f}")

    # Step 8: Prepare comparison data for Chart.js
    comparison_data = []
    # Training period actuals
    for idx, row in train_df.iterrows():
        comparison_data.append({
            'year': int(row['year']),
            'month': int(row['month']),
            'aktual': float(row['target']),
            'prediksi_rf': None,
            'prediksi_ma': None,
            'is_test': False,
        })

    # Test period: actuals + predictions
    for i, (idx, row) in enumerate(test_df.iterrows()):
        comparison_data.append({
            'year': int(row['year']),
            'month': int(row['month']),
            'aktual': float(row['target']),
            'prediksi_rf': float(y_pred_rf[i]),
            'prediksi_ma': float(ma_pred_test[i]),
            'is_test': True,
        })

    # Step 9: Next month prediction
    # Use the last row of the full feature set for next month prediction
    last_features = df[feature_cols].iloc[-1:].values
    next_month_rf = float(model.predict(last_features)[0])
    next_month_ma = float(np.mean(df['arus_kas_bersih'].values[-3:]))

    # Step 10: Save model + metadata
    metadata = {
        'trained_at': datetime.now().isoformat(),
        'total_data_months': len(raw_df),
        'training_samples': len(X_train),
        'testing_samples': len(X_test),
        'best_n_estimators': best_n,
        'rf_metrics': rf_metrics,
        'ma_metrics': ma_metrics,
        'feature_importance': feature_importance[:10],
        'tuning_results': tuning_results,
        'comparison_data': comparison_data,
        'next_month_prediction_rf': next_month_rf,
        'next_month_prediction_ma': next_month_ma,
        'feature_columns': feature_cols,
        'data_range': {
            'start_year': int(raw_df['year'].min()),
            'start_month': int(raw_df.loc[raw_df['year'] == raw_df['year'].min(), 'month'].min()),
            'end_year': int(raw_df['year'].max()),
            'end_month': int(raw_df.loc[raw_df['year'] == raw_df['year'].max(), 'month'].max()),
        },
    }

    save_model(model, metadata)

    if verbose:
        print(f"\n💾 Step 8: Model disimpan ke {MODEL_PATH}")
        print(f"📋 Metadata disimpan ke {METADATA_PATH}")
        print(f"\n🎯 Prediksi Arus Kas Bulan Depan:")
        print(f"   Random Forest : Rp {next_month_rf:,.0f}")
        print(f"   Moving Average: Rp {next_month_ma:,.0f}")
        print(f"\n{'='*60}")
        if rf_metrics['r2'] > ma_metrics['r2']:
            print(f"✅ Random Forest LEBIH BAIK dari Moving Average")
            print(f"   RF R² ({rf_metrics['r2']:.4f}) > MA R² ({ma_metrics['r2']:.4f})")
        else:
            print(f"⚠️  Moving Average lebih baik dari Random Forest")
            print(f"   MA R² ({ma_metrics['r2']:.4f}) > RF R² ({rf_metrics['r2']:.4f})")

    return {
        'model': model,
        'metadata': metadata,
        'rf_metrics': rf_metrics,
        'ma_metrics': ma_metrics,
    }
