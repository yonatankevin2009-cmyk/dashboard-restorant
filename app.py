import streamlit as st

st.set_page_config(page_title="Dashboard Kafe", layout="wide")

st.title("Dashboard Penjualan Restoran/Kafe")
st.success("Website berhasil dijalankan!")

col1, col2, col3 = st.columns(3)

col1.metric("Total Pendapatan", "Rp1.500.000")
col2.metric("Menu Terjual", 120)
col3.metric("Meja Terisi", 8)

st.write("Dashboard ini dibuat untuk tugas KKA kelas 12 TEI.")
