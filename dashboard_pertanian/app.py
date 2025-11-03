# app.py

import streamlit as st
import pandas as pd
import plotly.express as px
from modules.data_loader import get_master_data
from modules.export_utils import to_excel

# === 1. KONFIGURASI HALAMAN ===
st.set_page_config(
    page_title="Dashboard Pertanian Jawa Barat",
    page_icon="bar_chart",
    layout="wide"
)

# === 2. MEMUAT DATA ===
try:
    df = get_master_data()
except Exception as e:
    st.error(f"Terjadi kesalahan saat memuat data: {e}")
    st.stop()

# === 3. SIDEBAR (FILTER) ===
st.sidebar.header("Filter Dashboard")

list_tahun = sorted(df['Tahun'].unique(), reverse=True)
list_kabupaten = sorted(df['kabupaten_kota'].unique())
list_komoditas = sorted(df['komoditas'].unique())

selected_tahun = st.sidebar.multiselect(
    "Pilih Tahun:", options=list_tahun, default=list_tahun[:1]
)
selected_kabupaten = st.sidebar.multiselect(
    "Pilih Kabupaten/Kota:", options=list_kabupaten, default=[]
)
selected_komoditas = st.sidebar.multiselect(
    "Pilih Komoditas:", options=list_komoditas, default=[]
)

# === 4. LOGIKA FILTERING DATA ===
df_filtered = df.copy()

if selected_tahun:
    df_filtered = df_filtered[df_filtered['Tahun'].isin(selected_tahun)]
else:
    df_filtered = df_filtered[df_filtered['Tahun'] == list_tahun[0]]
if selected_kabupaten:
    df_filtered = df_filtered[df_filtered['kabupaten_kota'].isin(selected_kabupaten)]
if selected_komoditas:
    df_filtered = df_filtered[df_filtered['komoditas'].isin(selected_komoditas)]

# === 5. HALAMAN UTAMA (MAIN PAGE) ===

st.title("Dashboard Monitoring Indikator Pertanian Jawa Barat")
st.markdown("Analisis data produksi, luas panen, dan produktivitas pertanian berbasis data BPS.")
st.markdown("---")

if df_filtered.empty:
    st.warning("Tidak ada data yang ditemukan untuk kombinasi filter yang Anda pilih.")
    st.stop()

# --- Indikator Kinerja Utama (KPI) ---
st.header("Ringkasan Indikator Terfilter")
total_produksi = df_filtered['produksi'].sum()
total_luas_panen = df_filtered['luas_panen'].sum()
produktivitas_rata = total_produksi / total_luas_panen if total_luas_panen > 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("Total Produksi (Ton)", f"{total_produksi:,.0f}")
col2.metric("Total Luas Panen (Ha)", f"{total_luas_panen:,.0f}")
col3.metric("Produktivitas Rata-rata (Ton/Ha)", f"{produktivitas_rata:,.2f}")

st.markdown("---")

# --- VISUALISASI DATA MENGGUNAKAN TABS ---
st.header("Analisis Visual")

# --- PENINGKATAN ESTETIKA (FASE 4.5) ---
# Kita gunakan palet warna Plotly yang estetik
# 'Plotly' adalah palet kualitatif (untuk kategori)
# 'Viridis' adalah palet sekuensial (untuk angka, ramah buta warna)
PALET_KATEGORI = px.colors.qualitative.Plotly
PALET_SEKUENSIA = px.colors.sequential.Viridis
# ----------------------------------------

tab1, tab2, tab3 = st.tabs(["Analisis Tren", "Analisis Wilayah & Komoditas", "Detail Data Mentah"])

with tab1:
    st.subheader("Tren Indikator per Tahun")
    df_tren = df_filtered.groupby('Tahun')[['produksi', 'luas_panen']].sum().reset_index()
    df_tren_melted = df_tren.melt('Tahun', var_name='Indikator', value_name='Total')
    
    fig_line = px.line(
        df_tren_melted, 
        x='Tahun', y='Total', color='Indikator',
        title="Tren Total Produksi dan Luas Panen",
        markers=True,
        labels={"Total": "Total (Ton/Ha)", "Tahun": "Tahun Kalender"},
        color_discrete_sequence=PALET_KATEGORI # <-- TAMBAHAN ESTETIKA
    )
    fig_line.update_layout(legend_title_text='Indikator')
    st.plotly_chart(fig_line, use_container_width=True)

with tab2:
    col_vis1, col_vis2 = st.columns(2)
    
    with col_vis1:
        st.subheader("Distribusi Produksi per Wilayah")
        df_bar = df_filtered.groupby('kabupaten_kota')['produksi'].sum().sort_values(ascending=False).reset_index()
        df_bar_top15 = df_bar.head(15)

        fig_bar = px.bar(
            df_bar_top15, x='produksi', y='kabupaten_kota', orientation='h',
            title=f"Top {len(df_bar_top15)} Kabupaten/Kota Produksi Tertinggi",
            text='produksi', 
            labels={"produksi": "Total Produksi (Ton)", "kabupaten_kota": "Kabupaten/Kota"},
            color='produksi', # <-- UBAH WARNA BERDASARKAN NILAI
            color_continuous_scale=PALET_SEKUENSIA # <-- TAMBAHAN ESTETIKA
        )
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
        fig_bar.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_vis2:
        st.subheader("Komposisi Produksi per Komoditas")
        df_tree = df_filtered.groupby('komoditas')['produksi'].sum().reset_index()
        
        fig_tree = px.treemap(
            df_tree,
            path=[px.Constant("Semua Komoditas"), 'komoditas'],
            values='produksi',
            title="Proporsi Produksi Berdasarkan Komoditas",
            color='komoditas', # <-- UBAH WARNA BERDASARKAN KATEGORI
            color_discrete_sequence=PALET_KATEGORI # <-- TAMBAHAN ESTETIKA
        )
        fig_tree.update_traces(root_color="lightgrey")
        st.plotly_chart(fig_tree, use_container_width=True)

with tab3:
    st.subheader("Detail Data Terfilter (Sesuai Filter)")
    
    excel_data = to_excel(df_filtered)
    nama_file = f"data_pertanian_jabar_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    st.download_button(
        label="Ekspor Data ke Excel (.xlsx)",
        data=excel_data, file_name=nama_file,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    df_display = df_filtered.copy()
    df_display['kabupaten_kota'] = df_display['kabupaten_kota'].astype(str)
    st.dataframe(df_display, use_container_width=True)