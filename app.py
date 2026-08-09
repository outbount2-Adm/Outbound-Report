import streamlit as st
import pandas as pd
import numpy as np
import traceback
import datetime
import altair as alt
from io import BytesIO

# ==========================================
# 1. KONFIGURASI HALAMAN MODERN
# ==========================================
st.set_page_config(
    page_title="Outbound Auto-Processor", 
    layout="wide", 
    page_icon="📦", 
    initial_sidebar_state="expanded"
)

current_date = datetime.datetime.now().strftime("%B %d, %Y")

# ==========================================
# 2. CSS KUSTOM PROFESIONAL (Inter Font & Modern Slate Theme)
# ==========================================
custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp { 
        background-color: #F8FAFC; 
    }

    #MainMenu, footer, header, .stDeployButton, [data-testid="viewerBadge"] {
        visibility: hidden !important; 
        display: none !important;
    }

    .block-container {
        padding-top: 2rem !important;
        max-width: 1400px;
        margin: auto;
    }

    /* Typography */
    h1 {
        color: #1E293B;
        font-weight: 800;
        letter-spacing: -0.025em;
        font-size: 2.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    h3 {
        color: #334155;
        font-weight: 700;
        font-size: 1.25rem !important;
        margin-bottom: 1rem !important;
    }

    .subtitle {
        color: #64748B;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }

    /* Cards */
    .modern-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
        margin-bottom: 1.5rem;
    }

    /* Metrics */
    .metric-card {
        background: white;
        padding: 1.25rem;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        text-align: center;
    }
    .metric-label {
        color: #64748B;
        font-size: 0.875rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        color: #0F172A;
        font-size: 1.875rem;
        font-weight: 700;
        margin-top: 0.25rem;
    }

    /* Inputs & Buttons */
    [data-testid="stTextInput"] > div > div > input {
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        padding: 0.5rem 0.75rem !important;
    }

    [data-testid="stFileUploader"] {
        border: 2px dashed #CBD5E1 !important;
        border-radius: 12px !important;
        padding: 2rem !important;
        background-color: #F8FAFC !important;
    }

    div[data-testid="stButton"] > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s;
    }

    div[data-testid="stButton"] > button[kind="primary"] {
        background-color: #2563EB !important;
        border: none !important;
        padding: 0.75rem 1.5rem !important;
    }

    div[data-testid="stButton"] > button[kind="primary"]:hover {
        background-color: #1D4ED8 !important;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
    }

    /* Status Badges */
    .badge {
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-success { background-color: #DCFCE7; color: #166534; }
    .badge-warning { background-color: #FEF3C7; color: #92400E; }
    .badge-error { background-color: #FEE2E2; color: #991B1B; }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #F1F5F9;
        border-right: 1px solid #E2E8F0;
    }
    .sidebar-header {
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 1rem;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# 3. SIDEBAR - SETTINGS & INFO
# ==========================================
with st.sidebar:
    st.markdown('<div class="sidebar-header">⚙️ Konfigurasi</div>', unsafe_allow_html=True)
    
    if 'saved_admin' not in st.session_state:
        st.session_state['saved_admin'] = "Admin Logistik"
    
    admin_input = st.text_input("Nama Officer Aktif", value=st.session_state['saved_admin'])
    if st.button("Simpan Perubahan", use_container_width=True):
        st.session_state['saved_admin'] = admin_input
        st.toast("Nama officer diperbarui!", icon="✅")
    
    st.divider()
    
    st.markdown('<div class="sidebar-header">📖 Panduan Singkat</div>', unsafe_allow_html=True)
    st.info("""
    1. **Upload** file Master, Daily, HO, dan Order Summary.
    2. Klik **Proses Data** untuk memulai.
    3. **Review** hasil pada tabel preview.
    4. **Download** laporan Excel yang sudah diformat.
    """)
    
    st.divider()
    
    if st.button("🗑️ Reset Semua Data", use_container_width=True, type="secondary"):
        if 'file_uploader_key' not in st.session_state: st.session_state['file_uploader_key'] = 0
        st.session_state['file_uploader_key'] += 1
        if 'processed_result' in st.session_state: del st.session_state['processed_result']
        if 'excel_data' in st.session_state: del st.session_state['excel_data']
        st.rerun()

# ==========================================
# 4. MAIN CONTENT - HEADER
# ==========================================
col_h1, col_h2 = st.columns([2, 1])
with col_h1:
    st.markdown('<h1>Outbound Auto-Processor</h1>', unsafe_allow_html=True)
    st.markdown(f'<div class="subtitle">Logistics Automation Dashboard • {current_date}</div>', unsafe_allow_html=True)
with col_h2:
    st.markdown(f"""
        <div style="text-align: right; padding-top: 1rem;">
            <span style="color: #64748B; font-size: 0.9rem;">Officer:</span><br>
            <span style="color: #0F172A; font-weight: 700; font-size: 1.1rem;">{st.session_state['saved_admin']}</span>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 5. DATA CENTER (UPLOAD)
# ==========================================
st.markdown('<div class="modern-card">', unsafe_allow_html=True)
st.markdown('<h3>📁 Data Center</h3>', unsafe_allow_html=True)

if 'file_uploader_key' not in st.session_state:
    st.session_state['file_uploader_key'] = 0

uploaded_files = st.file_uploader(
    "Seret dan lepas file sumber Anda (XLSX, CSV)", 
    accept_multiple_files=True, 
    type=['xlsx', 'csv'],
    key=f"uploader_{st.session_state['file_uploader_key']}",
    label_visibility="visible"
)
st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 6. PROCESSING QUEUE
# ==========================================
files_ready = len(uploaded_files) > 0
if files_ready:
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.markdown('<h3>⚙️ Pemrosesan Data</h3>', unsafe_allow_html=True)
    
    execute_clicked = st.button(
        "Mulai Proses Data 🚀", 
        type="primary", 
        use_container_width=True
    )

    if execute_clicked:
        progress_container = st.empty()
        progress_bar = st.progress(0)
        
        try:
            def update_progress(val, text):
                progress_bar.progress(val)
                progress_container.markdown(f"**Status:** {text} ({val}%)")

            update_progress(10, "Membaca file sumber...")
            
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

            update_progress(35, "Mencocokkan baris & Merge data...")
            
            # --- START LOGIC AS IS ---
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
                wms_col = df_op['WMS Order#'].iloc[:, 0] if isinstance(df_op['WMS Order#'], pd.DataFrame) else df_op['WMS Order#']
                
                mask_staged = ev_col.astype(str).str.strip().str.lower() == 'staged'
                df_staged = pd.DataFrame({'WMS Order#': wms_col[mask_staged], 'Staged User': op_col[mask_staged]})
                df_staged = df_staged.drop_duplicates(subset=['WMS Order#'])
                res = res.merge(df_staged, left_on='WMS Order', right_on='WMS Order#', how='left')
            else:
                res['Staged User'] = np.nan

            def safe_key(val):
                s = str(val).strip()
                if s.endswith('.0'): s = s[:-2]
                return s

            col_store_res = next((c for c in res.columns if 'store number' in c.lower() or c.lower() == 'storenumber' or 'store' in c.lower()), None)
            if col_store_res:
                res['Brand'] = res[col_store_res].apply(lambda x: master_store_db.get(safe_key(x), {}).get('Brand', 'SK') if safe_key(x) != "" else "SK")
                res['Brand 2'] = res[col_store_res].apply(lambda x: master_store_db.get(safe_key(x), {}).get('Brand2', 'SK') if safe_key(x) != "" else "SK")
            else:
                res['Brand'] = 'SK'; res['Brand 2'] = 'SK'

            res['Admin'] = st.session_state['saved_admin']
            res['Load'] = 1
            
            col_carrier_code = next((c for c in res.columns if 'carrier code' in c.lower() or 'carriercode' in c.lower()), None)
            if col_carrier_code:
                res['Kurir'] = res[col_carrier_code].apply(lambda x: master_carrier_db.get(str(x).strip(), 'Unknown'))
            else:
                res['Kurir'] = 'Unknown'

            res['Loader'] = st.session_state['saved_admin']
            res['Tanggal Handover'] = current_date
            
            update_progress(65, "Menghitung durasi & Status...")

            for c in ['Created Time', 'Ordered Date', 'Picking Task Created Time', 'pickCompletedTime - Released Date Pack', 'Packing Complete', 'Shipped Date', 'Handover Date', 'End Ship Date']:
                col_found = next((col for col in res.columns if col.lower() == c.lower()), None)
                if col_found: res[c] = res[col_found]
                else: res[c] = np.nan

            def calc_diff(c1, c2):
                if c1 in res.columns and c2 in res.columns:
                    t1 = pd.to_datetime(res[c1], errors='coerce')
                    t2 = pd.to_datetime(res[c2], errors='coerce')
                    diff = t1 - t2
                    return diff.apply(lambda x: f"{int(x.total_seconds()//3600)}:{(int(x.total_seconds()%3600)//60):02d}:{int(x.total_seconds()%60):02d}" if pd.notna(x) else "0:00:00")
                return "0:00:00"

            res['Packing to Shpped Date'] = calc_diff('Shipped Date', 'Packing Complete')
            res['Packing to Handover'] = calc_diff('Handover Date', 'Packing Complete')
            res['Shipped Date to Handover'] = calc_diff('Handover Date', 'Shipped Date')
            res['End Ship Date to Shpped Date'] = calc_diff('End Ship Date', 'Shipped Date')

            for col_name in ['Kota', 'Provinsi', 'Status', 'Payment Menthood', 'total order amount']:
                col_found = next((c for c in res.columns if c.lower() == col_name.lower()), None)
                if col_found: res[col_name] = res[col_found]
                else: res[col_name] = np.nan

            res['Dokumen'] = 'Sudah Ada'
            res['Attachment'] = 'Sudah Ada'
            res['Times Proses Kurir'] = calc_diff('Handover Date', 'Shipped Date')
            res['Times Proses Kurir to Shpped Date'] = calc_diff('Shipped Date', 'Handover Date')

            if 'Status' in res.columns:
                res['Status Manifest'] = np.where(res['Status'].astype(str).str.strip().str.lower() == 'shipped', 'Late', 'Normal')
            else:
                res['Status Manifest'] = 'Normal'

            res['Status Late'] = np.where(res['Status Manifest'] == 'Late', 'Late', 'Normal')
            res['Remark Late'] = ""

            res['Pay-Created'] = calc_diff('Created Time', 'Ordered Date')
            res['Created-Released'] = calc_diff('Picking Task Created Time', 'Created Time')
            res['Released-Pick'] = calc_diff('pickCompletedTime - Released Date Pack', 'Picking Task Created Time')
            res['Pick-Pack'] = calc_diff('Packing Complete', 'pickCompletedTime - Released Date Pack')
            res['Pack-Collect'] = calc_diff('Shipped Date', 'Packing Complete')
            res['Collect-Manifest'] = calc_diff('Handover Date', 'Shipped Date')
            res['Manifest-Endshipdate'] = calc_diff('End Ship Date', 'Handover Date')
            res['Max'] = ""
            res['System'] = ""

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

            update_progress(90, "Menyusun laporan akhir & Excel...")
            
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
                    formula_late_by = f'=IF(AV{excel_row}, "System", IF(AW{excel_row}, "Admin", IF(AX{excel_row}, "Picker", IF(AY{excel_row}, "Packer", IF(AZ{excel_row}, "Outbound", IF(BA{excel_row}, "Kurir", ""))))))'
                    worksheet_wms.write_formula(row_num + 1, 53, formula_late_by)

                for col_num, col_name in enumerate(df_to_export.columns):
                    worksheet_wms.write(0, col_num, col_name, format_header)
                    col_data_len = df_to_export.iloc[:, col_num].astype(str).str.len().max() if not df_to_export.empty else 0
                    header_len = len(str(col_name))
                    max_len = max(header_len, col_data_len)
                    worksheet_wms.set_column(col_num, col_num, max_len + 4, cell_format_center)

                # --- SHEET DB (SUMMARY) ---
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
                            if sn == "": os_mapped_brands.append("SK")
                            else:
                                store_info = master_store_db.get(sn, {})
                                b_val = store_info.get('Brand2', store_info.get('Brand', 'SK'))
                                os_mapped_brands.append(b_val if b_val else "SK")
                        if os_mapped_brands:
                            target_counts = pd.Series(os_mapped_brands).value_counts()
                            df_brand['Target'] = df_brand['Brand'].map(target_counts).fillna(0).astype(int)
                        else: df_brand['Target'] = 0
                    else: df_brand['Target'] = 0
                else: df_brand['Target'] = 0

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
                    courier_col_idx = -1; qty_col_idx = -1
                    for idx, c_name in enumerate(cols_lower):
                        if any(k in c_name for k in ['ekspedisi', 'kurir', 'courier', 'service']):
                            courier_col_idx = idx; break
                    if courier_col_idx == -1 and len(raw_daily_df.columns) > 0: courier_col_idx = 0
                    for idx, c_name in enumerate(cols_lower):
                        if any(k in c_name for k in ['deliveree', 'qty', 'total', 'order']):
                            if idx != courier_col_idx: qty_col_idx = idx; break
                    if courier_col_idx != -1 and qty_col_idx != -1:
                        c_col_name = raw_daily_df.columns[courier_col_idx]
                        q_col_name = raw_daily_df.columns[qty_col_idx]
                        target_kurir = ['go-jek/grab/shopee instant', 'anteraja sameday (rit 1)', 'anteraja sameday (rit 2)', 'anteraja sameday (rit 3)', 'paxel ( rit 1 )', 'paxel ( rit 2 )', 'paxel ( rit 3 )']
                        for _, r in raw_daily_df.iterrows():
                            c_val = str(r[c_col_name]).strip().lower()
                            if any(t in c_val for t in ['total', 'jumlah', 'sum']): continue
                            if any(tk == c_val for tk in target_kurir):
                                try: val_kurir_instan += int(float(str(r[q_col_name]).replace(',', '').strip()))
                                except: pass

                if val_kurir_instan == 0 and 'Kurir' in final_df.columns:
                    instan_list = ['go-jek/grab/shopee instant', 'anteraja sameday (rit 1)', 'anteraja sameday (rit 2)', 'anteraja sameday (rit 3)', 'paxel ( rit 1 )', 'paxel ( rit 2 )', 'paxel ( rit 3 )']
                    val_kurir_instan = int(final_df['Kurir'].astype(str).str.strip().str.lower().isin(instan_list).sum())

                brand2_series = final_df['Brand 2'].astype(str).str.strip().str.lower()
                platform_series = final_df['Platform'].astype(str).str.strip().str.lower()
                fulfilment_brands = ['dojako', 'firda', 'noura', "mama's choice", 'mamas choice']
                is_fulfilment = brand2_series.isin(fulfilment_brands)
                is_other = ((platform_series == 'webstore') & (brand2_series == 'acekid')) | ((platform_series == 'other') & (brand2_series == 'sk'))
                is_enabler = ~is_fulfilment & ~is_other
                val_jc_fulfilment = int(is_fulfilment.sum())
                val_other = int(is_other.sum())
                val_jc_enabler = int(is_enabler.sum())

                val_pending = 0
                if not raw_daily_df.empty:
                    col0 = raw_daily_df.columns[0]; col1 = raw_daily_df.columns[1] if len(raw_daily_df.columns) > 1 else col0
                    clean_daily = raw_daily_df[~(raw_daily_df[col0].astype(str).str.lower().str.contains('total', na=False) | raw_daily_df[col1].astype(str).str.lower().str.contains('total', na=False))]
                    col_pending = next((c for c in clean_daily.columns if 'cut off' in c.lower() or 'pending' in c.lower()), None)
                    if col_pending: val_pending = int(pd.to_numeric(clean_daily[col_pending].astype(str).str.replace(r'[^\d.-]', '', regex=True), errors='coerce').fillna(0).sum())

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
            st.session_state['metrics'] = {
                "Delivery Rate": f"{val_delivery_rate}%",
                "Delivered": f"{val_delivered:,}",
                "Target": f"{val_target:,}",
                "Pending": f"{val_pending:,}"
            }
            update_progress(100, "Selesai!")
            st.toast("Data berhasil diproses!", icon="🚀")

        except Exception as e:
            st.error(f"❌ Terjadi kesalahan Sistem: {e}")
            st.code(traceback.format_exc())
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 7. RESULTS DASHBOARD
# ==========================================
if 'processed_result' in st.session_state:
    res_df = st.session_state['processed_result']
    
    # Quick Metrics
    if 'metrics' in st.session_state:
        m = st.session_state['metrics']
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Delivery Rate</div><div class="metric-value">{m["Delivery Rate"]}</div></div>', unsafe_allow_html=True)
        with col_m2:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Delivered</div><div class="metric-value">{m["Delivered"]}</div></div>', unsafe_allow_html=True)
        with col_m3:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Target</div><div class="metric-value">{m["Target"]}</div></div>', unsafe_allow_html=True)
        with col_m4:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Pending</div><div class="metric-value">{m["Pending"]}</div></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📊 Analytics", "🔍 Untraceable Check", "📋 Data Preview"])
    
    with tab1:
        st.markdown("### 📈 Grafik Late Proses By & Kurir")
        if 'Status Manifest' in res_df.columns and 'Late Proses By' in res_df.columns and 'Kurir' in res_df.columns:
            late_df_web = res_df[res_df['Status Manifest'].astype(str).str.strip().str.lower() == 'late'].copy()
            if not late_df_web.empty:
                chart_df = late_df_web.groupby(['Kurir', 'Late Proses By']).size().reset_index(name='Qty')
                chart_df = chart_df.sort_values(by='Qty', ascending=False)
                base = alt.Chart(chart_df).encode(
                    y=alt.Y('Kurir:N', sort='-x', title='Kurir'),
                    x=alt.X('Qty:Q', title='Jumlah Order (Qty)'),
                    color=alt.Color('Late Proses By:N', scale=alt.Scale(scheme='tableau10'), title='Late Proses By')
                )
                bars = base.mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
                text = base.mark_text(align='left', dx=5, fontWeight='bold').encode(text='Qty:Q')
                st.altair_chart((bars + text).properties(height=400), use_container_width=True)
            else:
                st.info("ℹ️ Tidak ada data dengan status manifest 'Late'.")
        
    with tab2:
        if 'Master_Tracking' in res_df.columns:
            untraceable_data = res_df[res_df['Master_Tracking'] == 'untraceable'].copy()
            untraceable_count = len(untraceable_data)
            
            if untraceable_count > 0:
                st.markdown(f'<span class="badge badge-warning">⚠️ {untraceable_count} Paket Untraceable</span>', unsafe_allow_html=True)
                col_u1, col_u2 = st.columns([1, 2])
                with col_u1:
                    st.markdown("**Ringkasan per Status:**")
                    status_summary = untraceable_data['Status'].value_counts().reset_index()
                    status_summary.columns = ['Status', 'Jumlah']
                    st.dataframe(status_summary, use_container_width=True, hide_index=True)
                with col_u2:
                    st.markdown("**Detail Paket:**")
                    cols_to_show = [c for c in ['No', 'WMS Order', 'ERP Document Number', 'Platform', 'Kurir', 'Status', 'Tracking#/PRO#'] if c in untraceable_data.columns]
                    st.dataframe(untraceable_data[cols_to_show], use_container_width=True, hide_index=True)
            else:
                st.success("🎉 Seluruh paket berstatus Traceable!")

    with tab3:
        essential_cols = ['WMS Order', 'ERP Document Number', 'Tracking#/PRO#', 'Platform', 'Kurir', 'Status']
        empty_report = []
        for col in essential_cols:
            if col in res_df.columns:
                missing_count = (res_df[col].isna() | (res_df[col].astype(str).str.strip() == '') | res_df[col].astype(str).str.strip().str.lower().isin(['nan', 'none', 'null', 'nat'])).sum()
                if missing_count > 0: empty_report.append(f"**{col}**: {missing_count} baris kosong")
        
        if empty_report:
            with st.expander("🚨 Peringatan Data Kosong"):
                for rep in empty_report: st.write(f"- {rep}")
        
        display_df = res_df.drop(columns=['Master_Tracking'], errors='ignore')
        st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.divider()
    
    col_d1, col_d2, col_d3 = st.columns([1, 1, 1])
    with col_d2:
        st.download_button(
            label="📥 Download Laporan Excel",
            data=st.session_state['excel_data'],
            file_name=f"Laporan_Outbound_{datetime.datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
