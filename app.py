import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Dashboard Restoran/Kafe",
    page_icon="☕",
    layout="wide"
)

# JUDUL
st.title("☕ Dashboard Penjualan Restoran/Kafe")
st.caption("Dashboard interaktif penjualan makanan dan minuman")

# DATA TRANSAKSI CONTOH
df = pd.DataFrame({
    "Menu": [
        "Nasi Goreng", "Mie Ayam", "Es Teh",
        "Kopi Susu", "Ayam Geprek", "Jus Jeruk",
        "Nasi Goreng", "Es Teh", "Mie Ayam",
        "Kopi Susu", "Ayam Geprek", "Jus Jeruk"
    ],
    "Kategori": [
        "Makanan", "Makanan", "Minuman",
        "Minuman", "Makanan", "Minuman",
        "Makanan", "Minuman", "Makanan",
        "Minuman", "Makanan", "Minuman"
    ],
    "Jumlah_Terjual": [
        20, 15, 30, 18, 25, 12,
        10, 22, 8, 14, 16, 9
    ],
    "Harga": [
        15000, 12000, 5000, 10000, 18000, 8000,
        15000, 5000, 12000, 10000, 18000, 8000
    ],
    "Shift": [
        "Pagi", "Pagi", "Pagi", "Malam",
        "Malam", "Malam", "Malam", "Pagi",
        "Malam", "Pagi", "Malam", "Pagi"
    ],
    "Jenis_Pesanan": [
        "Dine-in", "Takeaway", "Dine-in", "Takeaway",
        "Dine-in", "Takeaway", "Takeaway", "Dine-in",
        "Takeaway", "Dine-in", "Takeaway", "Dine-in"
    ],
    "Meja": [
        1, 0, 2, 0, 3, 0,
        0, 2, 0, 1, 0, 2
    ]
})

df["Total_Pendapatan"] = (
    df["Jumlah_Terjual"] * df["Harga"]
)

# FILTER SIDEBAR
st.sidebar.header("Filter Data")

jenis = st.sidebar.selectbox(
    "Jenis Pesanan",
    ["Semua", "Dine-in", "Takeaway"]
)

shift_pilihan = st.sidebar.selectbox(
    "Shift",
    ["Semua", "Pagi", "Malam"]
)

filtered = df.copy()

if jenis != "Semua":
    filtered = filtered[
        filtered["Jenis_Pesanan"] == jenis
    ]

if shift_pilihan != "Semua":
    filtered = filtered[
        filtered["Shift"] == shift_pilihan
    ]

# KPI
pendapatan = filtered["Total_Pendapatan"].sum()
terjual = filtered["Jumlah_Terjual"].sum()
meja = filtered["Meja"].sum()

st.subheader("Ringkasan Penjualan")

k1, k2, k3 = st.columns(3)

k1.metric(
    "Total Pendapatan",
    f"Rp{pendapatan:,.0f}".replace(",", ".")
)

k2.metric(
    "Menu Terjual",
    f"{terjual:,}".replace(",", ".")
)

k3.metric(
    "Jumlah Meja Terisi pada Data",
    f"{meja:,}".replace(",", ".")
)

st.divider()

# GRAFIK MENU FAVORIT
st.subheader("📊 Menu Paling Favorit")

menu = (
    filtered.groupby("Menu", as_index=False)
    ["Jumlah_Terjual"].sum()
    .sort_values("Jumlah_Terjual", ascending=False)
)

fig1 = px.bar(
    menu,
    x="Menu",
    y="Jumlah_Terjual",
    title="Jumlah Menu Terjual",
    labels={
        "Menu": "Nama Menu",
        "Jumlah_Terjual": "Jumlah Terjual"
    },
    color="Menu"
)

st.plotly_chart(fig1, use_container_width=True)

# GRAFIK PENDAPATAN PER SHIFT
st.subheader("📈 Pendapatan Berdasarkan Shift")

shift_data = (
    filtered.groupby("Shift", as_index=False)
    ["Total_Pendapatan"].sum()
)

urutan_shift = ["Pagi", "Malam"]
shift_data["Shift"] = pd.Categorical(
    shift_data["Shift"],
    categories=urutan_shift,
    ordered=True
)
shift_data = shift_data.sort_values("Shift")

fig2 = px.line(
    shift_data,
    x="Shift",
    y="Total_Pendapatan",
    markers=True,
    title="Perbandingan Pendapatan Shift Pagi dan Malam",
    labels={
        "Shift": "Shift",
        "Total_Pendapatan": "Pendapatan (Rp)"
    }
)

st.plotly_chart(fig2, use_container_width=True)

# DIAGRAM MAKANAN DAN MINUMAN
st.subheader("🥧 Penjualan Makanan vs Minuman")

kategori = (
    filtered.groupby("Kategori", as_index=False)
    ["Jumlah_Terjual"].sum()
)

fig3 = px.pie(
    kategori,
    names="Kategori",
    values="Jumlah_Terjual",
    title="Proporsi Penjualan Berdasarkan Kategori"
)

st.plotly_chart(fig3, use_container_width=True)

# TABEL TRANSAKSI
st.subheader("📋 Data Transaksi")

st.dataframe(
    filtered,
    use_container_width=True,
    hide_index=True
)

# DOWNLOAD CSV
csv = filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Unduh Data Transaksi CSV",
    data=csv,
    file_name="data_penjualan_kafe.csv",
    mime="text/csv"
)

st.caption(
    "Catatan: Data di atas merupakan data simulasi "
    "untuk keperluan demonstrasi tugas KKA."
)