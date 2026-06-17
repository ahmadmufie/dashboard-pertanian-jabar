# ✨ Dashboard Monitoring Indikator Pertanian

> Dashboard interaktif yang bertujuan untuk membantu dinas dalam mitigasi resiko dan pengambilan keputusan.

## Tautan Dashboard:
https://dashboard-pertanian-jabar.streamlit.app/.

1.	Keberhasilan Integrasi Data (Data Integration): Penulis berhasil mengintegrasikan data mentah (raw data) yang bersumber dari BPS periode 2019–2024. Tantangan perbedaan format data antara komoditas padi (terstruktur) dan hortikultura (wide format) berhasil diatasi melalui proses ETL (Extract, Transform, Load) menggunakan algoritma pemrograman Python. Hasilnya adalah satu basis data terpadu yang bersih dan siap dianalisis.
2.	Fungsionalitas Dashboard Interaktif: Telah terbangun sebuah dashboard berbasis web yang mampu memvisualisasikan indikator kinerja utama pertanian (Produksi, Luas Panen, dan Produktivitas) secara real-time. Fitur filter bertingkat (Tahun, Wilayah, Komoditas) terbukti berfungsi dengan baik dalam membantu pengguna melakukan eksplorasi data secara spesifik (granular).
3.	Analisis Prediktif (Forecasting): Sistem telah dilengkapi dengan modul peramalan menggunakan metode Regresi Linier Sederhana. Fitur ini mampu memberikan proyeksi tren produksi untuk 3 tahun ke depan (2025–2027) berdasarkan data historis. Meskipun menggunakan data deret waktu yang pendek (short time-series), model ini cukup memadai untuk memberikan gambaran estimasi tren (trend estimation) awal bagi pemangku kepentingan.
4.	Aksesibilitas Sistem: Aplikasi telah berhasil di-deploy ke layanan cloud hosting dan dapat diakses secara publik melalui jaringan internet. Hal ini meningkatkan aksesibilitas data, memungkinkan staf Dinas maupun pihak terkait untuk memantau data pertanian kapan saja dan di mana saja tanpa terbatas pada perangkat lokal kantor.
