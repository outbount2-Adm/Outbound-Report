import pandas as pd
import streamlit as st

# Konfigurasi Halaman
st.set_page_config(
    page_title="Report Outbound Auto-Processor", page_icon="📦", layout="wide"
)

# KODE CSS: Menyembunyikan menu atas, footer, dan tombol "Manage app" di pojok kanan bawah secara total
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display: none !important;}
    div[data-testid="stStatusWidget"] {display: none !important; visibility: hidden !important;}
    .viewerBadge_container__1QSob, .styles_viewerBadge__1yB5_, .viewerBadge_link__1S137 {display: none !important; visibility: hidden !important;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Judul dan Deskripsi Aplikasi
st.markdown(
    "<h1>📦 Report Outbound Auto-Processor</h1>", unsafe_allow_html=True
)
st.write(
    "Unggah File Order Summary Export, Export Operation Log, ERP, HO Outbound,"
    " Pack Task Perform Report, dan Master."
)

st.markdown("---")

# Bagian Pengaturan Admin
st.subheader("Pengaturan Admin")
admin_name = st.text_input("Nama Admin yang Bertugas:", value="Admin Logistik")

if st.button("Submit Admin"):
  if admin_name:
    st.success(f"Admin yang bertugas berhasil disimpan: **{admin_name}**")
  else:
    st.warning("Silakan masukkan nama admin terlebih dahulu.")

st.markdown("---")

# Bagian Upload Data Sumber
st.subheader("Upload Data Sumber")
st.write(
    "Upload file sumber (.xlsx / .csv) sekaligus di sini (termasuk Master.xlsx):"
)

uploaded_files = st.file_uploader(
    "Upload",
    type=["xlsx", "csv"],
    accept_multiple_files=True,
    label_visibility="collapsed",
)

# Logika jika file diunggah
if uploaded_files:
  st.success(f"Total {len(uploaded_files)} file berhasil diunggah!")
  for file in uploaded_files:
    st.write(f"📁 **{file.name}**")
