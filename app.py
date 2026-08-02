import streamlit as st
import datetime

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(
    page_title="Outbound Auto-Processor", 
    layout="wide", 
    initial_sidebar_state="collapsed",
    page_icon="icon.png" # Pastikan file icon.png Anda ada di repositori
)

# Mendapatkan tanggal hari ini (Format: Month DD, YYYY)
current_date = datetime.datetime.now().strftime("%B %d, %Y")

# ==========================================
# 2. CSS KUSTOM UNTUK DESAIN EXACT MATCH
# ==========================================
custom_css = """
<style>
    /* Mengubah background utama menjadi putih bersih */
    .stApp {
        background-color: #FFFFFF;
    }
    
    /* Menyembunyikan elemen bawaan Streamlit secara total */
    #MainMenu, footer, header, .stDeployButton, [data-testid="viewerBadge"] {
        visibility: hidden !important; 
        display: none !important;
    }

    /* Mengurangi jarak padding atas bawaan Streamlit */
    .block-container {
        padding-top: 2rem !important;
        max-width: 1200px;
    }

    /* Styling Typografi Header & Subheader */
    h1 {
        color: #0f172a;
        font-weight: 900;
        letter-spacing: -0.5px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        margin-bottom: 0px !important;
        padding-bottom: 0px !important;
    }
    h3 {
        color: #334155;
        font-weight: 700;
        font-size: 1.4rem !important;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }

    /* Teks Info Officer & Date */
    .meta-text {
        color: #64748b;
        font-size: 15px;
        margin-top: 5px;
        margin-bottom: 20px;
    }
    .officer-name {
        color: #2563eb;
        font-weight: bold;
    }

    /* Kotak File Uploader (Dashed Blue Border) */
    [data-testid="stFileUploader"] {
        background-color: #f8fafc !important;
        border: 1.5px dashed #3b82f6 !important;
        border-radius: 8px !important;
        padding: 20px !important;
    }

    /* Tombol Utama (EXECUTE BATCH PROCESSING) */
    .stButton > button[kind="primary"] {
        background-color: #2563eb !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px;
        padding: 14px 24px !important;
        transition: background-color 0.3s ease;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #1d4ed8 !important;
    }

    /* Tombol Sekunder (Clear Buffer & Submit Admin) */
    .stButton > button[kind="secondary"] {
        background-color: #ffffff !important;
        color: #475569 !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        padding: 14px 24px !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background-color: #f1f5f9 !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)


# ==========================================
# 3. HEADER & META INFO SECTION
# ==========================================
# Menyimpan status Admin di Session
if 'saved_admin' not in st.session_state:
    st.session_state['saved_admin'] = "Admin Logistik"

# Trik layout menggunakan kolom agar logo kustom bersebelahan dengan teks
col_header1, col_header2 = st.columns([1, 15])
with col_header1:
    # Memanggil file gambar sebagai ikon (opsional, jika Anda masih ingin pakai logo tumpukan kertas)
    try:
        st.image("icon.png", width=60)
    except:
        pass # Mengabaikan error jika file gambar belum diupload
with col_header2:
    st.markdown('<h1 style="margin-top: -10px;">Outbound Auto-Processor</h1>', unsafe_allow_html=True)

# Baris Info
st.markdown(f'<div class="meta-text">Officer: <span class="officer-name">{st.session_state["saved_admin"]}</span> | Date: {current_date}</div>', unsafe_allow_html=True)

# Kotak Input Admin & Tombol Submit
col_adm1, col_adm2 = st.columns([4, 1])
with col_adm1:
    admin_input = st.text_input("Admin", value=st.session_state['saved_admin'], label_visibility="collapsed", placeholder="Ketik nama Officer / Admin...")
with col_adm2:
    submit_admin = st.button("Submit Admin", kind="secondary", use_container_width=True)

if submit_admin:
    st.session_state['saved_admin'] = admin_input
    st.rerun()

st.divider()


# ==========================================
# 4. DATA CENTER (UPLOAD SECTION)
# ==========================================
st.markdown('<h3>📁 Data Center</h3>', unsafe_allow_html=True)
st.markdown('<div style="color: #475569; font-size: 14px; margin-bottom: 12px;">Upload multiple source files (Order Summary, Operation Log, ERP, HO Outbound, Master) to begin.</div>', unsafe_allow_html=True)

# State untuk mereset file uploader
if 'file_uploader_key' not in st.session_state:
    st.session_state['file_uploader_key'] = 0

col_up1, col_up2 = st.columns([5, 1])
with col_up1:
    uploaded_files = st.file_uploader(
        "Upload Area", 
        accept_multiple_files=True, 
        type=['xlsx', 'csv'],
        key=f"uploader_{st.session_state['file_uploader_key']}",
        label_visibility="collapsed"
    )

with col_up2:
    if st.button("🗑️ Clear Buffer", kind="secondary", use_container_width=True):
        st.session_state['file_uploader_key'] += 1
        st.rerun()

st.write("")


# ==========================================
# 5. PROCESSING QUEUE (EXECUTE SECTION)
# ==========================================
st.markdown('<h3>⚙️ Processing Queue</h3>', unsafe_allow_html=True)

# Tombol Biru Lebar
execute_clicked = st.button("🚀 EXECUTE BATCH PROCESSING", kind="primary", use_container_width=True)

if execute_clicked:
    if uploaded_files:
        st.success(f"Logika pemrosesan untuk {len(uploaded_files)} file siap dijalankan di sini!")
        # ---------------------------------------------------------
        # DI SINI ANDA BISA MEMASUKKAN KODE LOGIKA PANDAS ANDA
        # (Mulai dari with st.spinner("Sedang membaca file..."): try: sampai selesai)
        # ---------------------------------------------------------
    else:
        st.warning("Silakan unggah file sumber terlebih dahulu di area Data Center.")
