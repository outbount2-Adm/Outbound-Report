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
    page_title="Outbound Auto-Processor", 
    layout="wide", 
    page_icon="icon.png", 
    initial_sidebar_state="collapsed"
)

current_date = datetime.datetime.now().strftime("%B %d, %Y")

# ==========================================
# 2. CSS KUSTOM
# ==========================================
custom_css = """
<style>
    .stApp { background-color: #FFFFFF; }
    #MainMenu, footer, header, .stDeployButton, [data-testid="viewerBadge"] {
        visibility: hidden !important; 
        display: none !important;
    }
    .block-container {
        padding-top: 2rem !important;
        max-width: 1200px;
    }
    h1 {
        color: #0f172a;
        font-weight: 900;
        letter-spacing: -0.5px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        margin-bottom: 0px !important;
        padding-bottom: 0px !important;
        text-align: left !important;
    }
    h3 {
        color: #334155;
        font-weight: 700;
        font-size: 1.4rem !important;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .meta-text {
        color: #64748b;
        font-size: 15px;
        margin-top: 5px;
        margin-bottom: 20px;
        text-align: left !important;
    }
    .officer-name { color: #2563eb; font-weight: bold; }
    [data-testid="stFileUploader"] {
        background-color: #f8fafc !important;
        border: 1.5px dashed #3b82f6 !important;
        border-radius: 8px !important;
        padding: 20px !important;
    }
    div[data-testid="stButton"] > button[kind="primary"],
    button[data-testid="baseButton-primary"], 
    .stButton > button[type="primary"] {
        background-color: #2563eb !important;
        background-image: none !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px;
        padding: 14px 24px !important;
        transition: background-color 0.3s ease;
    }
    div[data-testid="stButton"] > button[kind="primary"]:hover,
    button[data-testid="baseButton-primary"]:hover, 
    .stButton > button[type="primary"]:hover {
        background-color: #1d4ed8 !important;
        color: white !important;
    }
    div[data-testid="stButton"] > button:not([kind="primary"]):not([type="primary"]) {
        background-color: #ffffff !important;
        color: #334155 !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        padding: 10px 16px !important;
        transition: background-color 0.2s ease, border-color 0.2s ease;
    }
    div[data-testid="stButton"] > button:not([kind="primary"]):not([type="primary"]):hover {
        background-color: #f8fafc !important;
        border-color: #94a3b8 !important;
        color: #0f172a !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# 3. HEADER & META INFO SECTION
# ==========================================
if 'saved_admin' not in st.session_state:
    st.session_state['saved_admin'] = "Admin Logistik"

col_header1, col_header2 = st.columns([1, 15])
with col_header1:
    try:
        st.image("icon.png", width=55)
    except:
        pass 
with col_header2:
    st.markdown('<h1 style="margin-top: -5px; text-align: left;">Outbound Auto-Processor</h1>', unsafe_allow_html=True)

st.markdown(f'<div class="meta-text">Officer: <span class="officer-name">{st.session_state["saved_admin"]}</span> | Date: {current_date}</div>', unsafe_allow_html=True)

col_adm1, col_adm2 = st.columns([4, 1])
with col_adm1:
    admin_input_temp = st.text_input("Admin", value=st.session_state['saved_admin'], label_visibility="collapsed", placeholder="Ketik nama Officer / Admin...")
with col_adm2:
    submit_admin = st.button("Submit Admin", use_container_width=True)

if submit_admin:
    st.session_state['saved_admin'] = admin_input_temp
    st.rerun()

current_admin = st.session_state['saved_admin']
st.divider()

# ==========================================
# 4. DATA CENTER (UPLOAD SECTION)
# ==========================================
st.markdown('<h3>📁 Data Center</h3>', unsafe_allow_html=True)
st.markdown('<div style="color: #475569; font-size: 14px; margin-bottom: 12px;">Upload multiple source files (Order Summary, Operation Log, ERP, HO Outbound, Master) to begin.</div>', unsafe_allow_html=True)

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
    if st.button("🗑️ Clear Data", use_container_width=True):
        st.session_state['file_uploader_key'] += 1
        if 'processed_result' in st.session_state:
            del st.session_state['processed_result']
        if 'excel_data' in st.session_state:
            del st.session_state['excel_data']
        st.rerun()

st.write("")

# ==========================================
# 5. PROCESSING QUEUE (EXECUTE SECTION)
# ==========================================
st.markdown('<h3>⚙️ Processing Queue</h3>', unsafe_allow_html=True)
execute_clicked = st.button("🚀 Data processing", type="primary", use_container_width=True)

if execute_clicked:
    if uploaded_files:
        progress_bar = st.progress(0, text="Processing... (0%)")
        
        try:
            progress_bar.progress(10, text="Processing... (Membaca file sumber) [10%]")
            dfs = {}
            master_store_db = {}
            master_carrier_db = {}
            master_category_map = {}
            
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

                    # Lookup Master Category (Platform & Brand 2)
                    m_pb2_col = next((c for c in df.columns if 'platform' in c.lower() and 'brand' in c.lower()), None)
                    m_plat_col = next((c for c in df.columns if c.lower().strip() == 'platform'), None)
                    m_b2_col = next((c for c in df.columns if 'brand' in c.lower() and ('2' in c or 'brand2' in c.lower())), None)
                    m_cat_col = next((c for c in df.columns if 'category' in c.lower()), None)
                    
                    if m_cat_col:
                        for _, row in df.iterrows():
                            cat_val = str(row[m_cat_col]).strip() if pd.notna(row[m_cat_col]) else "Other"
                            
                            if m_pb2_col and pd.notna(row[m_pb2_col]):
                                key_single = str(row[m_pb2_col]).strip().upper()
                                master_category_map[key_single] = cat_val
                                
                            if m_plat_col and m_b2_col:
                                p_v = str(row[m_plat_col]).strip().upper() if pd.notna(row[m_plat_col]) else ""
                                b_v = str(row[m_b2_col]).strip().upper() if pd.notna(row[m_b2_col]) else ""
                                if p_v and b_v:
                                    master_category_map[f"{p_v} & {b_v}"] = cat_val
                                    master_category_map[f"{p_v}&{b_v}"] = cat_val
                                    master_category_map[(p_v, b_v)] = cat_val

                elif 'ho' in file_name or 'outbound' in file_name or 'daily' in file_name: 
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
                st.error("❌ File 'HO Outbound' / 'Daily HO' tidak ditemukan.")
                st.stop()
            if 'order_summary' not in dfs:
                st.error("❌ File 'Order Summary' tidak ditemukan.")
                st.stop()
            if 'master' not in dfs:
                st.warning("⚠️ File 'Master' tidak ditemukan.")

            for key in ['op_log', 'pack_task', 'erp']:
                if key not in dfs: dfs[key] = pd.DataFrame()

            # --- TAHAP 2: Merge Data (35%) ---
            progress_bar.progress(35, text="Processing... (Mencocokkan baris & Merge data) [35%]")
            df_ho = dfs['ho_outbound'].copy()
            if 'WMS Order' not in df_ho.columns:
                st.error("❌ Kolom 'WMS Order' (atau 'No WMS') tidak ditemukan di file HO Outbound.")
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

            col_sales = next((c for c in res.columns if 'sales channel' in c.lower()), None)
            res['Platform'] = res[col_sales] if col_sales else np.nan
            
            plat_is_na = res['Platform'].isna() | (res['Platform'].astype(str).str.strip() == '') | (res['Platform'].astype(str).str.lower() == 'nan')
            plat_order_str = res['PlatformOrder'].astype(str).str.strip()
            
            kondisi_ck = plat_is_na & plat_order_str.str.startswith("CK")
            kondisi_kosong = plat_is_na & (plat_order_str == "")
            
            res['Platform'] = np.where(
                kondisi_ck | kondisi_kosong, "Other",
                np.where(plat_is_na, "Webstore", res['Platform'])
            )

            is_platform_other = res['Platform'].astype(str).str.strip() == 'Other'

            erp_empty = res['ERP Document Number'].isna() | (res['ERP Document Number'].astype(str).str.strip() == '') | (res['ERP Document Number'].astype(str).str.lower() == 'nan')
            res['ERP Document Number'] = np.where(erp_empty & is_platform_other, res['WMS Order'], res['ERP Document Number'])

            track_empty = res['Tracking#/PRO#'].isna() | (res['Tracking#/PRO#'].astype(str).str.strip() == '') | (res['Tracking#/PRO#'].astype(str).str.lower() == 'nan')
            res['Tracking#/PRO#'] = np.where(track_empty & is_platform_other, res['WMS Order'], res['Tracking#/PRO#'])

            platord_empty = res['PlatformOrder'].isna() | (res['PlatformOrder'].astype(str).str.strip() == '') | (res['PlatformOrder'].astype(str).str.lower() == 'nan')
            res['PlatformOrder'] = np.where(platord_empty & is_platform_other, res['WMS Order'], res['PlatformOrder'])

            df_op = dfs['op_log']
            if not df_op.empty and 'Event' in df_op.columns and 'WMS Order#' in df_op.columns and 'operator' in df_op.columns:
                ev_col = df_op['Event']
                if isinstance(ev_col, pd.DataFrame): ev_col = ev_col.iloc[:, 0]
                op_col = df_op['operator']
                if isinstance(op_col, pd.DataFrame): op_col = op_col.iloc[:, 0]
                wms_op_col = df_op['WMS Order#']
                if isinstance(wms_op_col, pd.DataFrame): wms_op_col = wms_op_col.iloc[:, 0]
                
                df_clean_op = pd.DataFrame({
                    'WMS Order#': wms_op_col,
                    'Event': ev_col.astype(str).str.strip().str.lower(),
                    'operator': op_col
                })
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
                return s[:-2] if s.endswith('.0') else s

            col_store = next((c for c in res.columns if 'store number' in c.lower()), None)
            if col_store:
                res['Store number'] = res[col_store]
            else:
                res['Store number'] = np.nan
            
            if 'Store number' in res.columns:
                res['Brand'] = res['Store number'].apply(safe_key).map(lambda x: master_store_db.get(x, {}).get('Brand', np.nan))
                res['Brand 2'] = res['Store number'].apply(safe_key).map(lambda x: master_store_db.get(x, {}).get('Brand2', np.nan))
            else:
                res['Brand'] = np.nan
                res['Brand 2'] = np.nan
            
            brand_is_na = res['Brand'].isna() | (res['Brand'].astype(str).str.strip() == '') | (res['Brand'].astype(str).str.lower() == 'nan')
            brand2_is_na = res['Brand 2'].isna() | (res['Brand 2'].astype(str).str.strip() == '') | (res['Brand 2'].astype(str).str.lower() == 'nan')

            res['Brand'] = np.where(brand_is_na & is_platform_other, "SK", np.where(brand_is_na, "AceKid", res['Brand']))
            res['Brand 2'] = np.where(brand2_is_na & is_platform_other, "SK", np.where(brand2_is_na, "AceKid", res['Brand 2']))

            res['Platform & Brand 2'] = res['Platform'].fillna('').astype(str).str.strip() + " & " + res['Brand 2'].fillna('').astype(str).str.strip()
            res['Admin'] = current_admin

            # --- TAHAP 3: Kalkulasi Waktu & SLA (70%) ---
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
                def fix_date_only(val):
                    if pd.isna(val): return val
                    if isinstance(val, datetime.datetime):
                        return f"{val.month:02d}/{val.day:02d}/{val.year}"
                    return str(val)
                
                raw_tgl_ho = df_ho[ho_col_map['Tgl_HO']].apply(fix_date_only)
                res['Tanggal Handover'] = pd.to_datetime(raw_tgl_ho, errors='coerce', dayfirst=True).dt.strftime('%m/%d/%Y')
            else:
                res['Tanggal Handover'] = np.nan
            
            if 'Expedisi' in ho_col_map:
                res['Kurir'] = df_ho[ho_col_map['Expedisi']].apply(safe_key).map(lambda x: master_carrier_db.get(x, x))
            else:
                res['Kurir'] = np.nan

            col_wave = next((c for c in res.columns if c.lower() == 'wave' or 'wave id' in c.lower()), None)
            col_created = next((c for c in res.columns if 'created date' in c.lower() and 'wave' not in c.lower() and 'picking' not in c.lower()), None)
            col_ordered = next((c for c in res.columns if 'ordered date' in c.lower()), None)
            col_pick_created = next((c for c in res.columns if 'picking task created' in c.lower()), None)

            res['Wave ID'] = res[col_wave] if col_wave else np.nan
            res['Created Time'] = res[col_created] if col_created else np.nan
            res['Ordered Date'] = res[col_ordered] if col_ordered else np.nan
            
            if col_pick_created:
                def get_last_picking_time(x):
                    if pd.isna(x): return x
                    x_str = str(x).strip()
                    if ',' in x_str:
                        return x_str.split(',')[-1].strip()
                    return x_str
                res['Picking Task Created Time'] = res[col_pick_created].apply(get_last_picking_time)
            else:
                res['Picking Task Created Time'] = np.nan

            df_pack = dfs['pack_task']
            col_pack_order = next((c for c in df_pack.columns if 'order#' in c.lower()), None) if not df_pack.empty else None
            if col_pack_order:
                df_pack = df_pack.drop_duplicates(subset=[col_pack_order])
                df_pack = df_pack.loc[:, ~df_pack.columns.duplicated()]
                col_released = next((c for c in df_pack.columns if 'released date' in c.lower()), None)
                col_close = next((c for c in df_pack.columns if 'close date' in c.lower()), None)
                
                cols_pack_merge = [col_pack_order]
                if col_released: cols_pack_merge.append(col_released)
                if col_close: cols_pack_merge.append(col_close)
                    
                res_pack_m = res[['WMS Order']].merge(df_pack[cols_pack_merge], left_on='WMS Order', right_on=col_pack_order, how='left')
                res['pickCompletedTime - Released Date Pack'] = res_pack_m[col_released] if col_released else np.nan
                res['Packing Complete'] = res_pack_m[col_close] if col_close else np.nan
            else:
                res['pickCompletedTime - Released Date Pack'] = np.nan
                res['Packing Complete'] = np.nan

            col_shipped = next((c for c in res.columns if 'shipped date' in c.lower()), None)
            col_endship = next((c for c in res.columns if 'end ship date' in c.lower()), None)
            
            res['Shipped Date'] = res[col_shipped] if col_shipped else np.nan
            
            if 'Waktu_HO' in ho_col_map:
                def fix_ho_date(val):
                    if pd.isna(val): return val
                    if isinstance(val, datetime.datetime):
                        return f"{val.year}-{val.month:02d}-{val.day:02d} {val.hour:02d}:{val.minute:02d}:{val.second:02d}"
                    return str(val)
                
                raw_ho = df_ho[ho_col_map['Waktu_HO']].apply(fix_ho_date)
                parsed_ho = pd.to_datetime(raw_ho, errors='coerce')
                res['Handover Date'] = parsed_ho.dt.strftime('%Y-%m-%d %H:%M:%S')
                res['Handover_Date_Raw'] = parsed_ho
            else:
                res['Handover Date'] = np.nan
                res['Handover_Date_Raw'] = pd.NaT

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
            res['End Ship Date to Shipped Date'] = format_timedelta_hhmmss(to_dt('End Ship Date') - to_dt('Shipped Date'))

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
            max_sec = df_sec.max(axis=1)
            
            max_is_neg = max_sec < 0
            max_sec_abs = abs(max_sec)
            mh = (max_sec_abs // 3600).astype(int)
            mm = ((max_sec_abs % 3600) // 60).astype(int)
            ms = (max_sec_abs % 60).astype(int)
            res['Max'] = mh.astype(str).str.zfill(2) + ":" + mm.astype(str).str.zfill(2) + ":" + ms.astype(str).str.zfill(2)
            res['Max'] = np.where(max_is_neg, "-" + res['Max'], res['Max'])

            res['System'] = np.nan
            res['Admin_Akhir'] = np.nan
            res['Picker'] = np.nan
            res['Packer'] = np.nan
            res['Outbound'] = np.nan
            res['Kurir_Akhir'] = np.nan
            res['Late Proses By'] = np.nan
            
            # --- TAHAP 4: Menyusun Kolom Final & Export Excel (90%) ---
            progress_bar.progress(90, text="Processing... (Menyusun laporan akhir & Excel) [90%]")
            kolom_final = [
                'WMS Order', 'ERP Document Number', 'Tracking#/PRO#', 'PlatformOrder', 'Staged User', 
                'Platform', 'Brand', 'Brand 2', 'Platform & Brand 2', 'Admin', 'Load', 'Kurir', 'Loader', 'Tanggal Handover', 
                'Wave ID', 'Created Time', 'Ordered Date', 'Picking Task Created Time', 
                'pickCompletedTime - Released Date Pack', 'Packing Complete', 'Shipped Date', 'Handover Date', 
                'End Ship Date', 'Packing to Shipped Date', 'Packing to Handover', 'Shipped Date to Handover', 
                'End Ship Date to Shipped Date', 'Kota', 'Provinsi', 'Status', 'Payment Menthood', 
                'total order amount', 'Dokumen', 'Attachment', 'Times Proses Kurir', 'Times Proses Kurir to Shpped Date', 
                'Status Manifest', 'Status Late', 'Remark Late', 'Pay-Created', 'Created-Released', 'Released-Pick', 
                'Pick-Pack', 'Pack-Collect', 'Collect-Manifest', 'Manifest-Endshipdate', 'Max', 'System', 'Admin_Akhir', 
                'Picker', 'Packer', 'Outbound', 'Kurir_Akhir', 'Late Proses By'
            ]
            
            for col in kolom_final:
                if col not in res.columns: res[col] = np.nan
            final_df = res[kolom_final].copy()

            final_df = final_df.rename(columns={'Admin_Akhir': 'Admin', 'Kurir_Akhir': 'Kurir'})
            final_df = final_df.loc[:, ~final_df.columns.duplicated()]

            # --- MAPPING MASTER TRACKING STATUS ---
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

            # Export Excel
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

                for col_num, value in enumerate(df_to_export.columns.values):
                    worksheet_wms.write(0, col_num, value, format_header)
                    worksheet_wms.set_column(col_num, col_num, 16)

                # ==========================================
                # SHEET DB (DASHBOARD SUMMARY)
                # ==========================================
                worksheet_db = workbook.add_worksheet('DB')
                header_format_db = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3', 'border': 1, 'align': 'center'})
                cell_format_db = workbook.add_format({'border': 1, 'align': 'center'})
                cell_format_left = workbook.add_format({'border': 1, 'align': 'left'})
                black_divider = workbook.add_format({'bg_color': '#000000'})
                
                df_brand = final_df['Brand'].value_counts().reset_index()
                df_brand.columns = ['Brand', 'Delivered']
                df_brand.insert(0, 'No', range(1, len(df_brand) + 1))
                df_brand['Target'] = 0 
                
                df_kurir = final_df['Kurir'].value_counts().reset_index()
                df_kurir.columns = ['Courier_Name', 'Total_Package']
                df_kurir = df_kurir.head(5)
                df_kurir.insert(0, 'No', range(1, len(df_kurir) + 1))
                df_kurir['Ranking'] = range(1, len(df_kurir) + 1)
                
                df_status = final_df['Status Manifest'].replace('', 'Unknown').value_counts().reset_index()
                df_status.columns = ['Status_Manifest', 'qty']
                df_status.insert(0, 'No', range(1, len(df_status) + 1))

                # --- REVISI KALKULASI METRICS SUMMARY ---
                df_os_open = dfs.get('order_summary_open', dfs.get('order_summary', pd.DataFrame()))
                col_ref_sum = next((c for c in df_os_open.columns if 'ref#' in c.lower()), None)
                val_target = df_os_open[col_ref_sum].astype(str).str.strip().replace('', np.nan).replace('nan', np.nan).dropna().nunique() if col_ref_sum else 0
                
                val_delivered = len(final_df)
                val_delivery_rate = round((val_delivered / val_target * 100), 2) if val_target > 0 else 0.0

                raw_ho_df = dfs.get('ho_outbound', pd.DataFrame())

                # Pending Order (Pencarian Kolom Fleksibel)
                val_pending = 0
                col_pending = next((c for c in raw_ho_df.columns if 'pending' in c.lower()), None)
                if col_pending:
                    val_pending = int(pd.to_numeric(raw_ho_df[col_pending].astype(str).str.replace(r'[^\d.-]', '', regex=True), errors='coerce').fillna(0).sum())

                # Average Times
                def get_avg_time_str(series_hhmmss):
                    if series_hhmmss is None or series_hhmmss.empty:
                        return "0:00:00"
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

                # Kurir Instan (Pencocokan Kata Kunci Fleksibel)
                val_kurir_instan = 0
                col_deliveree_qty = next((c for c in raw_ho_df.columns if 'deliveree' in c.lower() or 'qty' in c.lower()), None)
                col_expedisi_ho = next((c for c in raw_ho_df.columns if any(k in c.lower() for k in ['expedisi', 'kurir', 'carrier', 'ekspedisi'])), None)

                if col_expedisi_ho and col_deliveree_qty:
                    courier_series = raw_ho_df[col_expedisi_ho].astype(str).str.lower()
                    qty_series = pd.to_numeric(raw_ho_df[col_deliveree_qty].astype(str).str.replace(r'[^\d.-]', '', regex=True), errors='coerce').fillna(0)
                    
                    pattern = r'anteraja|grab|gojek|go-jek|shopee|paxel|instant|sameday'
                    mask_instan = courier_series.str.contains(pattern, regex=True, na=False)
                    val_kurir_instan = int(qty_series[mask_instan].sum())

                # Lookup Category: JC Enabler & JC Fulfilment (Perbaikan Swapped Logic & Flexible Match)
                def lookup_category_from_master(row):
                    pb2_val = str(row.get('Platform & Brand 2', '')).strip().upper()
                    p_val = str(row.get('Platform', '')).strip().upper()
                    b2_val = str(row.get('Brand 2', '')).strip().upper()
                    
                    if pb2_val in master_category_map:
                        return master_category_map[pb2_val]
                    elif (p_val, b2_val) in master_category_map:
                        return master_category_map[(p_val, b2_val)]
                    return "Other"

                final_df['Master_Category'] = final_df.apply(lookup_category_from_master, axis=1)
                cat_series = final_df['Master_Category'].astype(str).str.lower()

                mask_enabler = cat_series.str.contains('enabler', na=False)
                mask_fulfilment = cat_series.str.contains('fulfil|center', regex=True, na=False) & ~mask_enabler

                val_jc_enabler = int(mask_enabler.sum())
                val_jc_fulfilment = int(mask_fulfilment.sum())
                val_other = int((~mask_enabler & ~mask_fulfilment).sum())

                # Status Tracking
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
                    [8, "jc_enabler", f"{val_jc_enabler:,}", "Lookup Master: Jet Commerce Enabler"],
                    [9, "jc_fulfilment", f"{val_jc_fulfilment:,}", "Lookup Master: Jet Commerce Fulfillment Center"],
                    [10, "other", f"{val_other:,}", "Lookup Master: Kategori lainnya"],
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
                
                worksheet_db.set_column('E:E', 2, black_divider)
                worksheet_db.set_column('K:K', 2, black_divider)
                worksheet_db.set_column('Q:Q', 2, black_divider)
                worksheet_db.set_column('T:T', 2, black_divider)
                
                worksheet_db.set_column('A:A', 5)
                worksheet_db.set_column('B:B', 18)
                worksheet_db.set_column('C:C', 12)
                worksheet_db.set_column('D:D', 35)

                worksheet_db.set_column('F:F', 5)
                worksheet_db.set_column('G:G', 18)
                worksheet_db.set_column('H:I', 12)
                
                worksheet_db.set_column('L:L', 5)
                worksheet_db.set_column('M:M', 25)
                worksheet_db.set_column('N:O', 15)
                
                worksheet_db.set_column('U:U', 5)
                worksheet_db.set_column('V:V', 15)
                worksheet_db.set_column('W:W', 10)

            st.session_state['excel_data'] = output.getvalue()
            progress_bar.progress(100, text="Processing Selesai! (100%)")
            progress_bar.empty()

        except Exception as e:
            st.error(f"❌ Terjadi kesalahan Sistem: {e}")
            st.code(traceback.format_exc())
    else:
        st.warning("Silakan unggah file sumber terlebih dahulu di area Data Center.")

# ==========================================
# 6. TAMPILAN PREVIEW & NOTIFIKASI
# ==========================================
if 'processed_result' in st.session_state:
    res_df = st.session_state['processed_result']
    st.success(f"✅ Berhasil memproses total {len(res_df)} baris data!")

    if 'Master_Tracking' in res_df.columns:
        untraceable_data = res_df[res_df['Master_Tracking'] == 'untraceable']
        untraceable_count = len(untraceable_data)
        
        if untraceable_count > 0:
            st.warning(f"⚠️ **PERINGATAN DATA UNTRACEABLE:** Ditemukan **{untraceable_count}** paket dengan status **Untraceable**!")
            
            with st.expander("🔍 **Summary Preview Data Untraceable (Klik untuk buka/tutup)**", expanded=True):
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
            st.info("🎉 Seluruh paket berstatus **Traceable** (0 Untraceable).")

    display_df = res_df.drop(columns=['Master_Tracking'], errors='ignore')
    st.markdown("### 📊 Preview Hasil Data Outbound")
    st.dataframe(display_df, use_container_width=True)

    st.download_button(
        label="📥 Download Laporan Excel",
        data=st.session_state['excel_data'],
        file_name="Laporan_Daily_HO_Outbound.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary"
    )
