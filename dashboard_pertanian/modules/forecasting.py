# modules/forecasting.py

import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np

def create_forecast(df_input: pd.DataFrame, years_to_predict: int = 3) -> tuple[pd.DataFrame, str]:
    """
    Membuat ramalan time series sederhana menggunakan Regresi Linier.
    Hanya menggunakan 'Tahun' sebagai fitur (X) dan 'produksi' sebagai target (y).
    """
    
    # 1. Siapkan data, pastikan diurutkan berdasarkan Tahun
    df_model = df_input[['Tahun', 'produksi']].copy()
    df_model = df_model.sort_values(by='Tahun').dropna()

    # 2. Cek apakah data cukup untuk membuat model
    # Kita butuh setidaknya 3 titik data untuk regresi yang "masuk akal"
    if len(df_model) < 3:
        return None, "Data tidak cukup untuk membuat ramalan. Minimal dibutuhkan 3 tahun data historis."

    # 3. Siapkan data untuk pelatihan model
    X = df_model[['Tahun']] # Fitur (harus 2D array)
    y = df_model['produksi']  # Target

    # 4. Latih model Regresi Linier
    model = LinearRegression()
    model.fit(X, y)

    # 5. Siapkan tahun-tahun di masa depan untuk diprediksi
    last_year = df_model['Tahun'].max()
    future_years = np.arange(last_year + 1, last_year + 1 + years_to_predict).reshape(-1, 1)

    # 6. Buat prediksi
    predicted_production = model.predict(future_years)
    
    # 7. Best Practice: Produksi tidak bisa negatif. Setel 0 jika prediksi < 0.
    predicted_production[predicted_production < 0] = 0

    # 8. Siapkan DataFrame hasil gabungan (Historis + Ramalan)
    
    # Data historis
    df_hist = df_model.copy()
    df_hist['Status'] = 'Aktual'

    # Data ramalan
    df_forecast = pd.DataFrame({
        'Tahun': future_years.flatten(),
        'produksi': predicted_production,
        'Status': 'Ramalan'
    })
    
    # Gabungkan
    df_final = pd.concat([df_hist, df_forecast]).reset_index(drop=True)
    
    return df_final, "Ramalan berhasil dibuat menggunakan tren Regresi Linier."