import sqlite3
from io import BytesIO

import pandas as pd
import plotly.express as px
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table

st.set_page_config(page_title="Dashboard Restoran", page_icon="R", layout="wide")

st.markdown("""
<style>
:root { color-scheme: light; }
.stApp {
    background: linear-gradient(135deg, #fff8e7 0%, #f7e7bd 52%, #fffaf0 100%);
    color: #342316 !important;
}
html, body, [class*="css"], .stMarkdown, .stText,
p, label, small, li, span, div {
    color: #342316;
}
h1, h2, h3, h4, h5, h6 {
    color: #3b2416 !important;
    font-weight: 750 !important;
}
.stCaption, [data-testid="stCaptionContainer"] {
    color: #6b5848 !important;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #5b3825 0%, #7a5033 100%);
}
[data-testid="stSidebar"] * { color: #fff8e7 !important; }
.block-container { padding-top: 1.8rem; }
/* Kartu statistik */
[data-testid="stMetric"] {
    background: #fffdf7;
    border: 1px solid #d6b77a;
    padding: 16px;
    border-radius: 14px;
    box-shadow: 0 4px 14px rgba(74, 48, 27, .10);
}
[data-testid="stMetric"] label,
[data-testid="stMetricLabel"] p { color: #6b5848 !important; }
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] div { color: #3b2416 !important; }
/* Kolom input */
input, textarea,
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea,
[data-baseweb="select"] > div {
    background-color: #fffdf8 !important;
    color: #342316 !important;
    -webkit-text-fill-color: #342316 !important;
    border-color: #a98761 !important;
}
input::placeholder, textarea::placeholder {
    color: #786858 !important;
    -webkit-text-fill-color: #786858 !important;
    opacity: 1 !important;
}
[data-testid="stTextInput"] label,
[data-testid="stSelectbox"] label,
[data-testid="stNumberInput"] label,
[data-testid="stFileUploader"] label,
[data-testid="stCheckbox"] label,
[data-testid="stRadio"] label {
    color: #49301f !important;
    font-weight: 650 !important;
}
/* Form */
[data-testid="stForm"] {
    background: rgba(255,253,247,.94);
    border: 1px solid #c9a875;
    border-radius: 16px;
    padding: 22px;
}
/* Tombol */
div.stButton > button,
div.stDownloadButton > button,
div.stFormSubmitButton > button {
    background: #a85d27 !important;
    color: #ffffff !important;
    border: 1px solid #8b451f !important;
    border-radius: 9px;
    font-weight: 650;
}
div.stButton > button *,
div.stDownloadButton > button *,
div.stFormSubmitButton > button * { color: #ffffff !important; }
div.stButton > button:hover,
div.stDownloadButton > button:hover,
div.stFormSubmitButton > button:hover {
    background: #82451f !important;
    color: #ffffff !important;
}
/* Kotak info: cokelat tua dengan teks krem agar kontras */
[data-testid="stAlert"],
[data-testid="stAlert"] [data-testid="stMarkdownContainer"] {
    background: #6b452d !important;
    border-color: #8a6242 !important;
    border-radius: 12px !important;
}
[data-testid="stAlert"] *,
[data-testid="stAlert"] p,
[data-testid="stAlert"] span,
[data-testid="stAlert"] div {
    color: #fff8e7 !important;
    -webkit-text-fill-color: #fff8e7 !important;
}
/* Expander */
[data-testid="stExpander"] {
    background: #fffdf7 !important;
    border: 1px solid #c9a875 !important;
    border-radius: 12px;
}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary * {
    background: #6b452d !important;
    color: #fff8e7 !important;
    -webkit-text-fill-color: #fff8e7 !important;
}
[data-testid="stDataFrame"] { background: #fffdf7; }
[data-testid="stTable"] { color: #342316 !important; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# IKON SVG INLINE — SEMUA ADA DI FILE app.py
# =========================================================
SVG_ICONS = {
    "restaurant": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="30" height="30"
    fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
      <path d="M4 2v7a3 3 0 0 0 6 0V2"/><path d="M7 2v20"/>
      <path d="M16 2v8a3 3 0 0 0 6 0V2"/><path d="M19 13v9"/>
    </svg>
    """,
    "lock": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="28" height="28"
    fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
      <rect x="4" y="10" width="16" height="12" rx="2"/><path d="M8 10V7a4 4 0 1 1 8 0v3"/>
    </svg>
    """,
    "logout": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20"
    fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
      <path d="M10 17l5-5-5-5M15 12H3"/><path d="M12 3h7a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-7"/>
    </svg>
    """,
    "chart": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"
    fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
      <path d="M3 3v18h18"/><rect x="6" y="12" width="3" height="6"/>
      <rect x="11" y="8" width="3" height="10"/><rect x="16" y="4" width="3" height="14"/>
    </svg>
    """,
    "database": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"
    fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
      <ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 1.7 4 3 9 3s9-1.3 9-3V5"/>
      <path d="M3 12c0 1.7 4 3 9 3s9-1.3 9-3"/>
    </svg>
    """,
    "plus": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20"
    fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
      <path d="M12 5v14M5 12h14"/>
    </svg>
    """,
    "trash": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20"
    fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
      <path d="M3 6h18M8 6V4h8v2m-9 0 1 15h8l1-15M10 10v7m4-7v7"/>
    </svg>
    """,
    "document": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20"
    fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
      <path d="M6 2h8l5 5v15H6z"/><path d="M14 2v6h5M9 13h7M9 17h7"/>
    </svg>
    """,
    "download": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20"
    fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
      <path d="M12 3v12m-5-5 5 5 5-5M4 17v4h16v-4"/>
    </svg>
    """,
}

