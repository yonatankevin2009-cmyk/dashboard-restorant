import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(
    page_title="Dashboard Restoran",
    page_icon="🍽️",
    layout="wide"
)

st.title("🍽️ Dashboard Penjualan Restoran/Kafe")

# Membuat database
conn = sqlite3.connect("restoran.db", check_same_thread=False)

conn.execute("""
CREATE TABLE IF NOT EXISTS transaksi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    menu TEXT,
    kategori TEXT,
    jumlah INTEGER,
    harga INTEGER,
    shift TEXT,
    jenis_pesanan TEXT,
    meja INTEGER
)
""")
conn.commit()


def ambil_data():
    return pd.read_sql_query("SELECT * FROM transaksi", conn)


def hitung_pendapatan(data):
    if data.empty:
        return data.assign(Total_Pendapatan=pd.Series(dtype=int))
    data = data.copy()
    data["Total_Pendapatan"] = data["jumlah"] * data["harga"]
    return data


# Data awal hanya dimasukkan jika database masih kosong
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


# Navigasi halaman
halaman = st.sidebar.radio(
    "Pilih Halaman",
    ["Home", "Dashboard Analytics", "Data Management"]
)

if halaman == "Home":
    st.header("Selamat Datang!")
    st.write("""
    Aplikasi ini digunakan untuk memantau penjualan restoran atau kafe.

    Fitur yang tersedia:
    - Dashboard statistik dan grafik.
    - Pengelolaan data transaksi.
    - Import data CSV.
    - Export data CSV dan Excel.
    """)
    st.info("Pilih menu di sebelah kiri untuk mulai menggunakan aplikasi.")


elif halaman == "Dashboard Analytics":
    data = hitung_pendapatan(ambil_data())

    st.header("📊 Dashboard Analytics")

    if data.empty:
        st.warning("Belum ada data transaksi.")
    else:
        jenis = st.sidebar.multiselect(
            "Jenis Pesanan",
            sorted(data["jenis_pesanan"].dropna().unique()),
            default=sorted(data["jenis_pesanan"].dropna().unique())
        )

        shift = st.sidebar.multiselect(
            "Shift",
            sorted(data["shift"].dropna().unique()),
            default=sorted(data["shift"].dropna().unique())
        )

        tampil = data[
            data["jenis_pesanan"].isin(jenis)
            & data["shift"].isin(shift)
        ]

        pendapatan = tampil["Total_Pendapatan"].sum()
        total_menu = tampil["jumlah"].sum()
        meja_terisi = tampil.loc[
            tampil["jenis_pesanan"] == "Dine-in", "meja"
        ].nunique()

        c1, c2, c3 = st.columns(3)
        c1.metric("Total Pendapatan", f"Rp{pendapatan:,.0f}")
        c2.metric("Menu Terjual", f"{total_menu}")
        c3.metric("Meja Terisi", f"{meja_terisi}")

        favorit = tampil.groupby("menu", as_index=False)["jumlah"].sum()
        favorit = favorit.sort_values("jumlah", ascending=False)

        st.subheader("Menu Paling Favorit")
        st.plotly_chart(
            px.bar(favorit, x="menu", y="jumlah", title="Jumlah Menu Terjual"),
            use_container_width=True
        )

        omzet = tampil.groupby("shift", as_index=False)[
            "Total_Pendapatan"
        ].sum()

        st.subheader("Pendapatan Berdasarkan Shift")
        st.plotly_chart(
            px.line(
                omzet,
                x="shift",
                y="Total_Pendapatan",
                markers=True,
                title="Total Pendapatan per Shift"
            ),
            use_container_width=True
        )

        kategori = tampil.groupby("kategori", as_index=False)["jumlah"].sum()

        st.subheader("Penjualan Makanan vs Minuman")
        st.plotly_chart(
            px.pie(kategori, names="kategori", values="jumlah"),
            use_container_width=True
        )

        st.subheader("Data Transaksi")
        st.dataframe(tampil, use_container_width=True)


elif halaman == "Data Management":
    st.header("🗂️ Data Management")

    st.write("Tambahkan transaksi baru atau impor data dari file CSV.")

    with st.expander("➕ Tambah Transaksi", expanded=True):
        with st.form("form_transaksi"):
            menu = st.text_input("Nama Menu")
            kategori = st.selectbox("Kategori", ["Makanan", "Minuman"])
            jumlah = st.number_input("Jumlah Terjual", min_value=1, value=1)
            harga = st.number_input("Harga per Menu (Rp)", min_value=0, value=10000)
            shift = st.selectbox("Shift", ["Pagi", "Malam"])
            jenis = st.selectbox("Jenis Pesanan", ["Dine-in", "Takeaway"])
            meja = st.number_input("Nomor Meja", min_value=1, value=1)

            simpan = st.form_submit_button("Simpan Transaksi")

            if simpan:
                if not menu.strip():
                    st.error("Nama menu tidak boleh kosong.")
                else:
                    conn.execute("""
                        INSERT INTO transaksi
                        (menu, kategori, jumlah, harga, shift, jenis_pesanan, meja)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        menu.strip(), kategori, jumlah, harga,
                        shift, jenis, meja
                    ))
                    conn.commit()
                    st.success("Transaksi berhasil disimpan!")
                    st.rerun()

    st.divider()

    st.subheader("📥 Import Data CSV")
    st.caption(
        "Kolom CSV harus bernama: menu, kategori, jumlah, harga, "
        "shift, jenis_pesanan, meja."
    )

    file_csv = st.file_uploader("Pilih file CSV", type=["csv"])

    if file_csv is not None:
        try:
            csv_data = pd.read_csv(file_csv)
            kolom_wajib = [
                "menu", "kategori", "jumlah", "harga",
                "shift", "jenis_pesanan", "meja"
            ]

            if all(k in csv_data.columns for k in kolom_wajib):
                st.dataframe(csv_data.head(), use_container_width=True)

                if st.button("Import CSV ke Database"):
                    csv_data = csv_data[kolom_wajib].copy()
                    csv_data["jumlah"] = pd.to_numeric(
                        csv_data["jumlah"], errors="raise"
                    )
                    csv_data["harga"] = pd.to_numeric(
                        csv_data["harga"], errors="raise"
                    )
                    csv_data["meja"] = pd.to_numeric(
                        csv_data["meja"], errors="raise"
                    )

                    csv_data.to_sql(
                        "transaksi", conn, if_exists="append", index=False
                    )
                    st.success("Data CSV berhasil diimpor!")
                    st.rerun()
            else:
                st.error("Nama kolom CSV belum sesuai.")
        except Exception as e:
            st.error(f"CSV gagal dibaca: {e}")

    st.divider()

    st.subheader("📋 Daftar Transaksi")
    data = ambil_data()
    st.dataframe(data, use_container_width=True)

    if not data.empty:
        pilihan_id = st.selectbox(
            "Pilih ID transaksi yang akan dihapus",
            data["id"].tolist()
        )

        if st.button("🗑️ Hapus Transaksi"):
            conn.execute(
                "DELETE FROM transaksi WHERE id = ?", (int(pilihan_id),)
            )
            conn.commit()
            st.success("Transaksi berhasil dihapus.")
            st.rerun()

        st.divider()

        st.subheader("📤 Export Data")

        csv_bytes = data.to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            "Download CSV",
            data=csv_bytes,
            file_name="data_transaksi_restoran.csv",
            mime="text/csv"
        )

        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            data.to_excel(writer, index=False, sheet_name="Transaksi")

        st.download_button(
            "Download Excel",
            data=excel_buffer.getvalue(),
            file_name="data_transaksi_restoran.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )