# modules/export_utils.py

import pandas as pd
import io

def to_excel(df: pd.DataFrame) -> bytes:
    """
    Mengonversi DataFrame Pandas menjadi file Excel in-memory.
    
    Menggunakan io.BytesIO untuk menyimpan file di RAM alih-alih di disk,
    ini adalah 'best practice' untuk aplikasi web.
    """
    # Buat buffer I/O (file di dalam memori)
    output = io.BytesIO()
    
    # Gunakan 'with' agar writer tertutup secara otomatis
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Data Terfilter')
    
    # Ambil nilai byte dari file in-memory
    processed_data = output.getvalue()
    return processed_data