def tampilkan_ikon(nama):
    """Tampilkan ikon SVG langsung dari string di dalam app.py."""
    svg = SVG_ICONS[nama]
    st.markdown(
        f'<span style="display:inline-flex;align-items:center;vertical-align:middle;'
        f'color:var(--text-color)">{svg}</span>',
        unsafe_allow_html=True,
    )

# =========================================================
# LOGIN DEMO — untuk demonstrasi tugas sekolah
# =========================================================
if "sudah_login" not in st.session_state:
    st.session_state.sudah_login = False

if not st.session_state.sudah_login:
    tampilkan_ikon("lock")
    st.title("Login Dashboard Restoran")
    st.write("Silakan masuk untuk mengakses aplikasi.")
    with st.form("form_login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        masuk = st.form_submit_button("Login")
    if masuk:
        if username == "admin" and password == "restoran123":
            st.session_state.sudah_login = True
            st.rerun()
        else:
            st.error("Username atau password salah.")
    st.stop()

# =========================================================
# DATABASE SQLITE
# =========================================================
@st.cache_resource
def get_connection():
    return sqlite3.connect("restoran.db", check_same_thread=False)

conn = get_connection()
conn.execute("""
CREATE TABLE IF NOT EXISTS transaksi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    menu TEXT NOT NULL,
    kategori TEXT NOT NULL,
    jumlah INTEGER NOT NULL,
    harga INTEGER NOT NULL,
    shift TEXT NOT NULL,
    jenis_pesanan TEXT NOT NULL,
    meja INTEGER NOT NULL
)
""")
conn.commit()

def ambil_data():
    return pd.read_sql_query("SELECT * FROM transaksi ORDER BY id DESC", conn)

def hitung_pendapatan(data):
    data = data.copy()
    if data.empty:
        data["Total_Pendapatan"] = pd.Series(dtype="int64")
    else:
        data["Total_Pendapatan"] = data["jumlah"] * data["harga"]
    return data

# Tidak ada data dummy. Database dimulai kosong.
# Data hanya berasal dari transaksi yang dimasukkan pengguna atau file CSV.

# =========================================================
# NAVIGASI
# =========================================================
tampilkan_ikon("restaurant")
st.sidebar.title("Menu")
halaman = st.sidebar.radio(
    "Pilih Halaman",
    ["Home", "Dashboard Analytics", "Data Management"],
)
if st.sidebar.button("Logout"):
    st.session_state.sudah_login = False
    st.rerun()

st.title("Dashboard Penjualan Restoran/Kafe")

# =========================================================
# HOME
# =========================================================
if halaman == "Home":
    st.header("Selamat Datang!")
    st.image("https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=1600&q=85", caption="Restaurant & Cafe Dashboard", use_container_width=True)
    st.write("""
    Aplikasi ini digunakan untuk memantau penjualan restoran atau kafe.

    Fitur:
    - Statistik dan grafik penjualan
    - Pengelolaan transaksi
    - Import CSV
    - Export CSV dan Excel
    - Laporan PDF
    """)
    st.info("Pilih menu di sebelah kiri untuk mulai menggunakan aplikasi.")
    data_home = hitung_pendapatan(ambil_data())
    if not data_home.empty:
        a, b, c = st.columns(3)
        a.metric("Total Pendapatan", f"Rp{data_home['Total_Pendapatan'].sum():,.0f}")
        b.metric("Total Menu Terjual", f"{data_home['jumlah'].sum():,}")
        c.metric("Jumlah Transaksi", f"{len(data_home):,}")

# =========================================================
# DASHBOARD ANALYTICS
# =========================================================
elif halaman == "Dashboard Analytics":
    tampilkan_ikon("chart")
    st.header("Dashboard Analytics")
    data = hitung_pendapatan(ambil_data())
    if data.empty:
        st.warning("Belum ada data transaksi.")
    else:
        semua_jenis = sorted(data["jenis_pesanan"].dropna().unique().tolist())
        semua_shift = sorted(data["shift"].dropna().unique().tolist())
        jenis = st.sidebar.multiselect("Filter Jenis Pesanan", semua_jenis, default=semua_jenis)
        shift = st.sidebar.multiselect("Filter Shift", semua_shift, default=semua_shift)
        tampil = data[data["jenis_pesanan"].isin(jenis) & data["shift"].isin(shift)]
        pendapatan = int(tampil["Total_Pendapatan"].sum())
        total_menu = int(tampil["jumlah"].sum())
        meja_terisi = int(tampil.loc[tampil["jenis_pesanan"] == "Dine-in", "meja"].nunique())
        a, b, c = st.columns(3)
        a.metric("Total Pendapatan", f"Rp{pendapatan:,.0f}")
        b.metric("Menu Terjual", f"{total_menu:,}")
        c.metric("Meja Terisi", f"{meja_terisi:,}")

        if tampil.empty:
            st.warning("Tidak ada transaksi yang sesuai dengan filter.")
        else:
            favorit = tampil.groupby("menu", as_index=False)["jumlah"].sum().sort_values("jumlah", ascending=False)
            st.subheader("Menu Paling Favorit")
            st.plotly_chart(
                px.bar(favorit, x="menu", y="jumlah", title="Jumlah Menu Terjual", color="menu", color_discrete_sequence=px.colors.qualitative.Set2),
                use_container_width=True,
            )
            urutan_shift = ["Pagi", "Siang", "Malam"]
            omzet = tampil.groupby("shift", as_index=False).agg(
                Total_Pendapatan=("Total_Pendapatan", "sum"),
                Jumlah_Transaksi=("id", "count"),
                Menu_Terjual=("jumlah", "sum"),
            )
            omzet["shift"] = pd.Categorical(omzet["shift"], categories=urutan_shift, ordered=True)
            omzet = omzet.sort_values("shift")
            st.subheader("Analisis Penjualan Berdasarkan Shift")
            st.plotly_chart(
                px.bar(omzet, x="shift", y="Total_Pendapatan", color="shift",
                       title="Total Pendapatan per Shift",
                       labels={"shift": "Shift", "Total_Pendapatan": "Pendapatan (Rp)"},
                       color_discrete_sequence=["#f97316", "#0ea5e9", "#8b5cf6"]),
                use_container_width=True,
            )
            st.plotly_chart(
                px.bar(omzet, x="shift", y="Jumlah_Transaksi", color="shift",
                       title="Jumlah Transaksi per Shift",
                       labels={"shift": "Shift", "Jumlah_Transaksi": "Jumlah Transaksi"},
                       color_discrete_sequence=["#f97316", "#0ea5e9", "#8b5cf6"]),
                use_container_width=True,
            )
            kategori_data = tampil.groupby("kategori", as_index=False)["jumlah"].sum()
            st.subheader("Penjualan Makanan vs Minuman")
            st.plotly_chart(
                px.pie(kategori_data, names="kategori", values="jumlah", title="Proporsi Penjualan per Kategori", color_discrete_sequence=["#f97316", "#0ea5e9"]),
                use_container_width=True,
            )
            st.subheader("Data Transaksi")
            st.caption("Setiap transaksi memiliki ID sendiri. Menu yang sama diringkas pada grafik, sedangkan riwayat transaksi tetap tersimpan terpisah.")
            st.dataframe(tampil, use_container_width=True, hide_index=True)

# =========================================================
# DATA MANAGEMENT
# =========================================================
elif halaman == "Data Management":
    tampilkan_ikon("database")
    st.header("Data Management")
    st.write("Masukkan transaksi penjualan yang benar-benar terjadi, atau impor catatan penjualan dari kasir.")
    st.info("Database dimulai kosong. Grafik dan laporan baru terisi setelah transaksi nyata dimasukkan.")

    with st.expander("Tambah Transaksi", expanded=True):
        with st.form("form_transaksi", clear_on_submit=True):
            menu = st.text_input("Nama Menu")
            kategori = st.selectbox("Kategori", ["Makanan", "Minuman"])
            jumlah = st.number_input("Jumlah Terjual", min_value=1, value=1, step=1)
            harga = st.number_input("Harga per Menu (Rp)", min_value=0, value=10000, step=1000)
            shift = st.selectbox("Shift", ["Pagi", "Siang", "Malam"])
            jenis = st.selectbox("Jenis Pesanan", ["Dine-in", "Takeaway"])
            meja = st.number_input("Nomor Meja", min_value=1, value=1, step=1)
            simpan = st.form_submit_button("Simpan Transaksi")

    if simpan:
        if not menu.strip():
            st.error("Nama menu tidak boleh kosong.")
        else:
            conn.execute("""
                INSERT INTO transaksi
                (menu, kategori, jumlah, harga, shift, jenis_pesanan, meja)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (menu.strip(), kategori, int(jumlah), int(harga), shift, jenis, int(meja)))
            conn.commit()
            st.success("Transaksi berhasil disimpan!")
            st.rerun()

    st.divider()
    st.subheader("Import Data CSV")
    st.caption("Kolom CSV wajib: menu, kategori, jumlah, harga, shift, jenis_pesanan, meja.")
    file_csv = st.file_uploader("Pilih file CSV", type=["csv"])
    if file_csv is not None:
        try:
            csv_data = pd.read_csv(file_csv)
            kolom_wajib = ["menu", "kategori", "jumlah", "harga", "shift", "jenis_pesanan", "meja"]
            if all(k in csv_data.columns for k in kolom_wajib):
                csv_data = csv_data[kolom_wajib].copy()
                st.dataframe(csv_data.head(), use_container_width=True)
                if st.button("Import CSV ke Database"):
                    for kolom in ["jumlah", "harga", "meja"]:
                        csv_data[kolom] = pd.to_numeric(csv_data[kolom], errors="raise").astype(int)
                    if csv_data["menu"].isna().any() or (csv_data["menu"].astype(str).str.strip() == "").any():
                        st.error("Ada nama menu yang kosong di file CSV.")
                    else:
                        csv_data.to_sql("transaksi", conn, if_exists="append", index=False)
                        conn.commit()
                        st.success(f"{len(csv_data)} transaksi berhasil diimpor!")
                        st.rerun()
            else:
                st.error("Nama kolom CSV belum sesuai.")
        except Exception as e:
            st.error(f"CSV gagal dibaca atau diimpor: {e}")

    st.divider()
    st.subheader("Ringkasan Menu")
    ringkas_menu = ambil_data().groupby(["menu", "kategori"], as_index=False).agg(
        Total_Terjual=("jumlah", "sum"), Jumlah_Transaksi=("id", "count")
    ).sort_values("Total_Terjual", ascending=False)
    st.dataframe(ringkas_menu, use_container_width=True, hide_index=True)

    st.subheader("Riwayat Transaksi")
    st.caption("Transaksi baru selalu mendapat ID baru. Nama menu yang sama akan masuk ke ringkasan menu, bukan menimpa riwayat lama.")
    data = ambil_data()
    st.dataframe(data, use_container_width=True, hide_index=True)

    if not data.empty:
        pilihan_id = st.selectbox(
            "Pilih ID transaksi yang akan dihapus",
            data["id"].astype(int).tolist(),
        )
        if st.button("Hapus Transaksi"):
            conn.execute("DELETE FROM transaksi WHERE id = ?", (int(pilihan_id),))
            conn.commit()
            st.success("Transaksi berhasil dihapus.")
            st.rerun()

        st.divider()
        st.subheader("Export Data")
        csv_bytes = data.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "Download CSV",
            data=csv_bytes,
            file_name="data_transaksi_restoran.csv",
            mime="text/csv",
        )

        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            data.to_excel(writer, index=False, sheet_name="Transaksi")
        st.download_button(
            "Download Excel",
            data=excel_buffer.getvalue(),
            file_name="data_transaksi_restoran.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        st.divider()
        tampilkan_ikon("document")
        st.subheader("Laporan PDF")
        if st.button("Buat Laporan PDF"):
            pdf_buffer = BytesIO()
            dokumen = SimpleDocTemplate(pdf_buffer, pagesize=A4)
            gaya = getSampleStyleSheet()
            isi = [
                Paragraph("LAPORAN PENJUALAN RESTORAN/KAFE", gaya["Title"]),
                Spacer(1, 15),
            ]
            total_pendapatan = int((data["jumlah"] * data["harga"]).sum())
            total_menu = int(data["jumlah"].sum())
            isi.append(Paragraph(f"Total Pendapatan: Rp{total_pendapatan:,.0f}", gaya["Normal"]))
            isi.append(Paragraph(f"Total Menu Terjual: {total_menu:,}", gaya["Normal"]))
            isi.append(Spacer(1, 15))
            tabel_data = [["ID", "Menu", "Kategori", "Jumlah", "Harga", "Shift"]]
            for _, baris in data.iterrows():
                tabel_data.append([
                    str(baris["id"]),
                    str(baris["menu"]),
                    str(baris["kategori"]),
                    str(baris["jumlah"]),
                    f"Rp{int(baris['harga']):,}",
                    str(baris["shift"]),
                ])
            tabel = Table(tabel_data, repeatRows=1, colWidths=[35, 130, 75, 50, 80, 55])
            tabel.setStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ])
            isi.append(tabel)
            dokumen.build(isi)
            st.download_button(
                "Download Laporan PDF",
                data=pdf_buffer.getvalue(),
                file_name="laporan_penjualan_restoran.pdf",
                mime="application/pdf",
            )