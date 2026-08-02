import streamlit as st

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(
    page_title="Report Outbound Modern", 
    layout="wide", 
    page_icon="📦"
)

# ==========================================
# 2. CSS KUSTOM UNTUK TAMPILAN MODERN & CLEAN UI
# ==========================================
modern_css = """
<style>
    /* Mengubah background utama menjadi abu-abu sangat lembut */
    .stApp {
        background-color: #F8F9FA;
    }
    
    /* Menyembunyikan SEMUA elemen bawaan Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    [data-testid="viewerBadge"] {display: none !important;}

    /* Styling Judul dan Teks */
    h1 {
        color: #1E293B;
        font-weight: 800;
        padding-bottom: 0.5rem;
    }
    h3 {
        color: #334155;
        font-weight: 600;
        font-size: 1.25rem !important;
        margin-top: 1rem;
    }

    /* Styling Tombol Utama (Generate) */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.6rem 1.2rem;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #1D4ED8 0%, #1E40AF 100%);
    }

    /* Styling Tombol Sekunder (Clear / Submit Admin) */
    .stButton > button[kind="secondary"] {
        background-color: #FFFFFF;
        color: #475569;
        border: 1px solid #CBD5E1;
        border-radius: 8px;
        font-weight: 600;
    }
    .stButton > button[kind="secondary"]:hover {
        background-color: #F1F5F9;
        border-color: #94A3B8;
    }

    /* Styling Kotak File Uploader */
    [data-testid="stFileUploader"] {
        background-color: #FFFFFF;
        border: 2px dashed #CBD5E1;
        border-radius: 12px;
        padding: 15px;
    }
</style>
"""
st.markdown(modern_css, unsafe_allow_html=True)

# ==========================================
# 3. HEADER APLIKASI
# ==========================================
st.title("📦 Report Outbound Dashboard")
st.markdown("Sistem otomatisasi modern untuk pengolahan data Logistik, WMS, ERP, dan SLA Outbound.")
st.divider()

# ==========================================
# 4. PENGATURAN ADMIN
# ==========================================
st.subheader("👤 Pengaturan Admin")
col_adm1, col_adm2 = st.columns([3, 1])
with col_adm1:
    admin_input_temp = st.text_input("Nama Admin yang Bertugas:", value="Admin Logistik", label_visibility="collapsed")
with col_adm2:
    submit_admin = st.button("Simpan Admin", kind="secondary", use_container_width=True)

if submit_admin:
    st.success(f"Admin disimpan: {admin_input_temp}")

st.write("") # Spasi pemisah

# ==========================================
# 5. UPLOAD DATA & CLEAR DATA
# ==========================================
st.subheader("📂 Unggah Data Sumber")

# Logika state untuk mereset file uploader
if 'file_uploader_key' not in st.session_state:
    st.session_state['file_uploader_key'] = 0

col_up1, col_up2 = st.columns([5, 1])
with col_up1:
    uploaded_files = st.file_uploader(
        "Unggah file (.xlsx / .csv) sekaligus di sini (termasuk Master.xlsx):", 
        accept_multiple_files=True, 
        type=['xlsx', 'csv'],
        key=f"file_uploader_{st.session_state['file_uploader_key']}"
    )

with col_up2:
    st.write("") 
    st.write("") 
    # Tombol diletakkan di sebelah kanan sejajar dengan uploader
    if st.button("🗑️ Clear Data", kind="secondary", use_container_width=True):
        st.session_state['file_uploader_key'] += 1
        st.rerun()

st.write("") # Spasi pemisah

# ==========================================
# 6. TOMBOL GENERATE & AREA HASIL
# ==========================================
if uploaded_files:
    # Membuat tombol generate lebih rapi dan tidak terlalu panjang
    col_btn1, col_btn2, col_btn3 = st.columns([2, 2, 4])
    with col_btn1:
        generate_clicked = st.button("⚡ Generated Data", kind="primary", use_container_width=True)
    
    if generate_clicked:
        with st.spinner("⏳ Sedang membaca file, mencocokkan baris, dan mengkalkulasi data..."):
            
            # ---------------------------------------------------------
            # DI SINI ANDA BISA MEMASUKKAN KODE LOGIKA PANDAS ANDA
            # (Mulai dari try: sampai except Exception as e:)
            # ---------------------------------------------------------
            
            st.info("Logika proses data (kode asli Anda) akan berjalan di area ini.")
