# modules/data_loader.py

import pandas as pd
import streamlit as st

# Path file (sesuaikan jika perlu)
FILE_PADI = 'data/summary.csv'
FILE_SAYURAN = 'data/sayuran_integrated.csv'

def load_data_padi():
    """Memuat dan membersihkan data padi dari summary.csv."""
    df_padi = pd.read_csv(FILE_PADI)

    # === PERBAIKAN ===
    # Memaksa tipe data agar konsisten sebelum di-pre-processing
    df_padi['kabupaten_kota'] = df_padi['kabupaten_kota'].astype("string")
    df_padi['Tahun'] = df_padi['Tahun'].astype(int)
    # =================

    # Kolom 'luas_panen' memiliki nilai kosong (NaN), kita isi dengan 0
    df_padi['luas_panen'] = df_padi['luas_panen'].fillna(0)
    
    # Hanya pilih kolom yang relevan untuk digabung
    df_padi = df_padi[['kabupaten_kota', 'Tahun', 'produksi', 'luas_panen', 'produktivitas', 'komoditas']]
    return df_padi

def load_data_sayuran():
    """Memuat dan mentransformasi (melt) data sayuran dari wide ke long format."""
    df = pd.read_csv(FILE_SAYURAN)

    # === PERBAIKAN ===
    # Memaksa tipe data agar konsisten sebelum di-pre-processing
    df['kabupaten_kota'] = df['kabupaten_kota'].astype("string")
    df['Tahun'] = df['Tahun'].astype(int)                 # <-- TAMBAHAN BARU
    # =================
    
    # Pisahkan kolom berdasarkan ID, Produksi, dan Luas
    id_vars = ['kabupaten_kota', 'Tahun']
    
    # Dapatkan daftar kolom produksi (misal: bawang_daun, bayam, buncis, ...)
    col_stop_produksi = 'luas_bawang_daun'
    produksi_cols = df.loc[:, 'bawang_daun':col_stop_produksi].columns.drop(col_stop_produksi)
    
    # Dapatkan daftar kolom luas (misal: luas_bawang_daun, luas_bayam, ...)
    luas_cols = df.loc[:, col_stop_produksi:].columns
    
    # 1. Melt Data Produksi
    df_produksi = pd.melt(df, 
                          id_vars=id_vars, 
                          value_vars=produksi_cols, 
                          var_name='komoditas', 
                          value_name='produksi')

    # 2. Melt Data Luas Panen
    df_luas = pd.melt(df, 
                      id_vars=id_vars, 
                      value_vars=luas_cols, 
                      var_name='komoditas_luas', 
                      value_name='luas_panen')
    
    # Cleaning nama komoditas di df_luas agar cocok
    df_luas['komoditas'] = df_luas['komoditas_luas'].str.replace('luas_', '', regex=False)
    
    # 3. Gabungkan (Merge) data produksi dan luas berdasarkan ID + komoditas
    df_sayuran = pd.merge(df_produksi, 
                          df_luas[['kabupaten_kota', 'Tahun', 'komoditas', 'luas_panen']],
                          on=['kabupaten_kota', 'Tahun', 'komoditas'],
                          how='left') # Gunakan left join

    # 4. Hitung Produktivitas (Produksi / Luas Panen)
    df_sayuran['produktivitas'] = df_sayuran['produksi'].div(df_sayuran['luas_panen']).fillna(0)
    
    # Ganti nilai tak terhingga (jika ada) dengan 0
    df_sayuran.replace([float('inf'), float('-inf')], 0, inplace=True)
    
    return df_sayuran[['kabupaten_kota', 'Tahun', 'produksi', 'luas_panen', 'produktivitas', 'komoditas']]

@st.cache_data
def get_master_data():
    """Menggabungkan data Padi dan Sayuran menjadi satu Master Dataframe."""
    
    df_padi = load_data_padi()
    df_sayuran = load_data_sayuran()
    
    # Gabungkan kedua dataframe
    df_master = pd.concat([df_padi, df_sayuran], ignore_index=True)
    
    # === PERBAIKAN PENGAMAN GANDA ===
    # Kita paksa TEPAT SETELAH digabung, sebelum di-return
    # Ini untuk memastikan tipe data final benar-benar string dan integer
    df_master['kabupaten_kota'] = df_master['kabupaten_kota'].astype("string")
    df_master['Tahun'] = df_master['Tahun'].astype(int)
    # ==================================

    # Hapus baris di mana produksi dan luas panen adalah 0 (data tidak berguna)
    df_master = df_master[~((df_master['produksi'] == 0) & (df_master['luas_panen'] == 0))]

    # Membersihkan nama komoditas (misal: 'cabai_besar' -> 'Cabai Besar')
    df_master['komoditas'] = df_master['komoditas'].str.replace('_', ' ').str.title()
    
    return df_master