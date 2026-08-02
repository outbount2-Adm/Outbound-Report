import streamlit as st
import pandas as pd
import numpy as np
import traceback
import datetime
from io import BytesIO

# --- KONFIGURASI HALAMAN MODERN ---
st.set_page_config(
    page_title="Report Outbound Modern Dashboard", 
    layout="wide", 
    page_icon="📦"
)

# --- CSS KUSTOM UNTUK TAMPILAN MODERN & CLEAN UI ---
modern_css = """
<style>
    /* Mengubah background utama menjadi abu-abu sangat lembut khas dashboard modern */
    .stApp {
        background-color: #F8F9FA;
    }
    
    /* Menyembunyikan elemen bawaan Streamlit secara total */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    [data-testid="viewerBadge"] {display: none !important;}

    /* Styling Judul Utama */
    h1 {
        color: #1E293B;
        font-weight: 800;
        letter-spacing: -0.5px;
    }
    
    /* Styling Subheader */
    h3 {
        color: #334155;
        font-weight: 600;
        font-size: 1.25rem !important;
    }

    /* Membuat Container / Card Modern */
    .css-1r6slb0, .element-container, [data-testid="stVerticalBlock"] > div {
        border-radius: 12px;
    }
    
    /* Tombol Utama (Primary Button) */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.6rem 1.2rem;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
        transition: all 0.3s ease;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #1D4ED8 0%, #1E40AF 100%);
        box-shadow: 0 6px 8px -1px rgba(37, 99, 235, 0.3);
    }

    /* Tombol Sekunder / Clear Data */
    .stButton > button[kind="secondary"] {
        background-color: #F1F5F9;
        color: #475569;
        border: 1px solid #CBD5E1;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton > button[kind="secondary"]:hover {
        background-color: #E2E8F0;
        color: #1E293B;
    }

    /* Kotak File Uploader */
    [data-testid="stFileUploader"] {
        background-color: #FFFFFF;
        border: 2px dashed #CBD5E1;
        border-radius: 12px;
        padding: 20px;
        transition: border-color 0.2s ease;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #2563EB;
    }
</style>
"""
st.markdown(modern_css, unsafe_allow_html=True)

# --- HEADER SECTION ---
st.title("📦 Report Outbound Dashboard")
st.markdown("Sistem otomatisasi modern untuk pengolahan data Logistik, WMS, ERP, dan SLA Outbound.")
st.divider()

# ==========================================
# PENGATURAN ADMIN (CARD SECTION)
# ==========================================
st.subheader("👤 Pengaturan Admin")
with st.container():
    col_adm1, col_adm2 = st.columns([3, 1])
    with col_adm1:
        admin_input_temp = st.text_input("Nama Admin yang Bertugas:", value="Admin Logistik", label_visibility="collapsed")
    with col_adm2:
        submit_admin = st.button("Simpan Admin", kind="secondary", use_container_width=True)

# Simpan nama admin yang disubmit
if 'saved_admin' not in st.session_state:
    st.session_state['saved_admin'] = "Admin Logistik"

if submit_admin:
    st.session_state['saved_admin'] = admin_input_temp
    st.success(f"Berhasil disimpan: {st.session_state['saved_admin']}")

current_admin = st.session_state['saved_admin']
st.write("")

# ==========================================
# UPLOAD DATA & CLEAR DATA (CARD SECTION)
# ==========================================
st.subheader("📂 Unggah Data Sumber")

if 'file_uploader_key' not in st.session_state:
    st.session_state['file_uploader_key'] = 0

col_up1, col_up2 = st.columns([5, 1])
with col_up1:
    uploaded_files = st.file_uploader(
        "Unggah file (.xlsx / .csv) sekaligus (Order Summary, Operation Log, ERP, HO Outbound, Pack Task, Master):", 
        accept_multiple_files=True, 
        type=['xlsx', 'csv'],
        key=f"file_uploader_{st.session_state['file_uploader_key']}"
    )

with col_up2:
    st.write("") 
    st.write("") 
    if st.button("🗑️ Clear Data", kind="secondary", use_container_width=True):
        st.session_state['file_uploader_key'] += 1
        st.rerun()

st.write("")

