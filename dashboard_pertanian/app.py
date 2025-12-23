# app.py

import streamlit as st
import pandas as pd
import plotly.express as px
from modules.data_loader import get_master_data
from modules.export_utils import to_excel
from modules.forecasting import create_forecast

# === 1. KONFIGURASI HALAMAN ===
st.set_page_config(
    page_title="Dashboard Pertanian Jabar",
    page_icon="🌾",
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
    # Default behavior: jika tahun kosong, tetap gunakan semua atau tahun terbaru (opsional)
    # Di sini kita biarkan logika visualisasi yang menangani jika kosong
    pass 

if selected_kabupaten:
    df_filtered = df_filtered[df_filtered['kabupaten_kota'].isin(selected_kabupaten)]
if selected_komoditas:
    df_filtered = df_filtered[df_filtered['komoditas'].isin(selected_komoditas)]

# === 5. HALAMAN UTAMA (MAIN PAGE) ===

st.title("🌾 Dashboard Monitoring Pertanian Jawa Barat")
st.markdown("Analisis data produksi, luas panen, dan produktivitas pertanian berbasis data BPS.")
st.markdown("---")

# Validasi Data Kosong
if df_filtered.empty:
    st.warning("Tidak ada data yang ditemukan untuk kombinasi filter yang Anda pilih. Silakan atur ulang filter di sidebar.")
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

PALET_KATEGORI = px.colors.qualitative.Plotly
PALET_SEKUENSIA = px.colors.sequential.Plasma

tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Analisis Tren", 
    "🗺️ Analisis Wilayah & Komoditas", 
    "💾 Detail Data Mentah",
    "🔮 Analisis Ramalan (Forecast)"
])

# --- KONTEN TAB 1 (TREN) ---
# [REVISI] Logika Grafik Garis Dinamis Sesuai Permintaan Dosen
with tab1:
    st.subheader("Tren Indikator Pertanian")
    
    # KASUS 1: Jika User memilih Komoditas spesifik -> Pecah garis berdasarkan Komoditas
    if len(selected_komoditas) > 0:
        st.caption(f"Menampilkan perbandingan tren produksi untuk: {', '.join(selected_komoditas)}")
        
        # Kelompokkan berdasarkan Tahun DAN Komoditas
        df_tren = df_filtered.groupby(['Tahun', 'komoditas'])['produksi'].sum().reset_index()
        
        fig_line = px.line(
            df_tren, 
            x='Tahun', 
            y='produksi', 
            color='komoditas', # Ini kuncinya: Warna garis beda tiap komoditas
            title="Dinamika Produksi per Komoditas Terpilih", 
            markers=True,
            labels={"produksi": "Produksi (Ton)", "Tahun": "Tahun", "komoditas": "Jenis Komoditas"}
        )
        st.plotly_chart(fig_line, use_container_width=True)

    # KASUS 2: Jika User memilih Wilayah spesifik (tapi Komoditas kosong) -> Pecah garis berdasarkan Wilayah
    elif len(selected_kabupaten) > 0:
        st.caption(f"Menampilkan perbandingan tren produksi untuk wilayah terpilih.")
        
        # Kelompokkan berdasarkan Tahun DAN Wilayah
        df_tren = df_filtered.groupby(['Tahun', 'kabupaten_kota'])['produksi'].sum().reset_index()
        
        fig_line = px.line(
            df_tren, 
            x='Tahun', 
            y='produksi', 
            color='kabupaten_kota', # Warna garis beda tiap wilayah
            title="Dinamika Produksi per Wilayah Terpilih", 
            markers=True,
            labels={"produksi": "Produksi (Ton)", "Tahun": "Tahun", "kabupaten_kota": "Wilayah"}
        )
        st.plotly_chart(fig_line, use_container_width=True)

    # KASUS 3: Tidak ada filter spesifik (Global) -> Tampilkan Total Agregat (Seperti Semula)
    else:
        st.caption("Menampilkan tren total keseluruhan (Agregat) karena tidak ada filter spesifik yang dipilih.")
        
        df_tren = df_filtered.groupby('Tahun')[['produksi', 'luas_panen']].sum().reset_index()
        df_tren_melted = df_tren.melt('Tahun', var_name='Indikator', value_name='Total')
        
        fig_line = px.line(
            df_tren_melted, 
            x='Tahun', 
            y='Total', 
            color='Indikator',
            title="Tren Total Produksi dan Luas Panen (Gabungan)", 
            markers=True,
            labels={"Total": "Nilai Total", "Tahun": "Tahun", "Indikator": "Indikator"},
            color_discrete_sequence=PALET_KATEGORI
        )
        st.plotly_chart(fig_line, use_container_width=True)

