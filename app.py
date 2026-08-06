# --- D. KALKULASI METRIC SUMMARY (ULTIMATE ROBUST FIX) ---
                
                # 1. Target (Count unique Ref# dari file Order Summary Export OPEN)
                df_os_open = dfs.get('order_summary_open', dfs.get('order_summary', pd.DataFrame()))
                col_ref_sum = next((c for c in df_os_open.columns if 'ref#' in c.lower()), None)
                val_target = df_os_open[col_ref_sum].astype(str).str.strip().replace('', np.nan).replace('nan', np.nan).dropna().nunique() if col_ref_sum else 0
                
                val_delivered = len(final_df)
                val_delivery_rate = round((val_delivered / val_target * 100), 2) if val_target > 0 else 0.0

                # 2. pending_order (Total Qty mutlak dari Kolom H / Index 7 file Daily HO)
                val_pending = 0
                if dfs['ho_outbound'].shape[1] >= 8:
                    try:
                        col_h_raw = dfs['ho_outbound'].iloc[:, 7] # Kolom H secara indeks mutlak
                        val_pending = int(pd.to_numeric(col_h_raw.astype(str).str.replace(r'[^\d.-]', '', regex=True), errors='coerce').fillna(0).sum())
                    except: pass

                # 3. Avg Shipped & Avg Handover
                def get_avg_time_str(series_hhmmss):
                    if series_hhmmss is None or series_hhmmss.empty:
                        return "00:00:00"
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

                # 4. kurir_instan (Total Qty Kolom F berdasarkan Kolom B dengan pembersihan spasi)
                val_kurir_instan = 0
                if dfs['ho_outbound'].shape[1] >= 6:
                    try:
                        # Membersihkan spasi ganda/ekstra pada teks Kolom B
                        col_b_str = dfs['ho_outbound'].iloc[:, 1].astype(str).str.lower().str.replace(r'\s+', ' ', regex=True).str.strip()
                        col_f_val = dfs['ho_outbound'].iloc[:, 5]
                        
                        target_kurir_keywords = [
                            "instant", "sameday", "paxel"
                        ]
                        
                        # Mendeteksi baris yang mengandung kata kunci kurir instan/sameday/paxel secara fleksibel
                        mask_match = col_b_str.apply(lambda x: any(k in x for k in target_kurir_keywords))
                        val_kurir_instan = int(pd.to_numeric(col_f_val[mask_match].astype(str).str.replace(r'[^\d.-]', '', regex=True), errors='coerce').fillna(0).sum())
                    except: pass
                
                # 5. Lookup Kategori Master untuk jc_enabler, jc_fulfilment, dan other
                master_df = dfs.get('master', pd.DataFrame())
                master_cat_dict = {}
                if not master_df.empty:
                    m_plat_col = next((c for c in master_df.columns if 'platform' in c.lower()), None)
                    m_b2_col = next((c for c in master_df.columns if 'brand' in c.lower() and ('2' in c or 'brand2' in c.lower())), None)
                    m_cat_col = next((c for c in master_df.columns if 'category' in c.lower()), None)
                    
                    if m_plat_col and m_b2_col and m_cat_col:
                        for _, row in master_df.iterrows():
                            p_val = str(row[m_plat_col]).strip().lower()
                            b2_val = str(row[m_b2_col]).strip().lower()
                            cat_val = str(row[m_cat_col]).strip().lower() # Dinormalkan ke lowercase
                            if p_val and b2_val and pd.notna(row[m_cat_col]):
                                master_cat_dict[(p_val, b2_val)] = cat_val

                def get_master_category(row):
                    p = str(row.get('Platform', '')).strip().lower()
                    b2 = str(row.get('Brand 2', '')).strip().lower()
                    return master_cat_dict.get((p, b2), 'other')

                final_df['Master_Category'] = final_df.apply(get_master_category, axis=1)

                # Countif yang toleran terhadap variasi penulisan spasi/huruf besar-kecil pada Master
                val_jc_enabler = int(final_df['Master_Category'].str.contains('enabler', na=False).sum())
                val_jc_fulfilment = int(final_df['Master_Category'].str.contains('fulfilment|fullfilment', na=False).sum())
                val_other = int(final_df['Master_Category'].str.contains('other', na=False).sum()) | int((~final_df['Master_Category'].str.contains('enabler|fulfilment|fullfilment', na=False)).sum())

                # 6. Tracking Lookup (Status -> tracking di file Master)
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

                val_traceable = int(final_df['Master_Tracking'].eq('traceable').sum())
                val_untraceable = int(final_df['Master_Tracking'].eq('untraceable').sum())