if uploaded_files:
    col_btn1, col_btn2, col_btn3 = st.columns([2, 2, 4])
    with col_btn1:
        generate_clicked = st.button("⚡ Generated Data", kind="primary", use_container_width=True)
    
    if generate_clicked:
        with st.spinner("⏳ Sedang memproses file, mencocokkan baris, dan mengkalkulasi data..."):
            try:
                # --- A. IDENTIFIKASI FILE BERDASARKAN NAMA ---
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
                        dfs['master'] = df
                    
                    elif 'ho outbound' in file_name: 
                        rename_map = {}
                        for col in df.columns:
                            c_lower = col.lower()
                            if 'no wms' in c_lower: rename_map[col] = 'WMS Order'
                            elif 'expedisi' in c_lower: rename_map[col] = 'Expedisi'
                            elif c_lower == 'tanggal': rename_map[col] = 'Tgl_HO_Source'
                        df = df.rename(columns=rename_map)
                        dfs['ho_outbound'] = df
                        
                    elif 'order summary' in file_name: dfs['order_summary'] = df
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
                    st.error("❌ File 'HO Outbound' tidak ditemukan. Pastikan nama file mengandung kata 'HO Outbound'.")
                    st.stop()
                if 'order_summary' not in dfs:
                    st.error("❌ File 'Order Summary' tidak ditemukan. Pastikan nama file mengandung kata 'Order Summary'.")
                    st.stop()
                if 'master' not in dfs:
                    st.warning("⚠️ File 'Master' tidak ditemukan. Kolom Brand dan Kurir akan menggunakan nilai fallback.")

                for key in ['op_log', 'pack_task', 'erp']:
                    if key not in dfs: dfs[key] = pd.DataFrame()

                # --- B. BASIS DATA MENGIKUTI SELURUH ROW HO OUTBOUND ---
                df_ho = dfs['ho_outbound'].copy()
                if 'WMS Order' not in df_ho.columns:
                    st.error(f"❌ Kolom 'WMS Order' (atau 'No WMS') tidak ditemukan di file HO Outbound.")
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
                kondisi_platform_other = res['Platform'].astype(str).str.strip() == 'Other'

                res['Brand'] = np.where(brand_is_na & kondisi_platform_other, "SK", np.where(brand_is_na, "AceKid", res['Brand']))
                res['Brand 2'] = np.where(brand2_is_na & kondisi_platform_other, "SK", np.where(brand2_is_na, "AceKid", res['Brand 2']))

                res['Admin'] = current_admin

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
                            return f"{val.month:02d}/{val.day:02d}/{val.year} {val.hour:02d}:{val.minute:02d}:{val.second:02d}"
                        return str(val)
                    
                    raw_ho = df_ho[ho_col_map['Waktu_HO']].apply(fix_ho_date)
                    parsed_ho = pd.to_datetime(raw_ho, errors='coerce', dayfirst=True)
                    res['Handover Date'] = parsed_ho.dt.strftime('%m/%d/%Y %H:%M:%S')
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

                col_attach = ho_col_map.get('Attachment', None)
                res['Attachment'] = df_ho[col_attach].apply(lambda x: str(x).strip() if pd.notna(x) else '') if col_attach else np.nan
                is_no_attach = res['Attachment'].replace({0: np.nan, '0': np.nan, '': np.nan}).isna()
                res['Dokumen'] = np.where(is_no_attach, 'Not yet Input', 'YES')

                res['Times Proses Kurir to Shipped Date'] = format_timedelta_hhmmss(to_dt('Times Proses Kurir') - to_dt('Shipped Date'))

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
                
                kolom_final = [
                    'WMS Order', 'ERP Document Number', 'Tracking#/PRO#', 'PlatformOrder', 'Staged User', 
                    'Platform', 'Brand', 'Brand 2', 'Admin', 'Load', 'Kurir', 'Loader', 'Tanggal Handover', 
                    'Wave ID', 'Created Time', 'Ordered Date', 'Picking Task Created Time', 
                    'pickCompletedTime - Released Date Pack', 'Packing Complete', 'Shipped Date', 'Handover Date', 
                    'End Ship Date', 'Packing to Shipped Date', 'Packing to Handover', 'Shipped Date to Handover', 
                    'End Ship Date to Shipped Date', 'Kota', 'Provinsi', 'Status', 'Payment Menthood', 
                    'total order amount', 'Dokumen', 'Attachment', 'Times Proses Kurir', 'Times Proses Kurir to Shipped Date', 
                    'Status Manifest', 'Status Late', 'Remark Late', 'Pay-Created', 'Created-Released', 'Released-Pick', 
                    'Pick-Pack', 'Pack-Collect', 'Collect-Manifest', 'Manifest-Endshipdate', 'Max', 'System', 'Admin_Akhir', 
                    'Picker', 'Packer', 'Outbound', 'Kurir_Akhir', 'Late Proses By'
                ]
                
                for col in kolom_final:
                    if col not in res.columns: res[col] = np.nan
                final_df = res[kolom_final].copy()

                final_df = final_df.rename(columns={'Admin_Akhir': 'Admin', 'Kurir_Akhir': 'Kurir'})
                final_df = final_df.loc[:, ~final_df.columns.duplicated()]
                final_df.insert(0, 'No', range(1, len(final_df) + 1))

                # --- HASIL & PREVIEW DATA ---
                st.success(f"✨ Berhasil memproses total **{len(final_df)}** baris data dengan akurat!")
                st.dataframe(final_df, use_container_width=True, height=450)

                # --- EXPORT EXCEL ---
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    final_df.to_excel(writer, index=False, sheet_name='Laporan_WMS')
                    workbook = writer.book
                    worksheet = writer.sheets['Laporan_WMS']
                    format_header = workbook.add_format({'bold': True, 'bg_color': '#E2E8F0', 'border': 1})
                    
                    col_idx_track = list(final_df.columns).index('Tracking#/PRO#')
                    col_idx_plat = list(final_df.columns).index('PlatformOrder')
                    
                    for row_num in range(len(final_df)):
                        val_track = str(final_df.iloc[row_num]['Tracking#/PRO#'])
                        val_plat = str(final_df.iloc[row_num]['PlatformOrder'])
                        
                        if val_track != 'nan' and val_track != '':
                            worksheet.write_string(row_num + 1, col_idx_track, val_track)
                        if val_plat != 'nan' and val_plat != '':
                            worksheet.write_string(row_num + 1, col_idx_plat, val_plat)

                    for col_num, value in enumerate(final_df.columns.values):
                        worksheet.write(0, col_num, value, format_header)
                        worksheet.set_column(col_num, col_num, 16)

                processed_data = output.getvalue()
                
                st.write("")
                st.download_button(
                    label="📥 Download Laporan Excel",
                    data=processed_data,
                    file_name="Laporan_Daily_HO_Outbound.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary"
                )

            except Exception as e:
                st.error(f"❌ Terjadi kesalahan Sistem: {e}")
                st.code(traceback.format_exc())