# --- KONTEN TAB 2 (WILAYAH & KOMODITAS) ---
with tab2:
    col_vis1, col_vis2 = st.columns(2)
    with col_vis1:
            st.subheader("Distribusi Produksi per Wilayah")
            df_bar = df_filtered.groupby('kabupaten_kota')['produksi'].sum().sort_values(ascending=False).reset_index()
            df_bar_top15 = df_bar.head(15)
            fig_bar = px.bar(
                df_bar_top15, x='produksi', y='kabupaten_kota', orientation='h',
                title=f"Top {len(df_bar_top15)} Kabupaten/Kota Produksi Tertinggi",
                text='produksi', color='produksi', color_continuous_scale=PALET_SEKUENSIA
            )
            fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
            fig_bar.update_traces(texttemplate='%{text:.2s}', textposition='outside')
            st.plotly_chart(fig_bar, use_container_width=True)

    with col_vis2:
        st.subheader("Komposisi Produksi per Komoditas")
        df_tree = df_filtered.groupby('komoditas')['produksi'].sum().reset_index()
        fig_tree = px.treemap(
            df_tree, path=[px.Constant("Semua Komoditas"), 'komoditas'],
            values='produksi', title="Proporsi Produksi Berdasarkan Komoditas",
            color='komoditas', color_discrete_sequence=PALET_KATEGORI
        )
        st.plotly_chart(fig_tree, use_container_width=True)

# --- KONTEN TAB 3 (DATA MENTAH) ---
with tab3:
    st.subheader("Detail Data Terfilter")
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

# --- KONTEN TAB 4 (RAMALAN) ---
with tab4:
    st.subheader("Ramalan Produksi (Metode: Regresi Linier)")
    st.markdown("Pilih **satu** wilayah dan **satu** komoditas untuk memprediksi tren produksi 3 tahun ke depan.")
    
    list_kab_forecast = sorted(df['kabupaten_kota'].unique())
    list_kom_forecast = sorted(df['komoditas'].unique())

    col_fc1, col_fc2 = st.columns(2)
    with col_fc1:
        selected_kab_fc = st.selectbox("Pilih Kabupaten/Kota:", options=list_kab_forecast, index=0)
    with col_fc2:
        selected_kom_fc = st.selectbox("Pilih Komoditas:", options=list_kom_forecast, index=0)

    if st.button("Buat Ramalan Produksi"):
        data_for_model = df[
            (df['kabupaten_kota'] == selected_kab_fc) &
            (df['komoditas'] == selected_kom_fc)
        ]
        
        with st.spinner(f"Menghitung ramalan untuk {selected_kom_fc} di {selected_kab_fc}..."):
            df_hasil_forecast, pesan = create_forecast(data_for_model, years_to_predict=3)

        if df_hasil_forecast is None:
            st.error(pesan)
        else:
            st.success(pesan)
            fig_forecast = px.line(
                df_hasil_forecast, x='Tahun', y='produksi', color='Status', markers=True,
                title=f"Ramalan Produksi {selected_kom_fc} di {selected_kab_fc}",
                labels={"produksi": "Produksi (Ton)", "Tahun": "Tahun Kalender"},
                color_discrete_map={'Aktual': PALET_KATEGORI[0], 'Ramalan': PALET_KATEGORI[1]}
            )
            fig_forecast.update_traces(selector={"name": "Ramalan"}, line=dict(dash='dash'))
            st.plotly_chart(fig_forecast, use_container_width=True)
            st.dataframe(df_hasil_forecast, use_container_width=True)