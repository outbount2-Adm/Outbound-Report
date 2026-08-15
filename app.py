import streamlit as st
import pandas as pd
import numpy as np
import traceback
import datetime
from io import BytesIO

# ==========================================
# 1. KONFIGURASI HALAMAN 
# ==========================================
st.set_page_config(
    page_title="Outbound Logistic Dashboard", 
    layout="wide", 
    page_icon="📦", 
    initial_sidebar_state="collapsed"
)

current_date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ==========================================
# 2. CSS KUSTOM (Aman & Tanpa Skrip Eksternal)
# ==========================================
custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp { 
        background-color: #F0F2F5; 
    }

    /* ==========================================
       SEMBUNYIKAN SIDEBAR & KONTROLNYA SECARA TOTAL
       ========================================== */
    [data-testid="stSidebar"] {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
    }
    [data-testid="collapsedControl"] {
        display: none !important;
        visibility: hidden !important;
    }
    section[data-testid="stSidebar"] {
        display: none !important;
    }

    /* Top Bar / Header */
    .top-bar {
        background-color: white;
        padding: 10px 20px;
        border-radius: 8px;
        border: 1px solid #E8E8E8;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }

    /* Section Cards */
    .section-container {
        background-color: white;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #E8E8E8;
    }
    .section-title {
        font-size: 16px;
        font-weight: 700;
        color: #262626;
        margin-bottom: 15px;
        border-bottom: 1px solid #F0F0F0;
        padding-bottom: 10px;
    }

    /* Metric Cards (Todo Style) */
    .todo-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
        gap: 15px;
        margin-bottom: 10px;
    }
    .todo-card {
        border-radius: 6px;
        padding: 15px;
        color: white;
        min-height: 90px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .todo-card-teal { background: linear-gradient(135deg, #26C1C9 0%, #19A7AF 100%); }
    .todo-card-blue { background: linear-gradient(135deg, #4B7CF3 0%, #3A62D7 100%); }
    .todo-card-red  { background: linear-gradient(135deg, #EF4444 0%, #B91C1C 100%); }
    .todo-card-amber{ background: linear-gradient(135deg, #F59E0B 0%, #B45309 100%); }
    
    .todo-label { font-size: 13px; font-weight: 500; opacity: 0.95; line-height: 1.3; }
    .todo-value { font-size: 22px; font-weight: 700; margin-top: 8px; }

    /* Form Inputs & Buttons */
    [data-testid="stTextInput"] > div > div > input {
        border-radius: 6px;
        border: 1px solid #D9D9D9;
        background-color: #FFFFFF;
        color: #000000;
    }
    div[data-testid="stButton"] > button {
        border-radius: 6px !important;
        font-weight: 600 !important;
    }
    
    .result-notif {
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
        font-weight: 600;
        display: flex;
        align-items: center;
    }
    .result-warning { background-color: #FEF2F2; color: #991B1B; border: 1px solid #FCA5A5; }

    /* ==========================================
       SEMBUNYIKAN MENU & BADGE POJOK KANAN BAWAH
       ========================================== */
    #MainMenu { visibility: hidden !important; display: none !important; }
    footer { visibility: hidden !important; display: none !important; }
    header { visibility: hidden !important; display: none !important; }
    .stDeployButton { visibility: hidden !important; display: none !important; }
    [data-testid="stToolbar"] { visibility: hidden !important; display: none !important; }
    [data-testid="stDecoration"] { visibility: hidden !important; display: none !important; }
    [data-testid="stStatusWidget"] { visibility: hidden !important; display: none !important; }
    
    div[class*="viewerBadge"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }
    
    /* Penyesuaian alignment widget dalam kolom */
    div[data-testid="column"] > div > div[data-testid="stVerticalBlock"] > div.element-container {
        margin-top: 0px;
    }
    /* Memberikan jarak sedikit pada tombol agar tidak menempel ke input */
    div[data-testid="column"] > div > div[data-testid="stVerticalBlock"] > div.stButton {
        margin-top: 28px; /* Sesuaikan agar sejajar dengan input field */
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# 3. TOP BAR & DATA CENTER (UPLOAD + INPUT OFFICER)
# ==========================================
st.markdown(f"""
    <div class="top-bar">
        <div style="font-weight: 700; color: #1890FF; font-size: 16px;">📦 Automated Data Processing</div>
        <div style="font-size: 13px; color: #8C8C8C;">Update time: {current_date_time} <span style="color: #1890FF; margin-left: 10px; font-weight: 600;">Active 🔄</span></div>
    </div>
""", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📁 Data Center & Konfigurasi Officer</div>', unsafe_allow_html=True)
    
    if 'saved_admin' not in st.session_state:
        st.session_state['saved_admin'] = "Admin Logistik"

    # --- PERUBAHAN DIMULAI DI SINI ---
    # Membuat 3 kolom: Input Nama (lebar 3), Tombol Update (lebar 1), Tombol Reset (lebar 1)
    col_input, col_update, col_reset = st.columns([3, 1, 1])
    
    with col_input:
        admin_input = st.text_input("✍️ Input Officer Name", value=st.session_state['saved_admin'])
        
    with col_update:
        # Tambahkan sedikit spasi kosong di atas tombol agar sejajar dengan input field
        st.write("") 
        if st.button("Update Nama", use_container_width=True, type="secondary"):
            st.session_state['saved_admin'] = admin_input
            st.success("Nama diperbarui!")
            # Menggunakan st.rerun() untuk merefresh UI dengan nilai baru
            st.rerun()
            
    with col_reset:
        st.write("")
        if st.button("🗑️ Reset Cache", use_container_width=True, type="secondary"):
            if 'file_uploader_key' not in st.session_state: st.session_state['file_uploader_key'] = 0
            st.session_state['file_uploader_key'] += 1
            for k in ['processed_result', 'excel_data', 'metrics']:
                if k in st.session_state: del st.session_state[k]
            st.rerun()
    # --- PERUBAHAN SELESAI DI SINI ---

    st.divider()
    st.markdown('<div style="color: #475569; font-size: 14px; margin-bottom: 15px;">Seret dan lepas file sumber Anda di bawah ini untuk memulai pemrosesan otomatis.</div>', unsafe_allow_html=True)

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
        st.write("")
        files_ready = len(uploaded_files) > 0
        execute_clicked = st.button(
            "Proses Data 🚀" if files_ready else "Upload File", 
            type="primary", 
            use_container_width=True,
            disabled=not files_ready
        )

    # ==========================================
    # 4. LOGIKA UTAMA PEMPROSESAN DATA
    # ==========================================
    if execute_clicked:
        if uploaded_files:
            progress_bar = st.progress(0, text="Processing... (0%)")
            try:
                progress_bar.progress(10, text="Processing... (Membaca file sumber) [10%]")
                dfs = {}
                master_store_db = {}
                master_carrier_db = {}
                
                for file in uploaded_files:
                    file_name = file.name.lower()
                    df = pd.read_excel(file) if file_name.endswith('.xlsx') else pd.read_csv(file)
                    df.columns = df.columns.astype(str).str.strip().str.replace('\xa0', ' ')
                    df = df.loc[:, ~df.columns.duplicated()]
                    
                    if 'master' in file_name:
                        dfs['master'] = df
                        if 'Store Number' in df.columns:
                            store_df = df[['Store Number', 'Brand', 'Brand2']].dropna(subset=['Store Number'])
                            for _, row in store_df.iterrows():
                                sn = str(row['Store Number']).strip()
                                sn = sn[:-2] if sn.endswith('.0') else sn
                                master_store_db[sn] = {"Brand": str(row['Brand']).strip() if pd.notna(row['Brand']) else "", "Brand2": str(row['Brand2']).strip() if pd.notna(row['Brand2']) else ""}
                        if 'carrierCode' in df.columns:
                            carrier_df = df[['carrierCode', 'Kurir']].dropna(subset=['carrierCode'])
                            for _, row in carrier_df.iterrows():
                                master_carrier_db[str(row['carrierCode']).strip()] = str(row['Kurir']).strip() if pd.notna(row['Kurir']) else ""
                    elif 'daily' in file_name:
                        dfs['daily_ho'] = df
                    elif 'ho' in file_name or 'outbound' in file_name: 
                        rename_map = {}
                        for col in df.columns:
                            c_lower = col.lower()
                            if 'no wms' in c_lower: rename_map[col] = 'WMS Order'
                            elif 'expedisi' in c_lower: rename_map[col] = 'Expedisi'
                            elif c_lower == 'tanggal': rename_map[col] = 'Tgl_HO_Source'
                        dfs['ho_outbound'] = df.rename(columns=rename_map)
                    elif 'order summary' in file_name:
                        if 'open' in file_name: dfs['order_summary_open'] = df
                        if 'order_summary' not in dfs: dfs['order_summary'] = df
                        elif 'open' not in file_name: dfs['order_summary'] = df
                    elif 'operation log' in file_name: 
                        rename_map_op = {}
                        for col in df.columns:
                            c_lower = col.lower()
                            if 'wms order' in c_lower: rename_map_op[col] = 'WMS Order#'
                            elif c_lower == 'event': rename_map_op[col] = 'Event'
                            elif c_lower == 'operator': rename_map_op[col] = 'operator'
                        dfs['op_log'] = df.rename(columns=rename_map_op)
                    elif 'pack task' in file_name: dfs['pack_task'] = df
                    elif 'erp' in file_name: dfs['erp'] = df

                if 'ho_outbound' not in dfs or 'order_summary' not in dfs:
                    st.error("❌ File 'HO Outbound' atau 'Order Summary' tidak ditemukan.")
                    st.stop()

                for key in ['op_log', 'pack_task', 'erp', 'daily_ho']:
                    if key not in dfs: dfs[key] = pd.DataFrame()

                progress_bar.progress(35, text="Processing... (Mencocokkan baris & Merge data) [35%]")
                df_ho = dfs['ho_outbound'].copy()
                res = pd.DataFrame({'WMS Order': df_ho['WMS Order']})
                
                df_order = dfs['order_summary']
                col_order_summary = next((c for c in df_order.columns if 'order#' in c.lower()), None)
                if not df_order.empty and col_order_summary:
                    df_order = df_order.drop_duplicates(subset=[col_order_summary]).loc[:, ~df_order.columns.duplicated()]
                    res = res.merge(df_order, left_on='WMS Order', right_on=col_order_summary, how='left')

                col_ext_order = next((c for c in res.columns if 'ext. order#' in c.lower()), None)
                if col_ext_order:
                    erp_raw = res[col_ext_order].astype(str).str.strip()
                    res['ERP Document Number'] = np.where(erp_raw.str.startswith("CKSQ", na=False), erp_raw.str[:11], erp_raw.str[:14])
                else:
                    res['ERP Document Number'] = np.nan
                
                col_track = next((c for c in res.columns if 'tracking#' in c.lower() or 'pro#' in c.lower()), None)
                col_ref = next((c for c in res.columns if 'ref#' in c.lower()), None)
                res
