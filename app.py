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
    page_title="QianYi Style Dashboard", 
    layout="wide", 
    page_icon="📦", 
    initial_sidebar_state="expanded"
)

current_date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ==========================================
# 2. CSS KUSTOM (QianYi Design System)
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

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #001529 !important;
        color: white !important;
    }
    [data-testid="stSidebar"] * {
        color: #A6ADB4 !important;
    }
    .sidebar-active {
        background-color: #1890FF !important;
        color: white !important;
        border-radius: 4px;
        padding: 10px;
        margin-bottom: 5px;
    }
    .sidebar-item {
        padding: 10px;
        margin-bottom: 5px;
        cursor: pointer;
    }

    /* Top Bar / Header */
    .top-bar {
        background-color: white;
        padding: 10px 20px;
        border-bottom: 1px solid #E8E8E8;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }

    /* Section Cards */
    .section-container {
        background-color: white;
        border-radius: 4px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    .section-title {
        font-size: 16px;
        font-weight: 600;
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
        margin-bottom: 20px;
    }
    .todo-card {
        border-radius: 4px;
        padding: 15px;
        color: white;
        min-height: 100px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .todo-card-teal { background: linear-gradient(135deg, #26C1C9 0%, #19A7AF 100%); }
    .todo-card-blue { background: linear-gradient(135deg, #4B7CF3 0%, #3A62D7 100%); }
    
    .todo-label { font-size: 13px; font-weight: 400; opacity: 0.9; line-height: 1.2; }
    .todo-value { font-size: 24px; font-weight: 700; margin-top: 10px; }

    /* Stats Row Styling */
    .stats-row {
        display: flex;
        justify-content: space-around;
        text-align: center;
        padding: 10px 0;
    }
    .stat-item { flex: 1; border-right: 1px solid #F0F0F0; }
    .stat-item:last-child { border-right: none; }
    .stat-label { color: #8C8C8C; font-size: 13px; margin-bottom: 8px; }
    .stat-value { color: #1890FF; font-size: 22px; font-weight: 600; }

    /* Form Inputs */
    [data-testid="stTextInput"] > div > div > input {
        border-radius: 4px;
        border: 1px solid #D9D9D9;
    }
    
    /* Buttons */
    div[data-testid="stButton"] > button {
        border-radius: 4px !important;
        font-weight: 500 !important;
    }
    
    /* Hide default elements */
    #MainMenu, footer, header, .stDeployButton { visibility: hidden; display: none; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# 3. SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.markdown('<div style="font-size: 24px; font-weight: 800; color: white; margin-bottom: 30px; padding: 0 10px;">📦 QianYi Logis</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="sidebar-active">📊 Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-item">📝 Task Management</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-item">👥 User Management</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-item">📂 Master Data</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-item">📥 Inbound</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-item">📤 Outbound</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-item">🏠 Storage</div>', unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown('### ⚙️ Konfigurasi')
    if 'saved_admin' not in st.session_state:
        st.session_state['saved_admin'] = "Admin Logistik"
    
    admin_input = st.text_input("Officer Name", value=st.session_state['saved_admin'])
    if st.button("Update Nama ✍️", use_container_width=True):
        st.session_state['saved_admin'] = admin_input
        st.rerun()
        
    if st.button("🗑️ Reset Data", use_container_width=True, type="secondary"):
        if 'file_uploader_key' not in st.session_state: st.session_state['file_uploader_key'] = 0
        st.session_state['file_uploader_key'] += 1
        if 'processed_result' in st.session_state: del st.session_state['processed_result']
        if 'excel_data' in st.session_state: del st.session_state['excel_data']
        st.rerun()

# ==========================================
# 4. TOP BAR & DATA CENTER
# ==========================================
st.markdown(f"""
    <div class="top-bar">
        <div style="font-weight: 600; color: #1890FF;">Console</div>
        <div style="font-size: 12px; color: #8C8C8C;">Update time: {current_date_time} <span style="color: #1890FF; margin-left: 10px; cursor: pointer;">Manual Refresh 🔄</span></div>
    </div>
""", unsafe_allow_html=True)

# Data Center (Upload)
with st.container():
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📁 Data Center (Upload Files)</div>', unsafe_allow_html=True)
    
    if 'file_uploader_key' not in st.session_state:
        st.session_state['file_uploader_key'] = 0

    uploaded_files = st.file_uploader(
        "Upload Area", 
        accept_multiple_files=True, 
        type=['xlsx', 'csv'],
        key=f"uploader_{st.session_state['file_uploader_key']}",
        label_visibility="collapsed"
    )
    
    if len(uploaded_files) > 0:
        if st.button("Mulai Proses Data 🚀", type="primary", use_container_width=True):
            # --- START LOGIKA ASLI (COPY DARI appLastUpdate.py) ---
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
                else: res['ERP Document Number'] = np.nan
                
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
                else: res['Staged User'] = np.nan

                def safe_key(val):
                    s = str(val).strip()
                    if s.endswith('.0'): s = s[:-2]
                    return s

                col_store_res = next((c for c in res.columns if 'store number' in c.lower() or c.lower() == 'storenumber' or 'store' in c.lower()), None)
                if col_store_res:
                    res['Brand'] = res[col_store_res].apply(lambda x: master_store_db.get(safe_key(x), {}).get('Brand', 'SK') if safe_key(x) != "" else "SK")
                    res['Brand 2'] = res[col_store_res].apply(lambda x: master_store_db.get(safe_key(x), {}).get('Brand2', 'SK') if safe_key(x) != "" else "SK")
                else: res['Brand'] = 'SK'; res['Brand 2'] = 'SK'

                res['Admin'] = st.session_state['saved_admin']; res['Load'] = 1
                col_carrier_code = next((c for c in res.columns if 'carrier code' in c.lower() or 'carriercode' in c.lower()), None)
                if col_carrier_code: res['Kurir'] = res[col_carrier_code].apply(lambda x: master_carrier_db.get(str(x).strip(), 'Unknown'))
                else: res['Kurir'] = 'Unknown'

                res['Loader'] = st.session_state['saved_admin']; res['Tanggal Handover'] = datetime.datetime.now().strftime("%B %d, %Y")
                
                progress_bar.progress(65, text="Processing... (Menghitung durasi & Status) [65%]")
                for c in ['Created Time', 'Ordered Date', 'Picking Task Created Time', 'pickCompletedTime - Released Date Pack', 'Packing Complete', 'Shipped Date', 'Handover Date', 'End Ship Date']:
                    col_found = next((col for col in res.columns if col.lower() == c.lower()), None)
                    if col_found: res[c] = res[col_found]
                    else: res[c] = np.nan

                def calc_diff(c1, c2):
                    if c1 in res.columns and c2 in res.columns:
                        t1 = pd.to_datetime(res[c1], errors='coerce'); t2 = pd.to_datetime(res[c2], errors='coerce')
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

                res['Dokumen'] = 'Sudah Ada'; res['Attachment'] = 'Sudah Ada'
                res['Times Proses Kurir'] = calc_diff('Handover Date', 'Shipped Date')
                res['Times Proses Kurir to Shpped Date'] = calc_diff('Shipped Date', 'Handover Date')

                if 'Status' in res.columns: res['Status Manifest'] = np.where(res['Status'].astype(str).str.strip().str.lower() == 'shipped', 'Late', 'Normal')
                else: res['Status Manifest'] = 'Normal'
                res['Status Late'] = np.where(res['Status Manifest'] == 'Late', 'Late', 'Normal'); res['Remark Late'] = ""

                res['Pay-Created'] = calc_diff('Created Time', 'Ordered Date'); res['Created-Released'] = calc_diff('Picking Task Created Time', 'Created Time'); res['Released-Pick'] = calc_diff('pickCompletedTime - Released Date Pack', 'Picking Task Created Time'); res['Pick-Pack'] = calc_diff('Packing Complete', 'pickCompletedTime - Released Date Pack'); res['Pack-Collect'] = calc_diff('Shipped Date', 'Packing Complete'); res['Collect-Manifest'] = calc_diff('Handover Date', 'Shipped Date'); res['Manifest-Endshipdate'] = calc_diff('End Ship Date', 'Handover Date')
                res['Max'] = ""; res['System'] = ""

                def get_safe_seconds(td_str_series):
                    sec_list = []
                    for val in td_str_series:
                        if pd.isna(val) or str(val).strip() in ['', 'NaT']: sec_list.append(0.0); continue
                        val_str = str(val).strip(); sign = -1 if val_str.startswith('-') else 1; parts = val_str.replace('-', '').split(':')
                        try:
                            if len(parts) == 3: sec_list.append(sign * (float(parts[0] or 0) * 3600 + float(parts[1] or 0) * 60 + float(parts[2] or 0)))
                            else: sec_list.append(0.0)
                        except: sec_list.append(0.0)
                    return pd.Series(sec_list)

                sec_an = get_safe_seconds(res['Pay-Created']); sec_ao = get_safe_seconds(res['Created-Released']); sec_ap = get_safe_seconds(res['Released-Pick']); sec_aq = get_safe_seconds(res['Pick-Pack']); sec_ar = get_safe_seconds(res['Pack-Collect']); sec_as = get_safe_seconds(res['Collect-Manifest']); sec_at = get_safe_seconds(res['Manifest-Endshipdate'])
                max_sec = np.maximum.reduce([sec_an, sec_ao, sec_ap, sec_aq, sec_ar, sec_as, sec_at])

                res['Late Proses By'] = np.select(
                    [(max_sec > 0) & (max_sec == sec_an), (max_sec > 0) & (max_sec == sec_ao), (max_sec > 0) & (max_sec == sec_ap), (max_sec > 0) & (max_sec == sec_aq), (max_sec > 0) & (max_sec == sec_ar), (max_sec > 0) & (max_sec == sec_as)],
                    ["System", "Admin", "Picker", "Packer", "Outbound", "Kurir"],
                    default=""
                )

                progress_bar.progress(90, text="Processing... (Menyusun laporan akhir & Excel) [90%]")
                res['Admin '] = res['Admin']; res['Kurir '] = res['Kurir']
                kolom_final = ['WMS Order', 'ERP Document Number', 'Tracking#/PRO#', 'PlatformOrder', 'Staged User', 'Platform', 'Brand', 'Brand 2', 'Admin', 'Load', 'Kurir', 'Loader', 'Tanggal Handover', 'Wave ID', 'Created Time', 'Ordered Date', 'Picking Task Created Time', 'pickCompletedTime - Released Date Pack', 'Packing Complete', 'Shipped Date', 'Handover Date', 'End Ship Date', 'Packing to Shpped Date', 'Packing to Handover', 'Shipped Date to Handover', 'End Ship Date to Shpped Date', 'Kota', 'Provinsi', 'Status', 'Payment Menthood', 'total order amount', 'Dokumen', 'Attachment', 'Times Proses Kurir', 'Times Proses Kurir to Shpped Date', 'Status Manifest', 'Status Late', 'Remark Late', 'Pay-Created', 'Created-Released', 'Released-Pick', 'Pick-Pack', 'Pack-Collect', 'Collect-Manifest', 'Manifest-Endshipdate', 'Max', 'System', 'Admin ', 'Picker', 'Packer', 'Outbound', 'Kurir ', 'Late Proses By']
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
                        st_val = str(row[master_status_col]).strip().lower(); tr_val = str(row[master_track_col]).strip().lower()
                        if st_val and pd.notna(row[master_track_col]): master_track_dict[st_val] = tr_val

                final_df['Master_Tracking'] = final_df['Status'].astype(str).str.strip().str.lower().map(master_track_dict).fillna('untraceable')
                final_df.insert(0, 'No', range(1, len(final_df) + 1))
                st.session_state['processed_result'] = final_df

                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_to_export = final_df.drop(columns=['Master_Tracking'], errors='ignore')
                    df_to_export.columns = [c.strip() if c in ['Admin ', 'Kurir '] else c for c in df_to_export.columns]
                    df_to_export.to_excel(writer, index=False, sheet_name='Laporan_WMS')
                    workbook = writer.book; worksheet_wms = writer.sheets['Laporan_WMS']
                    format_header = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3', 'border': 1, 'align': 'center', 'valign': 'vcenter'})
                    format_time = workbook.add_format({'num_format': 'hh:mm:ss', 'border': 1, 'align': 'center', 'valign': 'vcenter'})
                    cell_format_center = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1})
                    col_idx_track = list(df_to_export.columns).index('Tracking#/PRO#'); col_idx_plat = list(df_to_export.columns).index('PlatformOrder')
                    for row_num in range(len(df_to_export)):
                        val_track = str(df_to_export.iloc[row_num]['Tracking#/PRO#']); val_plat = str(df_to_export.iloc[row_num]['PlatformOrder'])
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
                        worksheet_wms.write(0, col_num, col_name, format_header); col_data_len = df_to_export.iloc[:, col_num].astype(str).str.len().max() if not df_to_export.empty else 0; header_len = len(str(col_name)); max_len = max(header_len, col_data_len); worksheet_wms.set_column(col_num, col_num, max_len + 4, cell_format_center)

                st.session_state['excel_data'] = output.getvalue()
                
                # Metrics Calculation for UI
                val_total_late = int((final_df['Status Manifest'].astype(str).str.strip().str.lower() == 'late').sum())
                mask_late = final_df['Status Manifest'].astype(str).str.strip().str.lower() == 'late'
                val_avg_late_sec = max_sec[mask_late.values].mean() if val_total_late > 0 else 0
                avg_late_str = f"{int(val_avg_late_sec)//3600}:{(int(val_avg_late_sec)%3600)//60:02d}:{int(val_avg_late_sec)%60:02d}"
                
                # Get Order Summary stats
                val_target = len(df_os_open) if not df_os_open.empty else 0
                val_delivered = len(final_df)
                val_delivery_rate = round((val_delivered / val_target * 100), 2) if val_target > 0 else 0.0
                
                # Get Inbound Stats (Mock or from daily if available)
                val_inbound = 0
                if not dfs['daily_ho'].empty:
                    # Simple extraction for demo based on logic
                    val_inbound = int(dfs['daily_ho'].iloc[:, 1].sum()) if len(dfs['daily_ho'].columns) > 1 else 0

                st.session_state['metrics_qianyi'] = {
                    "orders_out_sla": val_total_late,
                    "avg_delay": avg_late_str,
                    "delivered": val_delivered,
                    "target": val_target,
                    "delivery_rate": val_delivery_rate,
                    "inbound": val_inbound,
                    "untraceable": int(final_df['Master_Tracking'].eq('untraceable').sum())
                }

                progress_bar.progress(100, text="Selesai!")
                st.toast("Data berhasil diproses!", icon="🚀")
            except Exception as e:
                st.error(f"Kesalahan: {e}"); st.code(traceback.format_exc())
            # --- END LOGIKA ASLI ---

    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 5. TODO SECTION (TOP METRICS)
# ==========================================
if 'metrics_qianyi' in st.session_state:
    m = st.session_state['metrics_qianyi']
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Todo</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="todo-grid">
        <div class="todo-card todo-card-teal">
            <div class="todo-label">Orders out of<br>SLA</div>
            <div class="todo-value">{m['orders_out_sla']}</div>
        </div>
        <div class="todo-card todo-card-teal">
            <div class="todo-label">Untraceable<br>Orders</div>
            <div class="todo-value">{m['untraceable']}</div>
        </div>
        <div class="todo-card todo-card-teal">
            <div class="todo-label">Avg Delay<br>Time</div>
            <div class="todo-value">{m['avg_delay']}</div>
        </div>
        <div class="todo-card todo-card-teal">
            <div class="todo-label">Pending<br>Tasks</div>
            <div class="todo-value">0</div>
        </div>
        <div class="todo-card todo-card-teal">
            <div class="todo-label">Picking<br>Exception</div>
            <div class="todo-value">0</div>
        </div>
        <div class="todo-card todo-card-blue">
            <div class="todo-label">Material<br>Consumption Failed</div>
            <div class="todo-value">0</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # 6. OUTBOUND SECTION
    # ==========================================
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Outbound</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="stats-row">
        <div class="stat-item">
            <div class="stat-label">Shipped Today</div>
            <div class="stat-value">{m['delivered']}</div>
        </div>
        <div class="stat-item">
            <div class="stat-label">Total Open</div>
            <div class="stat-value">{m['target']}</div>
        </div>
        <div class="stat-item">
            <div class="stat-label">Delivery Rate</div>
            <div class="stat-value">{m['delivery_rate']}%</div>
        </div>
        <div class="stat-item">
            <div class="stat-label">To Pick</div>
            <div class="stat-value">0</div>
        </div>
        <div class="stat-item">
            <div class="stat-label">To Pack</div>
            <div class="stat-value">0</div>
        </div>
        <div class="stat-item">
            <div class="stat-label">To Ship</div>
            <div class="stat-value">0</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # 7. INBOUND SECTION
    # ==========================================
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Inbound</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="stats-row">
        <div class="stat-item">
            <div class="stat-label">Today Inbound</div>
            <div class="stat-value">{m['inbound']}</div>
        </div>
        <div class="stat-item">
            <div class="stat-label">Due in Today</div>
            <div class="stat-value">0</div>
        </div>
        <div class="stat-item">
            <div class="stat-label">To Inspect</div>
            <div class="stat-value">0</div>
        </div>
        <div class="stat-item">
            <div class="stat-label">To Receive</div>
            <div class="stat-value">0</div>
        </div>
        <div class="stat-item">
            <div class="stat-label">To Putaway</div>
            <div class="stat-value">0</div>
        </div>
        <div class="stat-item">
            <div class="stat-label">Expect Arrive</div>
            <div class="stat-value">0</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # 8. ANALYTICS & DATA PREVIEW
    # ==========================================
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Analytics & Data Preview</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📊 Analytics Chart", "📋 Data Table"])
    
    with tab1:
        res_df = st.session_state['processed_result']
        late_df = res_df[res_df['Status Manifest'].astype(str).str.strip().str.lower() == 'late'].copy()
        if not late_df.empty:
            chart_df = late_df.groupby(['Kurir', 'Late Proses By']).size().reset_index(name='Qty')
            chart = alt.Chart(chart_df).mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4).encode(
                y=alt.Y('Kurir:N', sort='-x', title='Courier'),
                x=alt.X('Qty:Q', title='Qty'),
                color=alt.Color('Late Proses By:N', scale=alt.Scale(scheme='set2')),
                tooltip=['Kurir', 'Late Proses By', 'Qty']
            ).properties(height=400)
            st.altair_chart(chart, use_container_width=True)
        else: st.info("No late orders found.")
        
    with tab2:
        st.dataframe(st.session_state['processed_result'].drop(columns=['Master_Tracking'], errors='ignore'), use_container_width=True, hide_index=True)
        
    st.divider()
    col_d1, col_d2, col_d3 = st.columns([1, 1, 1])
    with col_d2:
        st.download_button(label="📥 Download Laporan Excel", data=st.session_state['excel_data'], file_name=f"Laporan_Outbound_{datetime.datetime.now().strftime('%Y%m%d')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
else:
    # Placeholder when no data is uploaded
    st.info("Silakan unggah file di Data Center untuk melihat statistik.")
