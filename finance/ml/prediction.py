import os

from .model_training import MODEL_PATH, METADATA_PATH, load_model


def is_model_trained():
    """Cek apakah model sudah pernah ditraining."""
    return os.path.exists(MODEL_PATH) and os.path.exists(METADATA_PATH)


def get_prediction_data():
    """
    Mengambil semua data yang diperlukan oleh halaman dashboard prediksi.

    Returns:
        dict:
        - model_trained (bool)
        - next_month_rf (float): Prediksi RF bulan depan
        - next_month_ma (float): Prediksi MA bulan depan
        - rf_metrics (dict): {mae, rmse, r2}
        - ma_metrics (dict): {mae, rmse, r2}
        - comparison_data (list): Data untuk Chart.js
        - feature_importance (list): Top fitur
        - model_info (dict): Info training
    """
    if not is_model_trained():
        return {
            'model_trained': False,
            'message': 'Model belum ditraining. Jalankan: python manage.py train_cashflow_model',
        }

    _, metadata = load_model()

    if not metadata:
        return {
            'model_trained': False,
            'message': 'Metadata model tidak ditemukan.',
        }

    return {
        'model_trained': True,
        'next_month_rf': metadata.get('next_month_prediction_rf', 0),
        'next_month_ma': metadata.get('next_month_prediction_ma', 0),
        'rf_metrics': metadata.get('rf_metrics', {}),
        'ma_metrics': metadata.get('ma_metrics', {}),
        'comparison_data': metadata.get('comparison_data', []),
        'feature_importance': metadata.get('feature_importance', []),
        'model_info': {
            'trained_at': metadata.get('trained_at', ''),
            'total_data_months': metadata.get('total_data_months', 0),
            'training_samples': metadata.get('training_samples', 0),
            'testing_samples': metadata.get('testing_samples', 0),
            'best_n_estimators': metadata.get('best_n_estimators', 0),
            'data_range': metadata.get('data_range', {}),
            'tuning_results': metadata.get('tuning_results', []),
        },
    }


def predict_next_month():
    """
    Melakukan prediksi arus kas bulan depan menggunakan data terbaru.

    Berbeda dengan get_prediction_data() yang membaca hasil cache,
    fungsi ini melakukan prediksi ulang menggunakan data real-time.

    Returns:
        dict: {rf_prediction, ma_prediction}
    """
    import numpy as np
    from .data_extraction import extract_monthly_cashflow
    from .feature_engineering import create_features, get_feature_columns

    model, metadata = load_model()
    if model is None:
        return None

    # Ambil data terbaru
    raw_df = extract_monthly_cashflow()
    if raw_df.empty:
        return None

    df = create_features(raw_df)

    feature_cols = metadata.get('feature_columns', get_feature_columns())
    available_cols = [c for c in feature_cols if c in df.columns]

    # Prediksi menggunakan data bulan terakhir
    last_row = df[available_cols].iloc[-1:].values
    rf_prediction = float(model.predict(last_row)[0])

    # Moving Average (3 bulan terakhir)
    ma_prediction = float(np.mean(df['arus_kas_bersih'].values[-3:]))

    return {
        'rf_prediction': rf_prediction,
        'ma_prediction': ma_prediction,
    }
