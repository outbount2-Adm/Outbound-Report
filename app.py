import streamlit as st
import pandas as pd
import numpy as np
import traceback
import datetime
from io import BytesIO

# ==========================================
# 1. KONFIGURASI HALAMAN MODERN
# ==========================================
st.set_page_config(
    page_title="Logistics Outbound Processor", 
    layout="wide", 
    page_icon="📦", 
    initial_sidebar_state="collapsed"
)

current_date = datetime.datetime.now().strftime("%d %B %Y")

# ==========================================
# 2. CSS KUSTOM MODERN (Tingkat Lanjut)
# ==========================================
custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

    :root {
        --primary-color: #2563eb;
        --primary-hover: #1d4ed8;
        --bg-color: #f8fafc;
        --card-bg: #ffffff;
        --text-main: #0f172a;
        --text-muted: #64748b;
        --border-color: #e2e8f0;
        --success-bg: #f0fdf4;
        --success-text: #166534;
        --warning-bg: #fffbeb;
        --warning-text: #92400e;
    }

    .stApp { 
        background-color: var(--bg-color);
        font-family: 'Inter', sans-serif;
    }

    #MainMenu, footer, header, .stDeployButton, [data-testid="viewerBadge"] {
        visibility: hidden !important; 
        display: none !important;
    }

    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 1200px;
        margin: auto;
    }

    /* Typography */
    h1 {
        color: var(--text-main);
        font-weight: 800;
        letter-spacing: -0.025em;
        font-size: 2.25rem !important;
        margin-bottom: 0.5rem !important;
    }

    h3 {
        color: var(--text-main);
        font-weight: 700;
        font-size: 1.25rem !important;
        margin-top: 0;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .meta-text {
        color: var(--text-muted);
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }

    /* Modern Card */
    .modern-card {
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
        margin-bottom: 24px;
        transition: transform 0.2s ease;
    }

    /* Officer Panel */
    .officer-panel {
        background-color: #f1f5f9;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 0;
        border: 1px solid var(--border-color);
    }

    .officer-name { 
        color: var(--primary-color); 
        font-weight: 700; 
    }

    /* Inputs */
    [data-testid="stTextInput"] > div > div > input {
        border-radius: 8px;
        border: 1px solid var(--border-color);
        padding: 8px 12px !important;
        transition: border-color 0.2s;
    }
    
    [data-testid="stTextInput"] > div > div > input:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1);
    }

    /* File Uploader */
    [data-testid="stFileUploader"] {
        border: 2px dashed var(--border-color) !important;
        border-radius: 12px !important;
        padding: 20px !important;
        background-color: #fafafa !important;
    }
    
    [data-testid="stFileUploader"] section {
        padding: 0 !important;
    }

    /* Buttons */
    div[data-testid="stButton"] > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s !important;
    }

    div[data-testid="stButton"] > button[kind="primary"] {
        background-color: var(--primary-color) !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
    }

    div[data-testid="stButton"] > button[kind="primary"]:hover {
        background-color: var(--primary-hover) !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
    }

    /* Notifications */
    .result-notif {
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 16px;
        font-weight: 500;
        font-size: 0.95rem;
    }

    .result-success {
        background-color: var(--success-bg);
        color: var(--success-text);
        border: 1px solid #bbf7d0;
    }

    .result-warning {
        background-color: var(--warning-bg);
        color: var(--warning-text);
        border: 1px solid #fde68a;
    }

    /* Dataframe styling */
    [data-testid="stDataFrame"] {
        border: 1px solid var(--border-color);
        border-radius: 8px;
        overflow: hidden;
    }

    /* Custom Metric Styling */
    .metric-container {
        display: flex;
        justify-content: space-between;
        gap: 16px;
        margin-bottom: 24px;
    }
    
    .metric-card {
        background: white;
        padding: 16px;
        border-radius: 8px;
        border: 1px solid var(--border-color);
        flex: 1;
        text-align: center;
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: 800;
        color: var(--primary-color);
    }
    
    .metric-label {
        font-size: 0.8rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# 3. HEADER & META INFO SECTION
# ==========================================
if 'saved_admin' not in st.session_state:
    st.session_state['saved_admin'] = "Admin Logistik"

with st.container():
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    
    # Layout Header yang lebih bersih
    col_h1, col_h2 = st.columns([7, 3])
    with col_h1:
        st.markdown('<h1>📦 Outbound Processor</h1>', unsafe_allow_html=True)
        st.markdown(f'<div class="meta-text">Logistics Automation Dashboard • <b>{current_date}</b></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="officer-panel">', unsafe_allow_html=True)
    col_adm1, col_adm2, col_info = st.columns([4, 2, 3])
    with col_adm1:
        st.markdown('<div style="font-size: 0.85rem; font-weight: 600; color: #475569; margin-bottom: 4px;">OFFICER AKTIF</div>', unsafe_allow_html=True)
        admin_input_temp = st.text_input("Admin", value=st.session_state['saved_admin'], label_visibility="collapsed", placeholder="Nama Officer...")
    with col_adm2:
        st.write("") 
        st.write("") 
        submit_admin = st.button("Update Nama", use_container_width=True)
    with col_info:
        st.markdown(f"""
            <div style="text-align: right; padding-top: 8px;">
                <span style="color: #64748b; font-size: 0.85rem;">Status Sistem:</span><br>
                <span style="color: #10b981; font-weight: 700; font-size: 0.9rem;">● Online & Ready</span>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if submit_admin:
        st.session_state['saved_admin'] = admin_input_temp
        st.rerun()

    current_admin = st.session_state['saved_admin']
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 4. DATA CENTER (UPLOAD SECTION) 
# ==========================================
with st.container():
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.markdown('<h3><span style="background:#eff6ff; padding:8px; border-radius:8px;">📁</span> Data Center</h3>', unsafe_allow_html=True)
    st.markdown('<div class="meta-text" style="margin-bottom: 20px;">Unggah file sumber (Order Summary, Operation Log, ERP, HO Outbound, Daily HO, Master) untuk memulai pemrosesan.</div>', unsafe_allow_html=True)

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
        if not uploaded_files:
            st.markdown("""
                <div style="text-align: center; padding: 20px; color: #94a3b8;">
                    <p style="font-size: 14px;">Belum ada file yang diunggah. Seret file ke sini atau klik untuk memilih.</p>
                </div>
            """, unsafe_allow_html=True)

    with col_up2:
        st.write("") 
        if st.button("🗑️ Reset", use_container_width=True, help="Hapus semua file dan hasil"):
            st.session_state['file_uploader_key'] += 1
            if 'processed_result' in st.session_state:
                del st.session_state['processed_result']
            if 'excel_data' in st.session_state:
                del st.session_state['excel_data']
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 5. PROCESSING QUEUE (EXECUTE SECTION)
# ==========================================
with st.container():
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.markdown('<h3><span style="background:#fef2f2; padding:8px; border-radius:8px;">⚙️</span> Processing Queue</h3>', unsafe_allow_html=True)
    
    files_ready = len(uploaded_files) > 0
    
    if files_ready:
        st.info(f"💡 {len(uploaded_files)} file terdeteksi dan siap diproses.")
    
    execute_clicked = st.button(
        "Mulai Pemrosesan Data 🚀" if files_ready else "Unggah File Terlebih Dahulu", 
        type="primary", 
        use_container_width=True,
        disabled=not files_ready
    )

    if execute_clicked:
        if uploaded_files:
            progress_bar = st.progress(0, text="Menyiapkan pemrosesan...")
            
            try:
                progress_bar.progress(10, text="Membaca file sumber... [10%]")
                dfs = {}
                master_store_db = {}
                master_carrier_db = {}
                
                for file in uploaded_files:
                    file_name = file.name.lower()
                    if file_name.endswith('.xlsx'):
                        df = pd.read_excel(file)
                    else:
                        df = pd.read_csv(file)
                    
                    df.columns = df.columns.astype(str).str.strip().str.replace('\xa0', ' ')
                    df = df.loc[:, ~df.columns.duplicated()]
                    
                    if 'master' in file_name:
                        dfs['master'] = df
                        if 'Store Number' in df.columns:
                            store_df = df[['Store Number', 'Brand', 'Brand2']].dropna(subset=['Store Number'])
                            for _, row in store_df.iterrows():
                                sn = str(row['Store Number']).strip()
                                sn = sn[:-2] if sn.endswith('.0') else sn
                                b1 = str(row['Brand']).strip() if pd.notna(row['Brand']) else ""
                                b2 = str(row['Brand2']).strip() if pd.notna(row['Brand2']) else ""
                                master_store_db[sn] = {"Brand": b1, "Brand2": b2}
                                
                        if 'carrierCode' in df.columns:
                            carrier_df = df[['carrierCode', 'Kurir']].dropna(subset=['carrierCode'])
                            for _, row in carrier_df.iterrows():
                                cc = str(row['carrierCode']).strip()
                                kur = str(row['Kurir']).strip() if pd.notna(row['Kurir']) else ""
                                master_carrier_db[cc] = kur

                    elif 'daily' in file_name:
                        dfs['daily_ho'] = df
                        
                    elif 'ho' in file_name or 'outbound' in file_name: 
                        rename_map = {}
                        for col in df.columns:
                            c_lower = col.lower()
                            if 'no wms' in c_lower: rename_map[col] = 'WMS Order'
                            elif 'expedisi' in c_lower: rename_map[col] = 'Expedisi'
                            elif c_lower == 'tanggal': rename_map[col] = 'Tgl_HO_Source'
                        df = df.rename(columns=rename_map)
                        dfs['ho_outbound'] = df
                        
                    elif 'order summary' in file_name:
                        if 'open' in file_name:
                            dfs['order_summary_open'] = df
                        if 'order_summary' not in dfs:
                            dfs['order_summary'] = df
                        elif 'open' not in file_name:
                            dfs['order_summary'] = df
                            
                    elif 'operation log' in file_name: 
                        rename_map_op = {}
                        for col in df.columns:
                            c_lower = col.lower()
                            if 'wms order' in c_lower: rename_map_op[col] = 'WMS Order#'
                            elif c_lower == 'event': rename_map_op[col] = 'Event'
                            elif c_lower == 'operator': rename_map_op[col] = 'operator'
                        df = df.rename(columns=rename_map_op)
                        dfs['op_log'] = df
                        
                    elif 'pack task' in file_name: dfs['pack_task'] = df
                    elif 'erp' in file_name: dfs['erp'] = df

                if 'ho_outbound' not in dfs:
                    st.error("❌ File 'HO Outbound' tidak ditemukan.")
                    st.stop()
                if 'order_summary' not in dfs:
                    st.error("❌ File 'Order Summary' tidak ditemukan.")
                    st.stop()

                for key in ['op_log', 'pack_task', 'erp', 'daily_ho']:
                    if key not in dfs: dfs[key] = pd.DataFrame()

                # --- TAHAP 2: Merge Data (35%) ---
                progress_bar.progress(35, text="Mencocokkan baris & Merge data... [35%]")
                df_ho = dfs['ho_outbound'].copy()
                if 'WMS Order' not in df_ho.columns:
                    st.error("❌ Kolom 'WMS Order' tidak ditemukan di file HO Outbound.")
                    st.stop()
                
                res = pd.DataFrame()
                res['WMS Order'] = df_ho['WMS Order']
                
                df_order = dfs['order_summary']
                col_order_summary = next((c for c in df_order.columns if 'order#' in c.lower()), None)
                if not df_order.empty and col_order_summary:
                    df_order = df_order.drop_duplicates(subset=[col_order_summary])
                    df_order = df_order.loc[:, ~df_order.columns.duplicated()]
                    res = res.merge(df_order, left_on='WMS Order', right_on=col_order_summary, how='left')

                col_ext_order = next((c for c in res.columns if 'ext. order#' in c.lower()), None)
                if col_ext_order:
                    res['ERP Document Number'] = res[col_ext_order].astype(str).str[:14]
                else:
                    res['ERP Document Number'] = np.nan
                
                col_track = next((c for c in res.columns if 'tracking#' in c.lower() or 'pro#' in c.lower()), None)
                col_ref = next((c for c in res.columns if 'ref#' in c.lower()), None)
                
                res['Tracking#/PRO#'] = res[col_track].apply(lambda x: str(x).strip() if pd.notna(x) and str(x).strip() != 'nan' else '') if col_track else ''
                res['PlatformOrder'] = res[col_ref].apply(lambda x: str(x).strip() if pd.notna(x) and str(x).strip() != 'nan' else '') if col_ref else ''

                col_resi_manual = next((c for c in df_ho.columns if 'resi manual' in c.lower() or 'manual resi' in c.lower()), None)
                if col_resi_manual:
                    resi_manual_vals = df_ho[col_resi_manual].apply(lambda x: str(x).strip() if pd.notna(x) and str(x).strip() != 'nan' else '')
                    res['PlatformOrder'] = np.where(resi_manual_vals != '', resi_manual_vals, res['PlatformOrder'])

                col_sales = next((c for c in res.columns if 'sales channel' in c.lower()), None)
                res['Platform'] = res[col_sales] if col_sales else np.nan
                
                plat_is_na = res['Platform'].isna() | (res['Platform'].astype(str).str.strip() == '') | (res['Platform'].astype(str).str.lower() == 'nan')
                plat_order_str = res['PlatformOrder'].astype(str).str.strip()
                
                kondisi_ck = plat_is_na & plat_order_str.str.startswith("CK")
                kondisi_kosong = plat_is_na & (plat_order_str == "")
                
                res['Platform'] = np.where(kondisi_ck, "Webstore", res['Platform'])
                res['Platform'] = np.where(kondisi_kosong, "Offline", res['Platform'])
                res['Platform'] = res['Platform'].fillna("Other")

                # Mapping Brand dari Master
                res['StoreNum_Temp'] = res['WMS Order'].astype(str).str[:5]
                res['Brand'] = res['StoreNum_Temp'].map(lambda x: master_store_db.get(x, {}).get("Brand", ""))
                res['Brand 2'] = res['StoreNum_Temp'].map(lambda x: master_store_db.get(x, {}).get("Brand2", ""))
                
                res['Admin'] = current_admin
                res['Load'] = 1
                
                col_carrier = next((c for c in res.columns if 'carrier code' in c.lower()), None)
                if col_carrier:
                    res['Kurir'] = res[col_carrier].astype(str).str.strip().map(master_carrier_db).fillna(res[col_carrier])
                else:
                    res['Kurir'] = np.nan
                
                res['Loader'] = current_admin
                res['Tanggal Handover'] = current_date
                
                col_wave = next((c for c in res.columns if 'wave id' in c.lower()), None)
                res['Wave ID'] = res[col_wave] if col_wave else np.nan

                # --- TAHAP 3: Sinkronisasi Waktu (60%) ---
                progress_bar.progress(60, text="Sinkronisasi waktu & kalkulasi SLA... [60%]")
                
                ho_col_map = {}
                for c in df_ho.columns:
                    c_low = c.lower()
                    if 'staged user' in c_low: ho_col_map['Staged User'] = c
                    elif 'handover date' in c_low: ho_col_map['Handover Date'] = c
                    elif 'logistics' in c_low: ho_col_map['Logistics'] = c
                    elif 'attachment' in c_low: ho_col_map['Attachment'] = c

                col_staged = ho_col_map.get('Staged User', None)
                res['Staged User'] = df_ho[col_staged] if col_staged else np.nan
                
                col_ho_date = ho_col_map.get('Handover Date', None)
                if col_ho_date:
                    res['Handover_Date_Raw'] = pd.to_datetime(df_ho[col_ho_date], errors='coerce')
                    res['Handover Date'] = res['Handover_Date_Raw'].dt.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    res['Handover Date'] = np.nan

                # Sinkronisasi dengan Operation Log
                df_op = dfs['op_log']
                if not df_op.empty and 'WMS Order#' in df_op.columns:
                    df_op_sorted = df_op.sort_values(by=['WMS Order#', 'Event'])
                    op_pivot = df_op_sorted.groupby(['WMS Order#', 'Event'])['operator'].first().unstack()
                    res = res.merge(op_pivot, left_on='WMS Order', right_on='WMS Order#', how='left')

                col_created = next((c for c in res.columns if 'created time' in c.lower()), None)
                col_ordered = next((c for c in res.columns if 'ordered date' in c.lower()), None)
                col_picking = next((c for c in res.columns if 'picking task created time' in c.lower()), None)
                col_released = next((c for c in res.columns if 'released date' in c.lower()), None)
                col_pack_comp = next((c for c in res.columns if 'packing complete' in c.lower()), None)
                col_shipped = next((c for c in res.columns if 'shipped date' in c.lower()), None)
                col_endship = next((c for c in res.columns if 'end ship date' in c.lower()), None)

                res['Created Time'] = res[col_created] if col_created else np.nan
                res['Ordered Date'] = res[col_ordered] if col_ordered else np.nan
                res['Picking Task Created Time'] = res[col_picking] if col_picking else np.nan
                res['pickCompletedTime - Released Date Pack'] = res[col_released] if col_released else np.nan
                res['Packing Complete'] = res[col_pack_comp] if col_pack_comp else np.nan
                res['Shipped Date'] = res[col_shipped] if col_shipped else np.nan
                res['End Ship Date'] = res[col_endship] if col_endship else np.nan

                col_logistics = ho_col_map.get('Logistics', None)
                res['Times Proses Kurir'] = df_ho[col_logistics] if col_logistics else np.nan

                is_time_empty = res['Times Proses Kurir'].isna() | (res['Times Proses Kurir'].astype(str).str.strip() == '') | (res['Times Proses Kurir'].astype(str).str.lower() == 'nan')
                is_instant_courier = res['Kurir'].astype(str).str.strip() == 'Go-Jek/Grab/Shopee Instant'
                col_shipped_temp = res['Shipped Date'] if 'Shipped Date' in res.columns else np.nan
                
                res['Times Proses Kurir'] = np.where(
                    is_time_empty & is_instant_courier,
                    col_shipped_temp,
                    res['Times Proses Kurir']
                )

                dt_format_cols = [
                    'Created Time', 'Ordered Date', 'Picking Task Created Time', 
                    'pickCompletedTime - Released Date Pack', 'Packing Complete', 
                    'Shipped Date', 'End Ship Date', 'Times Proses Kurir'
                ]
                for c in dt_format_cols:
                    if c in res.columns:
                        res[c] = pd.to_datetime(res[c], errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')
                        res[c] = res[c].replace('NaT', np.nan).fillna('')
                
                if 'Handover Date' in res.columns:
                    res['Handover Date'] = res['Handover Date'].replace('NaT', np.nan).fillna('')

                def to_dt(col_name): 
                    if col_name == 'Handover Date':
                        return res.get('Handover_Date_Raw')
                    return pd.to_datetime(res.get(col_name), errors='coerce')

                def format_timedelta_hhmmss(td_series):
                    if td_series is None: return ""
                    seconds = td_series.dt.total_seconds().fillna(0).astype(int)
                    is_neg = seconds < 0
                    seconds = abs(seconds)
                    hours = seconds // 3600
                    minutes = (seconds % 3600) // 60
                    secs = seconds % 60
                    res_str = hours.astype(str).str.zfill(2) + ":" + minutes.astype(str).str.zfill(2) + ":" + secs.astype(str).str.zfill(2)
                    res_str = np.where(is_neg, "-" + res_str, res_str)
                    return np.where(td_series.isna(), "", res_str)

                res['Packing to Shipped Date'] = format_timedelta_hhmmss(to_dt('Shipped Date') - to_dt('Packing Complete'))
                res['Packing to Handover'] = format_timedelta_hhmmss(to_dt('Handover Date') - to_dt('Packing Complete'))
                res['Shipped Date to Handover'] = format_timedelta_hhmmss(to_dt('Handover Date') - to_dt('Shipped Date'))
                res['End Ship Date to Shpped Date'] = format_timedelta_hhmmss(to_dt('End Ship Date') - to_dt('Shipped Date'))

                col_city = next((c for c in res.columns if 'ship to city' in c.lower()), None)
                col_prov = next((c for c in res.columns if 'ship to st' in c.lower() or 'prov' in c.lower()), None)
                res['Kota'] = res[col_city] if col_city else np.nan
                res['Provinsi'] = res[col_prov] if col_prov else np.nan

                df_erp = dfs['erp']
                col_erp_order = next((c for c in df_erp.columns if 'erp order number' in c.lower()), None) if not df_erp.empty else None
                if col_erp_order and 'ERP Document Number' in res.columns:
                    df_erp = df_erp.drop_duplicates(subset=[col_erp_order])
                    df_erp = df_erp.loc[:, ~df_erp.columns.duplicated()]
                    
                    col_status = next((c for c in df_erp.columns if 'online status' in c.lower()), None)
                    col_payment = next((c for c in df_erp.columns if 'payment method' in c.lower()), None)
                    col_amount = next((c for c in df_erp.columns if 'total order amount' in c.lower()), None)
                    
                    cols_erp_merge = [col_erp_order]
                    if col_status: cols_erp_merge.append(col_status)
                    if col_payment: cols_erp_merge.append(col_payment)
                    if col_amount: cols_erp_merge.append(col_amount)
                    
                    res_erp_m = res[['ERP Document Number']].merge(df_erp[cols_erp_merge], left_on='ERP Document Number', right_on=col_erp_order, how='left')
                    res['Status'] = res_erp_m[col_status] if col_status else np.nan
                    res['total order amount'] = res_erp_m[col_amount] if col_amount else np.nan
                    
                    def map_payment(x):
                        x_str = str(x).strip().lower()
                        if x_str in ['在线支付', 'nan', 'none', '']: return 'Non COD'
                        return 'COD'
                        
                    if col_payment:
                        res['Payment Menthood'] = res_erp_m[col_payment].apply(map_payment)
                    else:
                        res['Payment Menthood'] = 'Non COD'
                else:
                    res['Status'] = np.nan; res['total order amount'] = np.nan; res['Payment Menthood'] = 'Non COD'

                res['Status'] = res['Status'].apply(lambda x: 'Other' if pd.isna(x) or str(x).strip() in ['', 'nan', 'None'] else x)

                col_attach = ho_col_map.get('Attachment', None)
                res['Attachment'] = df_ho[col_attach].apply(lambda x: str(x).strip() if pd.notna(x) else '') if col_attach else np.nan
                is_no_attach = res['Attachment'].replace({0: np.nan, '0': np.nan, '': np.nan}).isna()
                res['Dokumen'] = np.where(is_no_attach, 'Not yet Input', 'YES')

                res['Times Proses Kurir to Shpped Date'] = format_timedelta_hhmmss(to_dt('Times Proses Kurir') - to_dt('Shipped Date'))

                plat_cond = res.get('Platform', pd.Series(['']*len(res))).astype(str).str.lower().isin(['shopee', 'tiktok'])
                ai_val = to_dt('Times Proses Kurir')
                w_val = to_dt('End Ship Date')
                
                res['Status Manifest'] = np.where(
                    ai_val.isna() | w_val.isna(), "",
                    np.where(plat_cond, np.where(ai_val > w_val, "Late", "On Time"), "On Time")
                )

                res['Status Late'] = np.nan; res['Remark Late'] = np.nan

                res['Pay-Created'] = format_timedelta_hhmmss(to_dt('Created Time') - to_dt('Ordered Date'))
                res['Created-Released'] = format_timedelta_hhmmss(to_dt('Picking Task Created Time') - to_dt('Created Time'))
                res['Released-Pick'] = format_timedelta_hhmmss(to_dt('pickCompletedTime - Released Date Pack') - to_dt('Picking Task Created Time'))
                res['Pick-Pack'] = format_timedelta_hhmmss(to_dt('Packing Complete') - to_dt('pickCompletedTime - Released Date Pack'))
                res['Pack-Collect'] = format_timedelta_hhmmss(to_dt('Shipped Date') - to_dt('Packing Complete'))
                res['Collect-Manifest'] = format_timedelta_hhmmss(to_dt('Times Proses Kurir') - to_dt('Shipped Date'))
                res['Manifest-Endshipdate'] = format_timedelta_hhmmss(to_dt('End Ship Date') - to_dt('Times Proses Kurir'))

                def get_safe_seconds(td_str_series):
                    sec_list = []
                    for val in td_str_series:
                        if pd.isna(val) or str(val).strip() == '' or str(val).strip() == 'NaT':
                            sec_list.append(0.0)
                            continue
                        val_str = str(val).strip()
                        sign = -1 if val_str.startswith('-') else 1
                        clean = val_str.replace('-', '')
                        parts = clean.split(':')
                        try:
                            if len(parts) == 3:
                                h = float(parts[0]) if parts[0] != '' else 0.0
                                m = float(parts[1]) if parts[1] != '' else 0.0
                                s = float(parts[2]) if parts[2] != '' else 0.0
                                sec_list.append(sign * (h * 3600 + m * 60 + s))
                            else:
                                sec_list.append(0.0)
                        except:
                            sec_list.append(0.0)
                    return pd.Series(sec_list)

                cols_sla_str = ['Pay-Created', 'Created-Released', 'Released-Pick', 'Pick-Pack', 'Pack-Collect', 'Collect-Manifest', 'Manifest-Endshipdate']
                df_sec = pd.DataFrame({col: get_safe_seconds(res[col]) for col in cols_sla_str})

                res['System'] = np.nan
                res['Admin_Akhir'] = np.nan
                res['Picker'] = np.nan
                res['Packer'] = np.nan
                res['Outbound'] = np.nan
                res['Kurir_Akhir'] = np.nan
                res['Late Proses By'] = np.nan
                
                # --- TAHAP 4: Menyusun Kolom Final ---
                progress_bar.progress(90, text="Menyusun laporan akhir... [90%]")
                kolom_final = [
                    'WMS Order', 'ERP Document Number', 'Tracking#/PRO#', 'PlatformOrder', 'Staged User', 
                    'Platform', 'Brand', 'Brand 2', 'Admin', 'Load', 'Kurir', 'Loader', 'Tanggal Handover', 
                    'Wave ID', 'Created Time', 'Ordered Date', 'Picking Task Created Time', 
                    'pickCompletedTime - Released Date Pack', 'Packing Complete', 'Shipped Date', 'Handover Date', 
                    'End Ship Date', 'Packing to Shipped Date', 'Packing to Handover', 'Shipped Date to Handover', 
                    'End Ship Date to Shpped Date', 'Kota', 'Provinsi', 'Status', 'Payment Menthood', 
                    'total order amount', 'Dokumen', 'Attachment', 'Times Proses Kurir', 'Times Proses Kurir to Shpped Date', 
                    'Status Manifest', 'Status Late', 'Remark Late', 'Pay-Created', 'Created-Released', 'Released-Pick', 
                    'Pick-Pack', 'Pack-Collect', 'Collect-Manifest', 'Manifest-Endshipdate', 'Max', 'System', 'Admin_Akhir', 
                    'Picker', 'Packer', 'Outbound', 'Kurir_Akhir', 'Late Proses Data Dummy', 'Late Proses By'
                ]
                
                for col in kolom_final:
                    if col not in res.columns: res[col] = np.nan
                final_df = res[kolom_final].copy()

                final_df = final_df.rename(columns={'Admin_Akhir': 'Admin', 'Kurir_Akhir': 'Kurir'})
                final_df = final_df.drop(columns=['Late Proses Data Dummy'], errors='ignore')
                final_df = final_df.loc[:, ~final_df.columns.duplicated()]

                master_df = dfs.get('master', pd.DataFrame())
                master_status_col = next((c for c in master_df.columns if 'online status' in c.lower() or c.lower() == 'status'), None)
                master_track_col = next((c for c in master_df.columns if 'tracking' in c.lower()), None)
                
                master_track_dict = {}
                if master_status_col and master_track_col:
                    for _, row in master_df.iterrows():
                        st_val = str(row[master_status_col]).strip().lower()
                        tr_val = str(row[master_track_col]).strip().lower()
                        if st_val and pd.notna(row[master_track_col]):
                            master_track_dict[st_val] = tr_val

                final_df['Master_Tracking'] = final_df['Status'].astype(str).str.strip().str.lower().map(master_track_dict).fillna('untraceable')

                final_df.insert(0, 'No', range(1, len(final_df) + 1))
                st.session_state['processed_result'] = final_df

                # Excel Generation
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_to_export = final_df.drop(columns=['Master_Tracking'], errors='ignore')
                    df_to_export.to_excel(writer, index=False, sheet_name='Laporan_WMS')
                    
                    workbook = writer.book
                    worksheet_wms = writer.sheets['Laporan_WMS']
                    format_header = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3', 'border': 1})
                    
                    col_idx_track = list(df_to_export.columns).index('Tracking#/PRO#')
                    col_idx_plat = list(df_to_export.columns).index('PlatformOrder')
                    
                    for row_num in range(len(df_to_export)):
                        val_track = str(df_to_export.iloc[row_num]['Tracking#/PRO#'])
                        val_plat = str(df_to_export.iloc[row_num]['PlatformOrder'])
                        
                        if val_track != 'nan' and val_track != '':
                            worksheet_wms.write_string(row_num + 1, col_idx_track, val_track)
                        if val_plat != 'nan' and val_plat != '':
                            worksheet_wms.write_string(row_num + 1, col_idx_plat, val_plat)

                        excel_row = row_num + 2
                        worksheet_wms.write_formula(row_num + 1, 46, f"=MAX(AN{excel_row}:AT{excel_row})")
                        worksheet_wms.write_formula(row_num + 1, 47, f"=AU{excel_row}=AN{excel_row}")
                        worksheet_wms.write_formula(row_num + 1, 48, f"=AU{excel_row}=AO{excel_row}")
                        worksheet_wms.write_formula(row_num + 1, 49, f"=AU{excel_row}=AP{excel_row}")
                        worksheet_wms.write_formula(row_num + 1, 50, f"=AU{excel_row}=AQ{excel_row}")
                        worksheet_wms.write_formula(row_num + 1, 51, f"=AU{excel_row}=AR{excel_row}")
                        worksheet_wms.write_formula(row_num + 1, 52, f"=AU{excel_row}=AS{excel_row}")
                        
                        formula_late_by = (
                            f'=IF(AV{excel_row}, "System", '
                            f'IF(AW{excel_row}, "Admin", '
                            f'IF(AX{excel_row}, "Picker", '
                            f'IF(AY{excel_row}, "Packer", '
                            f'IF(AZ{excel_row}, "Outbound", '
                            f'IF(BA{excel_row}, "Kurir", ""))))))'
                        )
                        worksheet_wms.write_formula(row_num + 1, 53, formula_late_by)

                    for col_num, value in enumerate(df_to_export.columns.values):
                        worksheet_wms.write(0, col_num, value, format_header)
                        worksheet_wms.set_column(col_num, col_num, 16)

                    # SHEET DB
                    worksheet_db = workbook.add_worksheet('DB')
                    header_format_db = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3', 'border': 1, 'align': 'center'})
                    cell_format_db = workbook.add_format({'border': 1, 'align': 'center'})
                    cell_format_left = workbook.add_format({'border': 1, 'align': 'left'})
                    black_divider = workbook.add_format({'bg_color': '#000000'})

                    df_brand = final_df.groupby(['Brand', 'Brand 2']).size().reset_index(name='Total')
                    df_kurir = final_df.groupby('Kurir').size().reset_index(name='Total')
                    df_status = final_df.groupby('Status').size().reset_index(name='Total')
                    df_kurir_manifest = final_df.groupby(['Kurir', 'Status Manifest']).size().reset_index(name='Total')

                    raw_daily_df = dfs.get('daily_ho', pd.DataFrame())
                    val_delivery_rate = "0%"
                    val_delivered = len(final_df)
                    val_target = 0
                    val_pending = 0

                    df_order_open = dfs.get('order_summary_open', pd.DataFrame())
                    col_ref_open = next((c for c in df_order_open.columns if 'ref#' in c.lower()), None)
                    if col_ref_open:
                        val_target = df_order_open[col_ref_open].nunique()
                    
                    if val_target > 0:
                        val_delivery_rate = f"{round((val_delivered / val_target) * 100, 2)}%"

                    if not raw_daily_df.empty:
                        col_pending = next((c for c in raw_daily_df.columns if 'pending' in c.lower() and 'qty' in c.lower()), None)
                        if col_pending:
                            val_pending = int(pd.to_numeric(raw_daily_df[col_pending].astype(str).str.replace(r'[^\d.-]', '', regex=True), errors='coerce').fillna(0).sum())

                    val_kurir_instan = 0
                    col_kurir_d = next((c for c in raw_daily_df.columns if any(k in c.lower() for k in ['kurir', 'carrier', 'expedisi', 'ekspedisi', 'logistics'])), None)
                    col_qty_d = next((c for c in raw_daily_df.columns if 'qty' in c.lower() and 'pending' not in c.lower()), None)

                    if col_kurir_d and col_qty_d and not raw_daily_df.empty:
                        courier_series = raw_daily_df[col_kurir_d].astype(str).str.lower()
                        qty_series = pd.to_numeric(raw_daily_df[col_qty_d].astype(str).str.replace(r'[^\d.-]', '', regex=True), errors='coerce').fillna(0)
                        pattern = r'(?i)instant|instan|sameday|same day|gojek|go-jek|grab|gosend|paxel|deliveree'
                        mask_instan = courier_series.str.contains(pattern, regex=True, na=False)
                        val_kurir_instan = int(qty_series[mask_instan].sum())

                    def get_avg_time_str(series_hhmmss):
                        if series_hhmmss is None or series_hhmmss.empty: return "0:00:00"
                        secs = get_safe_seconds(series_hhmmss)
                        valid_secs = secs[secs > 0]
                        if len(valid_secs) > 0:
                            mean_sec = int(valid_secs.mean())
                            h = mean_sec // 3600
                            m = (mean_sec % 3600) // 60
                            s = mean_sec % 60
                            return f"{h}:{m:02d}:{s:02d}"
                        return "0:00:00"

                    val_avg_shipped = get_avg_time_str(final_df['Packing to Shipped Date']) if 'Packing to Shipped Date' in final_df.columns else "0:00:00"
                    val_avg_handover = get_avg_time_str(final_df['Shipped Date to Handover']) if 'Shipped Date to Handover' in final_df.columns else "0:00:00"

                    def lookup_kondisi_rule(row):
                        b1 = str(row.get('Brand', '')).strip().upper()
                        b2 = str(row.get('Brand 2', '')).strip().upper()
                        p = str(row.get('Platform', '')).strip().upper()
                        b_combined = (b1 + " " + b2).replace("'", "").replace(" ", "")
                        if 'WEBSTORE' in p and 'ACEKID' in b_combined: return 'other'
                        if b1 == 'SK' or b2 == 'SK': return 'other'
                        if p == 'OTHER' and any(x in b2 for x in ['DOJAKO', 'FIRDA', 'MAMASCHOICE', 'NOURA']): return 'jc_fulfilment'
                        fulfilment_brands = ['DOJAKO', 'FIRDA', 'NOURA', 'MAMASCHOICE']
                        for fb in fulfilment_brands:
                            if fb in b_combined: return 'jc_fulfilment'
                        return 'jc_enabler'

                    final_df['Master_Category'] = final_df.apply(lookup_kondisi_rule, axis=1)
                    val_jc_enabler = int((final_df['Master_Category'] == 'jc_enabler').sum())
                    val_jc_fulfilment = int((final_df['Master_Category'] == 'jc_fulfilment').sum())
                    val_other = int((final_df['Master_Category'] == 'other').sum())
                    val_traceable = int(final_df['Master_Tracking'].eq('traceable').sum())
                    val_untraceable = int(final_df['Master_Tracking'].eq('untraceable').sum())

                    metrics_data = [
                        [1, "delivery_rate", val_delivery_rate, "Persentase delivery rate"],
                        [2, "delivered", f"{val_delivered:,}", "Total order di sheet Laporan_WMS"],
                        [3, "target", f"{val_target:,}", "Count unique Ref# dari file Order Summary Export OPEN"],
                        [4, "pending_order", f"{val_pending:,}", "Total qty di kolom Pending Cut Off Qty file Daily HO"],
                        [5, "avg_shipped", val_avg_shipped, "AVG Laporan_WMS Packing to Shipped Date"],
                        [6, "avg_handover", val_avg_handover, "AVG Laporan_WMS Shipped Date to Handover"],
                        [7, "kurir_instan", f"{val_kurir_instan:,}", "Total Deliveree Qty kriteria kurir instan"],
                        [8, "jc_enabler", f"{val_jc_enabler:,}", "Kondisi Rule: Jet Commerce Enabler"],
                        [9, "jc_fulfilment", f"{val_jc_fulfilment:,}", "Kondisi Rule: Jet Commerce Fulfillment Center / Service"],
                        [10, "other", f"{val_other:,}", "Kondisi Rule: Other"],
                        [11, "traceable", f"{val_traceable:,}", "Lookup Status: Paket traceable"],
                        [12, "untraceable", f"{val_untraceable:,}", "Lookup Status: Paket untraceable"],
                    ]
                    df_metrics = pd.DataFrame(metrics_data, columns=["No", "Metric_Name", "Value", "Description"])
                    
                    def write_custom_table(df_table, start_row, start_col):
                        for c_idx, col_name in enumerate(df_table.columns):
                            worksheet_db.write(start_row, start_col + c_idx, col_name, header_format_db)
                        for r_idx, row in enumerate(df_table.values):
                            for c_idx, val in enumerate(row):
                                fmt = cell_format_left if isinstance(val, str) else cell_format_db
                                worksheet_db.write(start_row + r_idx + 1, start_col + c_idx, val, fmt)

                    write_custom_table(df_metrics, 1, 0)          
                    write_custom_table(df_brand, 1, 5)            
                    write_custom_table(df_kurir, 1, 11)           
                    write_custom_table(df_status, 1, 20)          
                    write_custom_table(df_kurir_manifest, 1, 25)  
                    
                    worksheet_db.set_column('E:E', 2, black_divider)
                    worksheet_db.set_column('K:K', 2, black_divider)
                    worksheet_db.set_column('Q:Q', 2, black_divider)
                    worksheet_db.set_column('T:T', 2, black_divider)
                    worksheet_db.set_column('Y:Y', 2, black_divider)
                    worksheet_db.set_column('A:A', 5); worksheet_db.set_column('B:B', 18); worksheet_db.set_column('C:C', 12); worksheet_db.set_column('D:D', 35)
                    worksheet_db.set_column('F:F', 5); worksheet_db.set_column('G:G', 18); worksheet_db.set_column('H:I', 12)
                    worksheet_db.set_column('L:L', 5); worksheet_db.set_column('M:M', 25); worksheet_db.set_column('N:O', 15)
                    worksheet_db.set_column('U:U', 5); worksheet_db.set_column('V:V', 15); worksheet_db.set_column('W:W', 10)
                    worksheet_db.set_column('Z:Z', 5); worksheet_db.set_column('AA:AA', 25); worksheet_db.set_column('AB:AB', 25)

                st.session_state['excel_data'] = output.getvalue()
                st.session_state['summary_metrics'] = {
                    "Total Delivered": f"{val_delivered:,}",
                    "Delivery Rate": val_delivery_rate,
                    "Target Order": f"{val_target:,}",
                    "Untraceable": f"{val_untraceable:,}"
                }
                
                progress_bar.progress(100, text="Processing Selesai! (100%)")
                progress_bar.empty()

            except Exception as e:
                st.error(f"❌ Terjadi kesalahan Sistem: {e}")
                st.code(traceback.format_exc())
        else:
            st.warning("Silakan unggah file sumber terlebih dahulu di area Data Center.")

    st.write("")
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 6. TAMPILAN PREVIEW & NOTIFIKASI
# ==========================================
if 'processed_result' in st.session_state:
    res_df = st.session_state['processed_result']
    metrics = st.session_state.get('summary_metrics', {})
    
    with st.container():
        st.markdown('<div class="modern-card">', unsafe_allow_html=True)
        st.markdown('<h3><span style="background:#f0fdf4; padding:8px; border-radius:8px;">📊</span> Summary Dashboard</h3>', unsafe_allow_html=True)

        # Metric Cards
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        with m_col1:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Delivered</div><div class="metric-value">{metrics.get("Total Delivered", "0")}</div></div>', unsafe_allow_html=True)
        with m_col2:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Delivery Rate</div><div class="metric-value">{metrics.get("Delivery Rate", "0%")}</div></div>', unsafe_allow_html=True)
        with m_col3:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Target Order</div><div class="metric-value">{metrics.get("Target Order", "0")}</div></div>', unsafe_allow_html=True)
        with m_col4:
            color = "#ef4444" if int(metrics.get("Untraceable", "0").replace(",", "")) > 0 else "#2563eb"
            st.markdown(f'<div class="metric-card"><div class="metric-label">Untraceable</div><div class="metric-value" style="color: {color};">{metrics.get("Untraceable", "0")}</div></div>', unsafe_allow_html=True)

        st.markdown(f"""
            <div class="result-notif result-success">
                ✅ Berhasil memproses total <b>{len(res_df):,}</b> baris data! Laporan siap diunduh.
            </div>
        """, unsafe_allow_html=True)

        if 'Master_Tracking' in res_df.columns:
            untraceable_data = res_df[res_df['Master_Tracking'] == 'untraceable']
            untraceable_count = len(untraceable_data)
            
            if untraceable_count > 0:
                st.markdown(f"""
                    <div class="result-notif result-warning">
                        ⚠️ <b>PERINGATAN DATA UNTRACEABLE:</b> Ditemukan <b>{untraceable_count}</b> paket dengan status Untraceable!
                    </div>
                """, unsafe_allow_html=True)
                
                with st.expander("🔍 Detail Data Untraceable", expanded=False):
                    col_u1, col_u2 = st.columns([1, 2])
                    with col_u1:
                        st.markdown("**Ringkasan per Status:**")
                        status_summary = untraceable_data['Status'].value_counts().reset_index()
                        status_summary.columns = ['Status', 'Jumlah Paket']
                        st.dataframe(status_summary, use_container_width=True, hide_index=True)
                    with col_u2:
                        st.markdown("**Detail Paket:**")
                        cols_to_show = [c for c in ['No', 'WMS Order', 'ERP Document Number', 'Platform', 'Kurir', 'Status', 'Tracking#/PRO#'] if c in untraceable_data.columns]
                        st.dataframe(untraceable_data[cols_to_show], use_container_width=True, hide_index=True)
            else:
                st.info("🎉 Seluruh paket berstatus **Traceable** (0 Untraceable).")

        st.markdown("##### Pratinjau Seluruh Data:")
        display_df = res_df.drop(columns=['Master_Tracking'], errors='ignore')
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        st.write("")
        col_down1, col_down2, col_down3 = st.columns([1, 2, 1])
        with col_down2:
            st.download_button(
                label="📥 Download Laporan Excel (.xlsx)",
                data=st.session_state['excel_data'],
                file_name="Laporan_Daily_HO_Outbound.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                use_container_width=True
            )

        st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
    <div style="text-align: center; padding: 20px; color: #94a3b8; font-size: 0.8rem;">
        Logistics Outbound Auto-Processor v2.0 • Build with ❤️ for Efficiency
    </div>
""", unsafe_allow_html=True)
