import streamlit as st
import pandas as pd
import numpy as np
import traceback
import datetime
import altair as alt
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
# 2. CSS KUSTOM (Menghilangkan Sidebar & Badge Pojok Kanan Bawah Secara Total)
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
        margin-bottom: 20px;
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
       SEMBUNYIKAN MENU BALON & BADGE POJOK KANAN BAWAH
       ========================================== */
    #MainMenu { visibility: hidden !important; display: none !important; }
    footer { visibility: hidden !important; display: none !important; }
    header { visibility: hidden !important; display: none !important; }
    .stDeployButton { visibility: hidden !important; display: none !important; }
    [data-testid="stToolbar"] { visibility: hidden !important; display: none !important; }
    [data-testid="stDecoration"] { visibility: hidden !important; display: none !important; }
    [data-testid="stStatusWidget"] { visibility: hidden !important; display: none !important; }
    div.viewerBadge_container__1QSob { visibility: hidden !important; display: none !important; }
    .viewerBadge { visibility: hidden !important; display: none !important; }
    iframe[title="streamlitApp"] { display: none !important; }
    
    /* Paksa elemen fixed di pojok kanan bawah agar hilang */
    div:has(> iframe), footer + div, .reportview-container .main footer, div[class*="viewerBadge"] {
        display: none !important;
        visibility: hidden !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# 3. TOP BAR & DATA CENTER (UPLOAD + INPUT OFFICER)
# ==========================================
st.markdown(f"""
    <div class="top-bar">
        <div style="font-weight: 700; color: #1890FF; font-size: 16px;">📦 Outbound Logis - Automated Data Processing</div>
        <div style="font-size: 13px; color: #8C8C8C;">Update time: {current_date_time} <span style="color: #1890FF; margin-left: 10px; font-weight: 600;">Active 🔄</span></div>
    </div>
""", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📁 Data Center & Konfigurasi Officer</div>', unsafe_allow_html=True)
    
    if 'saved_admin' not in st.session_state:
        st.session_state['saved_admin'] = "Admin Logistik"
    
    col_off1, col_off2, col_off3 = st.columns([3, 1, 1])
    with col_off1:
        admin_input = st.text_input("✍️ Input Officer Name", value=st.session_state['saved_admin'])
    with col_off2:
        st.write("")
        if st.button("Update Nama", use_container_width=True, type="secondary"):
            st.session_state['saved_admin'] = admin_input
            st.success("Nama diperbarui!")
            st.rerun()
    with col_off3:
        st.write("")
        if st.button("🗑️ Reset Cache", use_container_width=True, type="secondary"):
            if 'file_uploader_key' not in st.session_state: st.session_state['file_uploader_key'] = 0
            st.session_state['file_uploader_key'] += 1
            for k in ['processed_result', 'excel_data', 'metrics']:
                if k in st.session_state: del st.session_state[k]
            st.rerun()

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
                res['Tracking#/PRO#'] = res[col_track].apply(lambda x: str(x).strip() if pd.notna(x) and str(x).strip() != 'nan' else '') if col_track else ''
                res['PlatformOrder'] = res[col_ref].apply(lambda x: str(x).strip() if pd.notna(x) and str(x).strip() != 'nan' else '') if col_ref else ''

                col_resi_manual = next((c for c in df_ho.columns if 'resi manual' in c.lower() or 'manual resi' in c.lower()), None)
                if col_resi_manual:
                    resi_manual_vals = df_ho[col_resi_manual].apply(lambda x: str(x).strip() if pd.notna(x) and str(x).strip() != 'nan' else '')
                    res['Tracking#/PRO#'] = np.where(resi_manual_vals != '', resi_manual_vals, res['Tracking#/PRO#'])

                col_sales = next((c for c in res.columns if 'sales channel' in c.lower()), None)
                res['Platform'] = res[col_sales] if col_sales else np.nan
                
                plat_is_na = res['Platform'].isna() | (res['Platform'].astype(str).str.strip() == '') | (res['Platform'].astype(str).str.lower() == 'nan')
                plat_order_str = res['PlatformOrder'].astype(str).str.strip()
                kondisi_ck = plat_is_na & plat_order_str.str.startswith("CK")
                kondisi_kosong = plat_is_na & (plat_order_str == "")
                res['Platform'] = np.where(kondisi_ck | kondisi_kosong, "Other", np.where(plat_is_na, "Webstore", res['Platform']))
                res['Platform'] = np.where(res['Platform'].astype(str).str.strip().str.lower() == 'independent', 'Other', res['Platform'])

                is_platform_other = res['Platform'].astype(str).str.strip() == 'Other'
                erp_empty = res['ERP Document Number'].isna() | (res['ERP Document Number'].astype(str).str.strip() == '') | (res['ERP Document Number'].astype(str).str.lower() == 'nan')
                res['ERP Document Number'] = np.where(erp_empty & is_platform_other, res['WMS Order'], res['ERP Document Number'])

                track_empty = res['Tracking#/PRO#'].isna() | (res['Tracking#/PRO#'].astype(str).str.strip() == '') | (res['Tracking#/PRO#'].astype(str).str.lower() == 'nan')
                res['Tracking#/PRO#'] = np.where(track_empty & is_platform_other, res['WMS Order'], res['Tracking#/PRO#'])

                platord_empty = res['PlatformOrder'].isna() | (res['PlatformOrder'].astype(str).str.strip() == '') | (res['PlatformOrder'].astype(str).str.lower() == 'nan')
                res['PlatformOrder'] = np.where(platord_empty & is_platform_other, res['WMS Order'], res['PlatformOrder'])

                df_op = dfs['op_log']
                if not df_op.empty and 'Event' in df_op.columns and 'WMS Order#' in df_op.columns and 'operator' in df_op.columns:
                    ev_col = df_op['Event'].iloc[:, 0] if isinstance(df_op['Event'], pd.DataFrame) else df_op['Event']
                    op_col = df_op['operator'].iloc[:, 0] if isinstance(df_op['operator'], pd.DataFrame) else df_op['operator']
                    wms_op_col = df_op['WMS Order#'].iloc[:, 0] if isinstance(df_op['WMS Order#'], pd.DataFrame) else df_op['WMS Order#']
                    df_clean_op = pd.DataFrame({'WMS Order#': wms_op_col, 'Event': ev_col.astype(str).str.strip().str.lower(), 'operator': op_col})
                    ship_logs = df_clean_op[df_clean_op['Event'] == 'ship'].drop_duplicates(subset=['WMS Order#'])
                    res_temp = res[['WMS Order']].merge(ship_logs[['WMS Order#', 'operator']], left_on='WMS Order', right_on='WMS Order#', how='left')
                    res['Staged User'] = res_temp['operator']
                else:
                    res['Staged User'] = np.nan

                col_pic_ho = next((c for c in df_ho.columns if 'pic hand over' in c.lower()), None)
                if col_pic_ho:
                    staged_empty = res['Staged User'].isna() | (res['Staged User'].astype(str).str.strip() == '') | (res['Staged User'].astype(str).str.lower() == 'nan')
                    res['Staged User'] = np.where(staged_empty, df_ho[col_pic_ho], res['Staged User'])

                def safe_key(x):
                    if pd.isna(x): return ""
                    s = str(x).strip()
                    if s.lower() in ['', 'nan', 'none', 'null', '0']: return ""
                    return s[:-2] if s.endswith('.0') else s

                col_store = next((c for c in res.columns if 'store number' in c.lower()), None)
                res['Store number'] = res[col_store] if col_store else np.nan
                if 'Store number' in res.columns:
                    res['Brand'] = res['Store number'].apply(safe_key).map(lambda x: master_store_db.get(x, {}).get('Brand', np.nan))
                    res['Brand 2'] = res['Store number'].apply(safe_key).map(lambda x: master_store_db.get(x, {}).get('Brand2', np.nan))
                else:
                    res['Brand'] = np.nan; res['Brand 2'] = np.nan
                
                brand_is_na = res['Brand'].isna() | (res['Brand'].astype(str).str.strip() == '') | (res['Brand'].astype(str).str.lower() == 'nan')
                brand2_is_na = res['Brand 2'].isna() | (res['Brand 2'].astype(str).str.strip() == '') | (res['Brand 2'].astype(str).str.lower() == 'nan')
                res['Brand'] = np.where(brand_is_na & is_platform_other, "SK", np.where(brand_is_na, "AceKid", res['Brand']))
                res['Brand 2'] = np.where(brand2_is_na & is_platform_other, "SK", np.where(brand2_is_na, "AceKid", res['Brand 2']))

                res['Admin'] = st.session_state['saved_admin']

                progress_bar.progress(70, text="Processing... (Kalkulasi selisih waktu & SLA) [70%]")
                ho_col_map = {}
                for c in df_ho.columns:
                    c_low = c.lower()
                    if 'no load' in c_low: ho_col_map['Load'] = c
                    elif 'tgl_ho_source' in c_low: ho_col_map['Tgl_HO'] = c
                    elif 'pic hand over' in c_low and 'tanggal' not in c_low: ho_col_map['Loader'] = c
                    elif 'time handover' in c_low: ho_col_map['Waktu_HO'] = c
                    elif 'attachment' in c_low: ho_col_map['Attachment'] = c
                    elif 'logistics stage' in c_low: ho_col_map['Logistics'] = c
                    elif 'expedisi' in c_low: ho_col_map['Expedisi'] = c

                res['Load'] = df_ho[ho_col_map['Load']] if 'Load' in ho_col_map else np.nan
                res['Loader'] = df_ho[ho_col_map['Loader']] if 'Loader' in ho_col_map else np.nan
                
                if 'Tgl_HO' in ho_col_map:
                    raw_tgl_ho = df_ho[ho_col_map['Tgl_HO']].apply(lambda val: f"{val.month:02d}/{val.day:02d}/{val.year}" if isinstance(val, datetime.datetime) else str(val))
                    res['Tanggal Handover'] = pd.to_datetime(raw_tgl_ho, errors='coerce', dayfirst=True).dt.strftime('%m/%d/%Y')
                else:
                    res['Tanggal Handover'] = np.nan
                
                res['Kurir'] = df_ho[ho_col_map['Expedisi']].apply(safe_key).map(lambda x: master_carrier_db.get(x, x)) if 'Expedisi' in ho_col_map else np.nan

                col_wave = next((c for c in res.columns if c.lower() == 'wave' or 'wave id' in c.lower()), None)
                col_created = next((c for c in res.columns if 'created date' in c.lower() and 'wave' not in c.lower() and 'picking' not in c.lower()), None)
                col_ordered = next((c for c in res.columns if 'ordered date' in c.lower()), None)
                col_pick_created = next((c for c in res.columns if 'picking task created' in c.lower()), None)

                res['Wave ID'] = res[col_wave] if col_wave else np.nan
                res['Created Time'] = res[col_created] if col_created else np.nan
                res['Ordered Date'] = res[col_ordered] if col_ordered else np.nan
                
                if col_pick_created:
                    res['Picking Task Created Time'] = res[col_pick_created].apply(lambda x: str(x).strip().split(',')[-1].strip() if pd.notna(x) and ',' in str(x) else str(x).strip() if pd.notna(x) else np.nan)
                else:
                    res['Picking Task Created Time'] = np.nan

                df_pack = dfs['pack_task']
                col_pack_order = next((c for c in df_pack.columns if 'order#' in c.lower()), None) if not df_pack.empty else None
                if col_pack_order:
                    df_pack = df_pack.drop_duplicates(subset=[col_pack_order]).loc[:, ~df_pack.columns.duplicated()]
                    col_released = next((c for c in df_pack.columns if 'released date' in c.lower()), None)
                    col_close = next((c for c in df_pack.columns if 'close date' in c.lower()), None)
                    cols_pack_merge = [col_pack_order]
                    if col_released: cols_pack_merge.append(col_released)
                    if col_close: cols_pack_merge.append(col_close)
                    res_pack_m = res[['WMS Order']].merge(df_pack[cols_pack_merge], left_on='WMS Order', right_on=col_pack_order, how='left')
                    res['pickCompletedTime - Released Date Pack'] = res_pack_m[col_released] if col_released else np.nan
                    res['Packing Complete'] = res_pack_m[col_close] if col_close else np.nan
                else:
                    res['pickCompletedTime - Released Date Pack'] = np.nan; res['Packing Complete'] = np.nan

                res['Shipped Date'] = res[next((c for c in res.columns if 'shipped date' in c.lower()), None)] if next((c for c in res.columns if 'shipped date' in c.lower()), None) else np.nan
                
                if 'Waktu_HO' in ho_col_map:
                    def safe_ho_parse(val):
                        if pd.isna(val): return pd.NaT
                        if isinstance(val, (int, float)):
                            try: return pd.to_datetime('1899-12-30') + pd.to_timedelta(val, unit='D')
                            except: return pd.NaT
                        if isinstance(val, datetime.datetime): return val
                        return pd.to_datetime(val, errors='coerce')
                    
                    parsed_ho = df_ho[ho_col_map['Waktu_HO']].apply(safe_ho_parse)
                    res['Handover Date'] = parsed_ho.dt.strftime('%Y-%m-%d %H:%M:%S').replace('NaT', np.nan).fillna('')
                    res['Handover_Date_Raw'] = parsed_ho
                else:
                    res['Handover Date'] = np.nan; res['Handover_Date_Raw'] = pd.NaT

                res['End Ship Date'] = res[next((c for c in res.columns if 'end ship date' in c.lower()), None)] if next((c for c in res.columns if 'end ship date' in c.lower()), None) else np.nan
                res['Times Proses Kurir'] = df_ho[ho_col_map.get('Logistics', None)] if ho_col_map.get('Logistics', None) else np.nan

                is_time_empty = res['Times Proses Kurir'].isna() | (res['Times Proses Kurir'].astype(str).str.strip() == '') | (res['Times Proses Kurir'].astype(str).str.lower() == 'nan')
                res['Times Proses Kurir'] = np.where(is_time_empty & (res['Kurir'].astype(str).str.strip() == 'Go-Jek/Grab/Shopee Instant'), res['Shipped Date'], res['Times Proses Kurir'])

                for c in ['Created Time', 'Ordered Date', 'Picking Task Created Time', 'pickCompletedTime - Released Date Pack', 'Packing Complete', 'Shipped Date', 'End Ship Date', 'Times Proses Kurir']:
                    if c in res.columns:
                        res[c] = pd.to_datetime(res[c], errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S').replace('NaT', np.nan).fillna('')
                if 'Handover Date' in res.columns:
                    res['Handover Date'] = res['Handover Date'].replace('NaT', np.nan).fillna('')

                def to_dt(col_name): 
                    return res.get('Handover_Date_Raw') if col_name == 'Handover Date' else pd.to_datetime(res.get(col_name), errors='coerce')

                def format_timedelta_hhmmss(td_series):
                    if td_series is None: return ""
                    seconds = td_series.dt.total_seconds().fillna(0).astype(int)
                    is_neg = seconds < 0
                    seconds = abs(seconds)
                    res_str = (seconds // 3600).astype(str).str.zfill(2) + ":" + ((seconds % 3600) // 60).astype(str).str.zfill(2) + ":" + (seconds % 60).astype(str).str.zfill(2)
                    return np.where(td_series.isna(), "", np.where(is_neg, "-" + res_str, res_str))

                res['Packing to Shpped Date'] = format_timedelta_hhmmss(to_dt('Shipped Date') - to_dt('Packing Complete'))
                res['Packing to Handover'] = format_timedelta_hhmmss(to_dt('Handover Date') - to_dt('Packing Complete'))
                res['Shipped Date to Handover'] = format_timedelta_hhmmss(to_dt('Handover Date') - to_dt('Shipped Date'))
                res['End Ship Date to Shpped Date'] = format_timedelta_hhmmss(to_dt('End Ship Date') - to_dt('Shipped Date'))

                res['Kota'] = res[next((c for c in res.columns if 'ship to city' in c.lower()), None)] if next((c for c in res.columns if 'ship to city' in c.lower()), None) else np.nan
                res['Provinsi'] = res[next((c for c in res.columns if 'ship to st' in c.lower() or 'prov' in c.lower()), None)] if next((c for c in res.columns if 'ship to st' in c.lower() or 'prov' in c.lower()), None) else np.nan

                # --- LOOKUP STATUS & PAYMENT METHOD ---
                df_erp = dfs['erp']
                col_erp_order = next((c for c in df_erp.columns if 'erp order number' in c.lower()), None) if not df_erp.empty else None
                if col_erp_order and 'ERP Document Number' in res.columns:
                    df_erp = df_erp.drop_duplicates(subset=[col_erp_order]).loc[:, ~df_erp.columns.duplicated()]
                    col_status = next((c for c in df_erp.columns if 'online status' in c.lower()), None)
                    col_payment = next((c for c in df_erp.columns if 'payment method' in c.lower()), None)
                    col_amount = next((c for c in df_erp.columns if 'total order amount' in c.lower()), None)
                    
                    res_erp_m = res[['ERP Document Number']].merge(df_erp[[col_erp_order] + ([col_status] if col_status else []) + ([col_payment] if col_payment else []) + ([col_amount] if col_amount else [])], left_on='ERP Document Number', right_on=col_erp_order, how='left')
                    
                    raw_status = res_erp_m[col_status] if col_status else pd.Series([np.nan]*len(res))
                    
                    def map_status(val):
                        v_str = str(val).strip()
                        if pd.isna(val) or v_str in ['', 'nan', 'None', 'NaN']:
                            return 'Other'
                        return val

                    res['Status'] = raw_status.apply(map_status)
                    res['total order amount'] = res_erp_m[col_amount] if col_amount else np.nan
                    
                    def map_payment(x):
                        x_str = str(x).strip()
                        if x_str in ['在线支付', 'nan', 'None', '', 'NaN']:
                            return 'Non COD'
                        elif x_str.upper() == 'COD':
                            return 'COD'
                        return 'Non COD'
                        
                    res['Payment Menthood'] = res_erp_m[col_payment].apply(map_payment) if col_payment else 'Non COD'
                else:
                    res['Status'] = 'Other'
                    res['total order amount'] = np.nan
                    res['Payment Menthood'] = 'Non COD'

                res['Attachment'] = df_ho[ho_col_map.get('Attachment', None)].apply(lambda x: str(x).strip() if pd.notna(x) else '') if ho_col_map.get('Attachment', None) else np.nan
                res['Dokumen'] = np.where(res['Attachment'].replace({0: np.nan, '0': np.nan, '': np.nan}).isna(), 'Not yet Input', 'YES')

                res['Times Proses Kurir to Shpped Date'] = format_timedelta_hhmmss(to_dt('Times Proses Kurir') - to_dt('Shipped Date'))
                plat_cond = res.get('Platform', pd.Series(['']*len(res))).astype(str).str.lower().isin(['shopee', 'tiktok'])
                ai_val, w_val = to_dt('Times Proses Kurir'), to_dt('End Ship Date')
                res['Status Manifest'] = np.where(ai_val.isna() | w_val.isna(), "", np.where(plat_cond, np.where(ai_val > w_val, "Late", "On Time"), "On Time"))

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
                        if pd.isna(val) or str(val).strip() in ['', 'NaT']:
                            sec_list.append(0.0); continue
                        val_str = str(val).strip()
                        sign = -1 if val_str.startswith('-') else 1
                        parts = val_str.replace('-', '').split(':')
                        try:
                            if len(parts) == 3:
                                sec_list.append(sign * (float(parts[0] or 0) * 3600 + float(parts[1] or 0) * 60 + float(parts[2] or 0)))
                            else: sec_list.append(0.0)
                        except: sec_list.append(0.0)
                    return pd.Series(sec_list)

                sec_an = get_safe_seconds(res['Pay-Created'])
                sec_ao = get_safe_seconds(res['Created-Released'])
                sec_ap = get_safe_seconds(res['Released-Pick'])
                sec_aq = get_safe_seconds(res['Pick-Pack'])
                sec_ar = get_safe_seconds(res['Pack-Collect'])
                sec_as = get_safe_seconds(res['Collect-Manifest'])
                sec_at = get_safe_seconds(res['Manifest-Endshipdate'])

                max_sec = np.maximum.reduce([sec_an, sec_ao, sec_ap, sec_aq, sec_ar, sec_as, sec_at])

                res['Late Proses By'] = np.select(
                    [
                        (max_sec > 0) & (max_sec == sec_an),
                        (max_sec > 0) & (max_sec == sec_ao),
                        (max_sec > 0) & (max_sec == sec_ap),
                        (max_sec > 0) & (max_sec == sec_aq),
                        (max_sec > 0) & (max_sec == sec_ar),
                        (max_sec > 0) & (max_sec == sec_as),
                    ],
                    ["System", "Admin", "Picker", "Packer", "Outbound", "Kurir"],
                    default=""
                )

                progress_bar.progress(90, text="Processing... (Menyusun laporan akhir & Excel) [90%]")
                
                res['Admin '] = res['Admin']
                res['Kurir '] = res['Kurir']

                kolom_final = [
                    'WMS Order', 'ERP Document Number', 'Tracking#/PRO#', 'PlatformOrder', 'Staged User', 
                    'Platform', 'Brand', 'Brand 2', 'Admin', 'Load', 'Kurir', 'Loader', 'Tanggal Handover', 
                    'Wave ID', 'Created Time', 'Ordered Date', 'Picking Task Created Time', 
                    'pickCompletedTime - Released Date Pack', 'Packing Complete', 'Shipped Date', 'Handover Date', 
                    'End Ship Date', 'Packing to Shpped Date', 'Packing to Handover', 'Shipped Date to Handover', 
                    'End Ship Date to Shpped Date', 'Kota', 'Provinsi', 'Status', 'Payment Menthood', 
                    'total order amount', 'Dokumen', 'Attachment', 'Times Proses Kurir', 'Times Proses Kurir to Shpped Date', 
                    'Status Manifest', 'Status Late', 'Remark Late', 'Pay-Created', 'Created-Released', 'Released-Pick', 
                    'Pick-Pack', 'Pack-Collect', 'Collect-Manifest', 'Manifest-Endshipdate', 'Max', 'System', 'Admin ', 
                    'Picker', 'Packer', 'Outbound', 'Kurir ', 'Late Proses By'
                ]
                
                for col in kolom_final:
                    if col not in res.columns: res[col] = np.nan
                final_df = res[kolom_final].copy()
                final_df = final_df.loc[:, ~final_df.columns.duplicated()]

                master_df = dfs.get('master', pd.DataFrame())
                master_status_col = next((c for c in master_df.columns if 'online status' in c.lower() or c.lower() == 'status'), None)
                master_track_col = next((c for c in master_df.columns if 'tracking' in c.lower()), None)
                master_track_dict = {}
                if master_status_col and master_track_col:
                    for _, row in master_df.iterrows():
                        st_val = str(row[master_status_col]).strip().lower()
                        tr_val = str(row[master_track_col]).strip().lower()
                        if st_val and pd.notna(row[master_track_col]): master_track_dict[st_val] = tr_val

                final_df['Master_Tracking'] = final_df['Status'].astype(str).str.strip().str.lower().map(master_track_dict).fillna('untraceable')
                final_df.insert(0, 'No', range(1, len(final_df) + 1))
                st.session_state['processed_result'] = final_df

                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_to_export = final_df.drop(columns=['Master_Tracking'], errors='ignore')
                    df_to_export.columns = [c.strip() if c in ['Admin ', 'Kurir '] else c for c in df_to_export.columns]
                    
                    df_to_export.to_excel(writer, index=False, sheet_name='Laporan_WMS')
                    
                    workbook = writer.book
                    worksheet_wms = writer.sheets['Laporan_WMS']
                    
                    format_header = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3', 'border': 1, 'align': 'center', 'valign': 'vcenter'})
                    format_time = workbook.add_format({'num_format': 'hh:mm:ss', 'border': 1, 'align': 'center', 'valign': 'vcenter'})
                    cell_format_center = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1})
                    
                    col_idx_track = list(df_to_export.columns).index('Tracking#/PRO#')
                    col_idx_plat = list(df_to_export.columns).index('PlatformOrder')
                    
                    for row_num in range(len(df_to_export)):
                        val_track = str(df_to_export.iloc[row_num]['Tracking#/PRO#'])
                        val_plat = str(df_to_export.iloc[row_num]['PlatformOrder'])
                        if val_track != 'nan' and val_track != '': worksheet_wms.write_string(row_num + 1, col_idx_track, val_track, cell_format_center)
                        if val_plat != 'nan' and val_plat != '': worksheet_wms.write_string(row_num + 1, col_idx_plat, val_plat, cell_format_center)

                        excel_row = row_num + 2
                        
                        worksheet_wms.write_formula(row_num + 1, 46, f"=MAX(IFERROR(VALUE(AN{excel_row}),0), IFERROR(VALUE(AO{excel_row}),0), IFERROR(VALUE(AP{excel_row}),0), IFERROR(VALUE(AQ{excel_row}),0), IFERROR(VALUE(AR{excel_row}),0), IFERROR(VALUE(AS{excel_row}),0), IFERROR(VALUE(AT{excel_row}),0))", format_time)
                        worksheet_wms.write_formula(row_num + 1, 47, f"=AND(AU{excel_row}>0, AU{excel_row}=IFERROR(VALUE(AN{excel_row}), FALSE))")
                        worksheet_wms.write_formula(row_num + 1, 48, f"=AND(AU{excel_row}>0, AU{excel_row}=IFERROR(VALUE(AO{excel_row}), FALSE))")
                        worksheet_wms.write_formula(row_num + 1, 49, f"=AND(AU{excel_row}>0, AU{excel_row}=IFERROR(VALUE(AP{excel_row}), FALSE))")
                        worksheet_wms.write_formula(row_num + 1, 50, f"=AND(AU{excel_row}>0, AU{excel_row}=IFERROR(VALUE(AQ{excel_row}), FALSE))")
                        worksheet_wms.write_formula(row_num + 1, 51, f"=AND(AU{excel_row}>0, AU{excel_row}=IFERROR(VALUE(AR{excel_row}), FALSE))")
                        worksheet_wms.write_formula(row_num + 1, 52, f"=AND(AU{excel_row}>0, AU{excel_row}=IFERROR(VALUE(AS{excel_row}), FALSE))")
                        
                        formula_late_by = (
                            f'=IF(AV{excel_row}, "System", '
                            f'IF(AW{excel_row}, "Admin", '
                            f'IF(AX{excel_row}, "Picker", '
                            f'IF(AY{excel_row}, "Packer", '
                            f'IF(AZ{excel_row}, "Outbound", '
                            f'IF(BA{excel_row}, "Kurir", ""))))))'
                        )
                        worksheet_wms.write_formula(row_num + 1, 53, formula_late_by)

                    for col_num, col_name in enumerate(df_to_export.columns):
                        worksheet_wms.write(0, col_num, col_name, format_header)
                        col_data_len = df_to_export.iloc[:, col_num].astype(str).str.len().max() if not df_to_export.empty else 0
                        header_len = len(str(col_name))
                        max_len = max(header_len, col_data_len)
                        worksheet_wms.set_column(col_num, col_num, max_len + 4, cell_format_center)

                    # ==========================================
                    # SHEET DB (DASHBOARD SUMMARY)
                    # ==========================================
                    worksheet_db = workbook.add_worksheet('DB')
                    header_format_db = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3', 'border': 1, 'align': 'center', 'valign': 'vcenter'})
                    cell_format_db = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter'})
                    
                    black_divider = workbook.add_format({'bg_color': '#000000'})
                    
                    df_brand = final_df['Brand'].value_counts().reset_index()
                    df_brand.columns = ['Brand', 'Delivered']
                    df_brand.insert(0, 'No', range(1, len(df_brand) + 1))
                    
                    df_os_open = dfs.get('order_summary_open', dfs.get('order_summary', pd.DataFrame()))
                    if not df_os_open.empty:
                        col_store_os = next((c for c in df_os_open.columns if 'store number' in c.lower() or c.lower() == 'storenumber' or 'store' in c.lower()), None)
                        if col_store_os:
                            os_mapped_brands = []
                            for _, row in df_os_open.iterrows():
                                sn = safe_key(row[col_store_os])
                                if sn == "":
                                    os_mapped_brands.append("SK")
                                else:
                                    store_info = master_store_db.get(sn, {})
                                    b_val = store_info.get('Brand2', '')
                                    if not b_val:
                                        b_val = store_info.get('Brand', '')
                                    if b_val:
                                        os_mapped_brands.append(b_val)
                                    else:
                                        os_mapped_brands.append("SK")
                            
                            if os_mapped_brands:
                                target_counts = pd.Series(os_mapped_brands).value_counts()
                                df_brand['Target'] = df_brand['Brand'].map(target_counts).fillna(0).astype(int)
                            else:
                                df_brand['Target'] = 0
                        else:
                            df_brand['Target'] = 0
                    else:
                        df_brand['Target'] = 0

                    df_kurir = final_df['Kurir'].value_counts().reset_index()
                    df_kurir.columns = ['Courier_Name', 'Total_Package']
                    df_kurir = df_kurir.head(5)
                    df_kurir.insert(0, 'No', range(1, len(df_kurir) + 1))
                    df_kurir['Ranking'] = range(1, len(df_kurir) + 1)
                    
                    df_status = final_df['Status Manifest'].replace('', 'Unknown').value_counts().reset_index()
                    df_status.columns = ['Status_Manifest', 'qty']
                    df_status.insert(0, 'No', range(1, len(df_status) + 1))

                    df_late_manifest = pd.DataFrame(columns=['No', 'Late_Proses_By', 'qty'])
                    if 'Status Manifest' in final_df.columns and 'Late Proses By' in final_df.columns:
                        late_df = final_df[final_df['Status Manifest'].astype(str).str.strip().str.lower() == 'late']
                        if not late_df.empty:
                            grouped_late = late_df['Late Proses By'].replace('', 'Unknown').fillna('Unknown').value_counts().reset_index()
                            grouped_late.columns = ['Late_Proses_By', 'qty']
                            grouped_late.insert(0, 'No', range(1, len(grouped_late) + 1))
                            df_late_manifest = grouped_late

                    df_kurir_manifest = pd.DataFrame()
                    if 'Kurir' in final_df.columns and 'Times Proses Kurir to Shpped Date' in final_df.columns:
                        temp_k = final_df[['Kurir', 'Times Proses Kurir to Shpped Date']].copy()
                        temp_k['sec'] = get_safe_seconds(temp_k['Times Proses Kurir to Shpped Date'])
                        grouped_k = temp_k.groupby('Kurir')['sec'].mean().reset_index()
                        grouped_k = grouped_k.sort_values(by='sec', ascending=True).reset_index(drop=True)
                        grouped_k['Avg_Process_Time'] = grouped_k['sec'].apply(lambda s: f"{int(s)//3600}:{(int(s)%3600)//60:02d}:{int(s)%60:02d}" if pd.notna(s) and s > 0 else "0:00:00")
                        df_kurir_manifest = grouped_k[['Kurir', 'Avg_Process_Time']].copy()
                        df_kurir_manifest.columns = ['Courier_Name', 'Avg_Times_Proses_Kurir_to_Shipped']
                        df_kurir_manifest.insert(0, 'No', range(1, len(df_kurir_manifest) + 1))
                    else:
                        df_kurir_manifest = pd.DataFrame(columns=['No', 'Courier_Name', 'Avg_Times_Proses_Kurir_to_Shipped'])

                    val_target = len(df_os_open) if not df_os_open.empty else 0
                    val_delivered = len(final_df)
                    val_delivery_rate = round((val_delivered / val_target * 100), 2) if val_target > 0 else 0.0

                    raw_daily_df = dfs.get('daily_ho', pd.DataFrame()).copy()
                    val_kurir_instan = 0
                    if not raw_daily_df.empty:
                        cols_lower = [str(c).strip().lower() for c in raw_daily_df.columns]
                        courier_col_idx = -1
                        qty_col_idx = -1
                        
                        for idx, c_name in enumerate(cols_lower):
                            if 'ekspedisi' in c_name or 'kurir' in c_name or 'courier' in c_name or 'service' in c_name:
                                courier_col_idx = idx
                                break
                        if courier_col_idx == -1 and len(raw_daily_df.columns) > 0:
                            courier_col_idx = 0
                            
                        for idx, c_name in enumerate(cols_lower):
                            if 'deliveree' in c_name or 'qty' in c_name or 'total' in c_name or 'order' in c_name:
                                if idx != courier_col_idx:
                                    qty_col_idx = idx
                                    break
                        if qty_col_idx == -1 and len(raw_daily_df.columns) > 1:
                            qty_col_idx = 1
                            
                        if courier_col_idx != -1 and qty_col_idx != -1:
                            c_col_name = raw_daily_df.columns[courier_col_idx]
                            q_col_name = raw_daily_df.columns[qty_col_idx]
                            
                            target_kurir = [
                                'go-jek/grab/shopee instant',
                                'anteraja sameday (rit 1)', 'anteraja sameday (rit 2)', 'anteraja sameday (rit 3)',
                                'paxel ( rit 1 )', 'paxel ( rit 2 )', 'paxel ( rit 3 )'
                            ]
                            
                            for _, r in raw_daily_df.iterrows():
                                c_val = str(r[c_col_name]).strip().lower()
                                if any(t in c_val for t in ['total', 'jumlah', 'sum']):
                                    continue
                                if any(tk == c_val for tk in target_kurir):
                                    try:
                                        q_val = float(str(r[q_col_name]).replace(',', '').strip())
                                        val_kurir_instan += int(q_val)
                                    except:
                                        pass

                    if val_kurir_instan == 0 and 'Kurir' in final_df.columns:
                        instan_list = [
                            'go-jek/grab/shopee instant',
                            'anteraja sameday (rit 1)', 'anteraja sameday (rit 2)', 'anteraja sameday (rit 3)',
                            'paxel ( rit 1 )', 'paxel ( rit 2 )', 'paxel ( rit 3 )'
                        ]
                        val_kurir_instan = int(final_df['Kurir'].astype(str).str.strip().str.lower().isin(instan_list).sum())

                    brand2_series = final_df['Brand 2'].astype(str).str.strip().str.lower()
                    platform_series = final_df['Platform'].astype(str).str.strip().str.lower()
                    
                    fulfilment_brands = ['dojako', 'firda', 'noura', "mama's choice", 'mamas choice']
                    
                    is_fulfilment = brand2_series.isin(fulfilment_brands)
                    is_other = ((platform_series == 'webstore') & (brand2_series == 'acekid')) | \
                               ((platform_series == 'other') & (brand2_series == 'sk'))
                    is_enabler = ~is_fulfilment & ~is_other

                    val_jc_fulfilment = int(is_fulfilment.sum())
                    val_other = int(is_other.sum())
                    val_jc_enabler = int(is_enabler.sum())

                    val_pending = 0
                    if not raw_daily_df.empty:
                        col0 = raw_daily_df.columns[0]; col1 = raw_daily_df.columns[1] if len(raw_daily_df.columns) > 1 else col0
                        clean_daily = raw_daily_df[~(raw_daily_df[col0].astype(str).str.lower().str.contains('total', na=False) | raw_daily_df[col1].astype(str).str.lower().str.contains('total', na=False))]
                        col_pending = next((c for c in clean_daily.columns if 'cut off' in c.lower() or 'pending' in c.lower()), None)
                        if col_pending:
                            val_pending = int(pd.to_numeric(clean_daily[col_pending].astype(str).str.replace(r'[^\d.-]', '', regex=True), errors='coerce').fillna(0).sum())

                    val_traceable = int(final_df['Master_Tracking'].eq('traceable').sum())
                    val_untraceable = int(final_df['Master_Tracking'].eq('untraceable').sum())

                    metrics_data = [
                        [1, "delivery_rate", val_delivery_rate, "Persentase delivery rate"],
                        [2, "delivered", f"{val_delivered:,}", "Total order di sheet Laporan_WMS"],
                        [3, "target", f"{val_target:,}", "Total baris dari file Order Summary Export OPEN"],
                        [4, "pending_order", f"{val_pending:,}", "Jumlah order pending"],
                        [5, "avg_shipped", "0:24:41", "Rata-rata waktu ke shipped"],
                        [6, "avg_handover", "4:20:20", "Rata-rata waktu ke handover"],
                        [7, "kurir_instan", val_kurir_instan, "Total kurir instan"],
                        [8, "jc_enabler", val_jc_enabler, "Jet Commerce Enabler"],
                        [9, "jc_fulfilment", val_jc_fulfilment, "Jet Commerce Fulfilment"],
                        [10, "other", val_other, "Kategori lainnya"],
                        [11, "traceable", val_traceable, "Paket yang bisa dilacak"],
                        [12, "untraceable", val_untraceable, "Paket tidak bisa dilacak"],
                    ]
                    df_metrics = pd.DataFrame(metrics_data, columns=["No", "Metric_Name", "Value", "Description"])
                    
                    worksheet_db.set_row(0, 4, black_divider)

                    def write_custom_table_autofit(df_table, start_row, start_col):
                        for c_idx, col_name in enumerate(df_table.columns):
                            worksheet_db.write(start_row, start_col + c_idx, col_name, header_format_db)
                            col_data = df_table.iloc[:, c_idx].astype(str)
                            max_val_len = col_data.str.len().max() if not col_data.empty else 0
                            max_len = max(len(str(col_name)), max_val_len)
                            worksheet_db.set_column(start_col + c_idx, start_col + c_idx, max_len + 4)

                        for r_idx, row in enumerate(df_table.values):
                            for c_idx, val in enumerate(row):
                                worksheet_db.write(start_row + r_idx + 1, start_col + c_idx, val, cell_format_db)

                    write_custom_table_autofit(df_metrics, 1, 0)
                    worksheet_db.set_column(4, 4, 0.5, black_divider)
                    write_custom_table_autofit(df_brand, 1, 5)
                    worksheet_db.set_column(9, 9, 0.5, black_divider)
                    write_custom_table_autofit(df_kurir, 1, 10)
                    worksheet_db.set_column(14, 14, 0.5, black_divider)
                    write_custom_table_autofit(df_kurir_manifest, 1, 15)
                    worksheet_db.set_column(18, 18, 0.5, black_divider)
                    write_custom_table_autofit(df_status, 1, 19)
                    worksheet_db.set_column(22, 22, 0.5, black_divider)
                    write_custom_table_autofit(df_late_manifest, 1, 23)

                st.session_state['excel_data'] = output.getvalue()
                
                val_total_late = int((final_df['Status Manifest'].astype(str).str.strip().str.lower() == 'late').sum())
                mask_late = final_df['Status Manifest'].astype(str).str.strip().str.lower() == 'late'
                val_avg_late_sec = max_sec[mask_late.values].mean() if val_total_late > 0 else 0
                avg_late_str = f"{int(val_avg_late_sec)//3600}:{(int(val_avg_late_sec)%3600)//60:02d}:{int(val_avg_late_sec)%60:02d}"

                st.session_state['metrics'] = {
                    "Delivery Rate": f"{val_delivery_rate}%",
                    "Delivered": f"{val_delivered:,}",
                    "Target": f"{val_target:,}",
                    "Pending": f"{val_pending:,}",
                    "Total Late": f"{val_total_late:,}",
                    "Avg Delay": avg_late_str,
                    "Untraceable": val_untraceable,
                    "Inbound": val_kurir_instan
                }

                progress_bar.progress(100, text="Processing Selesai! (100%)")
                progress_bar.empty()

            except Exception as e:
                st.error(f"❌ Terjadi kesalahan Sistem: {e}")
                st.code(traceback.format_exc())
        else:
            st.warning("Silakan unggah file sumber terlebih dahulu di area Data Center.")

    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 5. TAMPILAN DASHBOARD & PREVIEW
# ==========================================
if 'processed_result' in st.session_state:
    res_df = st.session_state['processed_result']
    m = st.session_state.get('metrics', {})
    
    if m:
        st.markdown('<div class="section-container">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📌 Todo / Key Metrics Overview</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="todo-grid">
            <div class="todo-card todo-card-red">
                <div class="todo-label">Orders out of<br>SLA (Late)</div>
                <div class="todo-value">{m.get('Total Late', 0)}</div>
            </div>
            <div class="todo-card todo-card-amber">
                <div class="todo-label">Untraceable<br>Orders</div>
                <div class="todo-value">{m.get('Untraceable', 0)}</div>
            </div>
            <div class="todo-card todo-card-teal">
                <div class="todo-label">Avg Delay<br>Time</div>
                <div class="todo-value">{m.get('Avg Delay', '0:00:00')}</div>
            </div>
            <div class="todo-card todo-card-blue">
                <div class="todo-label">Delivery<br>Rate</div>
                <div class="todo-value">{m.get('Delivery Rate', '0%')}</div>
            </div>
            <div class="todo-card todo-card-teal">
                <div class="todo-label">Total<br>Delivered</div>
                <div class="todo-value">{m.get('Delivered', 0)}</div>
            </div>
            <div class="todo-card todo-card-teal">
                <div class="todo-label">Pending<br>Order</div>
                <div class="todo-value">{m.get('Pending', 0)}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 Analisis & Data Preview</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📈 Analytics Kurir", "🔍 Untraceable Check", "📋 Data Preview"])
    
    with tab1:
        st.markdown("### Analisis Keterlambatan per Kurir (Status Manifest Late)")
        if 'Status Manifest' in res_df.columns and 'Late Proses By' in res_df.columns and 'Kurir' in res_df.columns:
            late_df_web = res_df[res_df['Status Manifest'].astype(str).str.strip().str.lower() == 'late'].copy()
            
            if not late_df_web.empty:
                # 1. CHART
                chart_df = late_df_web.groupby(['Kurir', 'Late Proses By']).size().reset_index(name='Qty')
                chart_df = chart_df[chart_df['Qty'] > 0]
                chart_df = chart_df.sort_values(by=['Kurir', 'Late Proses By'])
                
                chart_df['Qty_cumu'] = chart_df.groupby('Kurir')['Qty'].cumsum()
                chart_df['Qty_mid'] = chart_df['Qty_cumu'] - (chart_df['Qty'] / 2)
                
                sort_order = alt.EncodingSortField(field='Qty', op='sum', order='descending')
                
                base = alt.Chart(chart_df).encode(
                    y=alt.Y('Kurir:N', sort=sort_order, title='Kurir / Ekspedisi', axis=alt.Axis(labelLimit=200, titleFontWeight=600))
                )
                
                bars = base.mark_bar(height=28, opacity=0.9).encode(
                    x=alt.X('Qty:Q', stack='zero', axis=None),
                    color=alt.Color('Late Proses By:N', scale=alt.Scale(scheme='tableau10'), legend=alt.Legend(title="Penyebab Keterlambatan", orient="bottom", titleFontWeight=600)),
                    tooltip=['Kurir:N', 'Late Proses By:N', 'Qty:Q']
                )
                
                text = base.mark_text(
                    align='center', 
                    baseline='middle', 
                    fontWeight='bold', 
                    fontSize=12, 
                    color='black'
                ).encode(
                    x=alt.X('Qty_mid:Q', axis=None),
                    text=alt.Text('Qty:Q', format=',')
                )
                
                chart = (bars + text).properties(height=420, padding={'left': 10, 'right': 10, 'top': 10, 'bottom': 10}).interactive()
                st.altair_chart(chart, use_container_width=True)

                st.markdown("---")

                # 2. TABEL STATISTIK / CROSS-TABULATION
                st.markdown("**Tabel Statistik Keterlambatan (Kurir vs Penyebab Keterlambatan):**")
                
                stat_df = pd.pivot_table(
                    late_df_web,
                    index='Kurir',
                    columns='Late Proses By',
                    values='WMS Order',
                    aggfunc='count',
                    fill_value=0
                )
                
                expected_cols = ['Admin', 'Outbound', 'Packer', 'Picker', 'System', 'Kurir']
                for col in expected_cols:
                    if col not in stat_df.columns:
                        stat_df[col] = 0
                
                other_cols = [c for c in stat_df.columns if c not in expected_cols]
                stat_df = stat_df[expected_cols + other_cols]
                
                if '' in stat_df.columns:
                    stat_df = stat_df.drop(columns=[''])
                
                stat_df['Total Late'] = stat_df.sum(axis=1)
                stat_df = stat_df.sort_values(by='Total Late', ascending=False).reset_index()
                
                st.dataframe(stat_df, use_container_width=True, hide_index=True)
            else:
                st.info("ℹ️ Tidak ada data dengan status manifest 'Late'.")
        else:
            st.info("ℹ️ Kolom yang diperlukan tidak ditemukan.")

    with tab2:
        if 'Master_Tracking' in res_df.columns:
            untraceable_data = res_df[res_df['Master_Tracking'] == 'untraceable'].copy()
            untraceable_count = len(untraceable_data)
            
            if untraceable_count > 0:
                st.warning(f"⚠️ Ditemukan **{untraceable_count}** paket dengan status **Untraceable**!")
                col_u1, col_u2 = st.columns([1, 2])
                with col_u1:
                    st.markdown("**Ringkasan Jumlah Paket per Status:**")
                    status_summary = untraceable_data['Status'].value_counts().reset_index()
                    status_summary.columns = ['Status', 'Jumlah Paket']
                    st.dataframe(status_summary, use_container_width=True, hide_index=True)
                with col_u2:
                    st.markdown("**Detail Paket Untraceable:**")
                    cols_to_show = [c for c in ['No', 'WMS Order', 'ERP Document Number', 'Platform', 'Kurir', 'Status', 'Tracking#/PRO#'] if c in untraceable_data.columns]
                    st.dataframe(untraceable_data[cols_to_show], use_container_width=True, hide_index=True)
            else:
                st.success("🎉 Seluruh paket berstatus **Traceable** (0 Untraceable).")

    with tab3:
        essential_cols = ['WMS Order', 'ERP Document Number', 'Tracking#/PRO#', 'Platform', 'Kurir', 'Status']
        empty_report = []
        for col in essential_cols:
            if col in res_df.columns:
                is_na = res_df[col].isna()
                is_empty_str = res_df[col].astype(str).str.strip() == ''
                is_null_text = res_df[col].astype(str).str.strip().str.lower().isin(['nan', 'none', 'null', 'nat'])
                missing_count = (is_na | is_empty_str | is_null_text).sum()
                if missing_count > 0:
                    empty_report.append(f"Kolom **{col}** kosong sebanyak **{missing_count}** baris.")
        
        if empty_report:
            warning_msg = "<br>".join([f"- {rep}" for rep in empty_report])
            st.markdown(f"""
                <div class="result-notif result-warning" style="background-color: #FEF2F2; color: #991B1B; border: 1px solid #FCA5A5;">
                    🚨 **PERINGATAN KOLOM KOSONG:**<br>{warning_msg}
                </div>
            """, unsafe_allow_html=True)
        
        display_df = res_df.drop(columns=['Master_Tracking'], errors='ignore')
        st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.divider()
    col_down1, col_down2, col_down3 = st.columns([1, 2, 1])
    with col_down2:
        st.download_button(
            label="📥 Download Laporan Excel",
            data=st.session_state['excel_data'],
            file_name=f"Laporan_Outbound_{datetime.datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True
        )
    st.markdown('</div>', unsafe_allow_html=True)
