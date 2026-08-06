import pandas as pd
import numpy as np

# 1. Load File Data
df_wms = pd.read_excel('Laporan_WMS.xlsx')  # Sesuaikan nama file WMS Anda
df_order = pd.read_excel('Order_Summary.xlsx')  # Sesuaikan nama file Order Summary Anda
df_ho = pd.read_excel('Daily HO.xlsx')
df_master = pd.read_excel('Master.xlsx')

# -------------------------------------------------------------
# A. PENDING ORDER & KURIR INSTAN (DARI FILE DAILY HO)
# -------------------------------------------------------------
# Bersihkan nama kolom dari spasi berlebih
df_ho.columns = df_ho.columns.str.strip().str.replace(r'\s+', ' ', regex=True)

# 1. Pending Order (Mencari kolom yang memuat 'Pending Cut Off Qty')
col_pending = [c for c in df_ho.columns if 'pending' in c.lower() and 'cut' in c.lower()]
pending_order = df_ho[col_pending[0]].fillna(0).sum() if col_pending else 0

# 2. Kurir Instan (Mencari kata kunci 'Instant', 'Grab', 'Gojek', 'Shopee Instant' di kolom Kurir)
col_kurir = [c for c in df_ho.columns if 'kurir' in c.lower()][0]
col_qty = [c for c in df_ho.columns if 'deliveree' in c.lower() or 'qty' in c.lower()][0]

mask_instan = df_ho[col_kurir].astype(str).str.contains('instant|sameday|grab|gojek|shopee instant', case=False, na=False)
kurir_instan = df_ho.loc[mask_instan, col_qty].fillna(0).sum()

# -------------------------------------------------------------
# B. LOOKUP MASTER (JC ENABLER, JC FULFILMENT, OTHER)
# -------------------------------------------------------------
# Buat Map Kategori dari File Master (Toleran terhadap huruf besar/kecil & typo Fullfilment)
brand_map = {}

# Mapping dari Brand 2 ke Category
for _, row in df_master.iterrows():
    if pd.notna(row.get('Brand 2')) and pd.notna(row.get('Category')):
        brand = str(row['Brand 2']).strip().upper()
        cat = str(row['Category']).strip()
        brand_map[brand] = cat

# Normalisasi Nama Brand di Laporan WMS
col_brand_wms = [c for c in df_wms.columns if 'brand' in c.lower()][0]
df_wms['Brand_Clean'] = df_wms[col_brand_wms].astype(str).str.strip().str.upper()

# Lakukan Mapping Kategori
df_wms['Category_Mapped'] = df_wms['Brand_Clean'].map(brand_map).fillna('Other')

# Hitung Distribusi Kategori (Toleran ejaan 'Fullfilment' vs 'Fulfillment')
jc_enabler = (df_wms['Category_Mapped'] == 'Jet Commerce Enabler').sum()

# Menggabungkan ejaan 'Fullfilment' (l ganda) dan 'Fulfillment' (l tunggal)
mask_fulfilment = df_wms['Category_Mapped'].str.contains('Fullfilment|Fulfillment', case=False, na=False)
jc_fulfilment = mask_fulfilment.sum()

# Sisa kategori yang tidak terpetakan
other = len(df_wms) - (jc_enabler + jc_fulfilment)

# -------------------------------------------------------------
# C. TAMPILKAN HASIL AKHIR
# -------------------------------------------------------------
print(f"pending_order  : {int(pending_order)}")
print(f"kurir_instan   : {int(kurir_instan)}")
print(f"jc_enabler     : {jc_enabler}")
print(f"jc_fulfilment  : {jc_fulfilment}")
print(f"other          : {other}")
