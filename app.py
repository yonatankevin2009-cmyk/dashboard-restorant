import sqlite3
from io import BytesIO

import pandas as pd
import plotly.express as px
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table

st.set_page_config(page_title="Dashboard Restoran", page_icon="🍽️", layout="wide")

# LOGIN DEMO - hanya untuk demonstrasi tugas sekolah
if "sudah_login" not in st.session_state:
    st.session_state.sudah_login = False

if not st.session_state.sudah_login:
    st.title("🔐 Login Dashboard Restoran")
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

# DATABASE SQLITE
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


# Data contoh hanya dimasukkan jika tabel kosong
if ambil_data().empty:
    data_awal = [
        ("Nasi Goreng", "Makanan", 10, 18000, "Pagi", "Dine-in", 1),
        ("Mie Goreng", "Makanan", 8, 15000, "Malam", "Takeaway", 2),
        ("Ayam Geprek", "Makanan", 12, 20000, "Malam", "Dine-in", 3),
        ("Es Teh", "Minuman", 15, 5000, "Pagi", "Takeaway", 4),
        ("Kopi Susu", "Minuman", 10, 12000, "Pagi", "Dine-in", 5),
        ("Jus Jeruk", "Minuman", 7, 10000, "Malam", "Takeaway", 6),
    ]
    conn.executemany("""
        INSERT INTO transaksi
        (menu, kategori, jumlah, harga, shift, jenis_pesanan, meja)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, data_awal)
    conn.commit()

st.sidebar.title("🍽️ Menu")
halaman = st.sidebar.radio("Pilih Halaman", ["Home", "Dashboard Analytics", "Data Management"])
if st.sidebar.button("🚪 Logout"):
    st.session_state.sudah_login = False
    st.rerun()

st.title("🍽️ Dashboard Penjualan Restoran/Kafe")

if halaman == "Home":
    st.header("Selamat Datang!")
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

elif halaman == "Dashboard Analytics":
    data = hitung_pendapatan(ambil_data())
    st.header("📊 Dashboard Analytics")
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
            st.plotly_chart(px.bar(favorit, x="menu", y="jumlah", title="Jumlah Menu Terjual"), use_container_width=True)
            omzet = tampil.groupby("shift", as_index=False)["Total_Pendapatan"].sum()
            st.subheader("Pendapatan Berdasarkan Shift")
            st.plotly_chart(px.line(omzet, x="shift", y="Total_Pendapatan", markers=True, title="Total Pendapatan per Shift"), use_container_width=True)
            kategori_data = tampil.groupby("kategori", as_index=False)["jumlah"].sum()
            st.subheader("Penjualan Makanan vs Minuman")
            st.plotly_chart(px.pie(kategori_data, names="kategori", values="jumlah"), use_container_width=True)
            st.subheader("Data Transaksi")
            st.dataframe(tampil, use_container_width=True, hide_index=True)

elif halaman == "Data Management":
    st.header("🗂️ Data Management")
    st.write("Tambahkan transaksi baru atau impor data CSV.")
    with st.expander("➕ Tambah Transaksi", expanded=True):
        with st.form("form_transaksi", clear_on_submit=True):
            menu = st.text_input("Nama Menu")
            kategori = st.selectbox("Kategori", ["Makanan", "Minuman"])
            jumlah = st.number_input("Jumlah Terjual", min_value=1, value=1, step=1)
            harga = st.number_input("Harga per Menu (Rp)", min_value=0, value=10000, step=1000)
            shift = st.selectbox("Shift", ["Pagi", "Malam"])
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
    st.subheader("📥 Import Data CSV")
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
    st.subheader("📋 Daftar Transaksi")
    data = ambil_data()
    st.dataframe(data, use_container_width=True, hide_index=True)
    if not data.empty:
        pilihan_id = st.selectbox("Pilih ID transaksi yang akan dihapus", data["id"].astype(int).tolist())
        if st.button("🗑️ Hapus Transaksi"):
            conn.execute("DELETE FROM transaksi WHERE id = ?", (int(pilihan_id),))
            conn.commit()
            st.success("Transaksi berhasil dihapus.")
            st.rerun()

        st.divider()
        st.subheader("📤 Export Data")
        csv_bytes = data.to_csv(index=False).encode("utf-8-sig")
        st.download_button("Download CSV", data=csv_bytes, file_name="data_transaksi_restoran.csv", mime="text/csv")
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            data.to_excel(writer, index=False, sheet_name="Transaksi")
        st.download_button("Download Excel", data=excel_buffer.getvalue(), file_name="data_transaksi_restoran.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        st.divider()
        st.subheader("📄 Laporan PDF")
        if st.button("Buat Laporan PDF"):
            pdf_buffer = BytesIO()
            dokumen = SimpleDocTemplate(pdf_buffer, pagesize=A4)
            gaya = getSampleStyleSheet()
            isi = [Paragraph("LAPORAN PENJUALAN RESTORAN/KAFE", gaya["Title"]), Spacer(1, 15)]
            total_pendapatan = int((data["jumlah"] * data["harga"]).sum())
            total_menu = int(data["jumlah"].sum())
            isi.append(Paragraph(f"Total Pendapatan: Rp{total_pendapatan:,.0f}", gaya["Normal"]))
            isi.append(Paragraph(f"Total Menu Terjual: {total_menu:,}", gaya["Normal"]))
            isi.append(Spacer(1, 15))
            tabel_data = [["ID", "Menu", "Kategori", "Jumlah", "Harga", "Shift"]]
            for _, baris in data.iterrows():
                tabel_data.append([str(baris["id"]), str(baris["menu"]), str(baris["kategori"]), str(baris["jumlah"]), f"Rp{int(baris['harga']):,}", str(baris["shift"])])
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
            st.download_button("⬇️ Download Laporan PDF", data=pdf_buffer.getvalue(), file_name="laporan_penjualan_restoran.pdf", mime="application/pdf")