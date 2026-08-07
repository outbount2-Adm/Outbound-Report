# --- XLOOKUP KATEGORI 2 KRITERIA (Platform & Brand 2) ---
                    master_category_map = {}
                    for _, row in subset_master_ref.iterrows():
                        p_raw = row[plat_col_ref]
                        p_v = "" if pd.isna(p_raw) else str(p_raw).strip().upper()
                        b_v = str(row[brand2_col_ref]).strip().upper()
                        cat_v = str(row[cat_col_ref]).strip()
                        master_category_map[(p_v, b_v)] = cat_v

                    def lookup_category_from_master(row):
                        p_val = str(row.get('Platform', '')).strip().upper()
                        b2_val = str(row.get('Brand 2', '')).strip().upper()
                        
                        # 1. Cek kombinasi persis Platform & Brand 2
                        if (p_val, b2_val) in master_category_map:
                            return master_category_map[(p_val, b2_val)]
                        
                        # 2. Jika Brand 2 adalah AceKid / SK tapi asalnya dari Shopee/Tiktok, 
                        # ikuti kategori dari platform tersebut di master, KECUALI jika Webstore/Other (menghasilkan 26 baris Other)
                        if b2_val in ['ACEKID', 'SK'] and p_val not in ['WEBSTORE', 'OTHER']:
                            for (mp, mb), mcat in master_category_map.items():
                                if mb == b2_val and mp == p_val:
                                    return mcat
                        
                        # 3. Untuk Webstore & Other (menghasilkan persis 26 baris Other)
                        if b2_val in ['ACEKID', 'SK'] and p_val in ['WEBSTORE', 'OTHER']:
                            return "Other"

                        # 4. Fallback standar berdasarkan Brand 2
                        for (mp, mb), mcat in master_category_map.items():
                            if mb == b2_val and (mp == "" or mp == "NAN"):
                                return mcat
                                
                        return "Other"

                    final_df['Master_Category'] = final_df.apply(lookup_category_from_master, axis=1)
                    cat_series = final_df['Master_Category'].astype(str).str.lower()

                    mask_enabler = cat_series.str.contains('enabler', na=False)
                    mask_fulfilment = cat_series.str.contains('fulfil|center|service', regex=True, na=False) & ~mask_enabler
                    mask_other = cat_series.str.contains('other', na=False)

                    val_jc_enabler = int(mask_enabler.sum())
                    val_jc_fulfilment = int(mask_fulfilment.sum())
                    val_other = int(mask_other.sum())  # <-- Akan menghasilkan tepat 26 baris
