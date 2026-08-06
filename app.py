import pandas as pd
import re

# Asumsi dataframe dari file Anda:
# raw_ho_df = dfs['ho_outbound']  (atau nama variabel dataframe Daily HO Anda)
# master_df = dfs['master']       (atau nama variabel dataframe Master Anda)

# ==========================================
# 1. PERBAIKAN PENDING ORDER
# ==========================================
# Mencari kolom yang spesifik mengandung kata 'pending' DAN 'qty'
# Menghindari salah ambil kolom 'Status Pending' atau 'Alasan Pending'
col_pending = next((c for c in raw_ho_df.columns if 'pending' in c.lower() and 'qty' in c.lower()), None)

if col_pending:
    # Memastikan data diubah ke angka (numeric), mengabaikan teks kosong/error
    pending_order = pd.to_numeric(raw_ho_df[col_pending], errors='coerce').fillna(0).sum()
else:
    pending_order = 0


# ==========================================
# 2. PERBAIKAN KURIR INSTAN
# ==========================================
# Mencari kolom kurir/logistik dan kolom Qty utama (bukan pending qty)
col_kurir = next((c for c in raw_ho_df.columns if 'kurir' in c.lower() or 'carrier' in c.lower() or 'logistics' in c.lower()), None)
col_qty = next((c for c in raw_ho_df.columns if 'qty' in c.lower() and 'pending' not in c.lower()), None)

kurir_instan = 0
if col_kurir and col_qty:
    # Regex super ketat HANYA untuk layanan cepat (tidak akan menghitung shopee standard/anteraja reguler)
    instan_regex = r'(?i)instant|instan|sameday|same day|gojek|go-jek|grab|gosend|paxel'
    
    # Filter baris yang kurirnya mengandung kata-kata di atas
    is_instan = raw_ho_df[col_kurir].astype(str).str.contains(instan_regex, regex=True, na=False)
    
    # Jumlahkan qty khusus untuk baris yang terfilter kurir instan
    kurir_instan = pd.to_numeric(raw_ho_df.loc[is_instan, col_qty], errors='coerce').fillna(0).sum()


# ==========================================
# 3. PERBAIKAN JC ENABLER, FULFILMENT, & OTHER
# ==========================================
# Variabel awal di-set 0
jc_enabler = 0
jc_fulfilment = 0
other = 0

# Mencari nama kolom Platform dan Brand 2 di file HO (fleksibel huruf besar/kecil)
col_ho_platform = next((c for c in raw_ho_df.columns if 'platform' in c.lower()), None)
col_ho_brand = next((c for c in raw_ho_df.columns if 'brand 2' in c.lower() or 'brand' in c.lower()), None)

# Mencari nama kolom Platform, Brand, dan Category di Master
col_master_platform = next((c for c in master_df.columns if 'platform' in c.lower()), None)
col_master_brand = next((c for c in master_df.columns if 'brand' in c.lower()), None)
col_master_category = next((c for c in master_df.columns if 'category' in c.lower() or 'kategori' in c.lower()), None)

if all([col_ho_platform, col_ho_brand, col_master_platform, col_master_brand, col_master_category, col_qty]):
    
    # LAKUKAN STANDARISASI TEKS: Huruf kecil semua & hapus spasi berlebih di awal/akhir kata
    # Untuk file HO:
    raw_ho_df['_clean_platform'] = raw_ho_df[col_ho_platform].astype(str).str.strip().str.lower()
    raw_ho_df['_clean_brand'] = raw_ho_df[col_ho_brand].astype(str).str.strip().str.lower()
    
    # Untuk file Master:
    master_df['_clean_platform'] = master_df[col_master_platform].astype(str).str.strip().str.lower()
    master_df['_clean_brand'] = master_df[col_master_brand].astype(str).str.strip().str.lower()
    master_df['_clean_category'] = master_df[col_master_category].astype(str).str.strip().str.lower()
    
    # Buat kamus pemetaan (Dictionary Mapping) dari Master untuk pencarian instan
    # Kunci (Key) = Tuple (Platform, Brand), Nilai (Value) = Category
    master_mapping = master_df.set_index(['_clean_platform', '_clean_brand'])['_clean_category'].to_dict()
    
    # Fungsi untuk mencocokkan data
    def tentukan_kategori(row):
        plat = str(row.get('_clean_platform', '')).strip().lower()
        brnd = str(row.get('_clean_brand', '')).strip().lower()
        
        # Jika kosong, pakai default Webstore & Acekid seperti logika Anda sebelumnya
        if plat == 'nan' or plat == '': plat = 'webstore'
        if brnd == 'nan' or brnd == '': brnd = 'acekid'
        
        # Cari di kamus mapping. Jika tidak ketemu, lempar ke 'other'
        return master_mapping.get((plat, brnd), 'other')
    
    # Aplikasikan fungsi ke data HO
    raw_ho_df['Kategori_Final'] = raw_ho_df.apply(tentukan_kategori, axis=1)
    
    # Pastikan kolom Qty bisa dihitung
    raw_ho_df[col_qty] = pd.to_numeric(raw_ho_df[col_qty], errors='coerce').fillna(0)
    
    # Hitung masing-masing kategori
    jc_enabler = raw_ho_df[raw_ho_df['Kategori_Final'] == 'jc enabler'][col_qty].sum()
    jc_fulfilment = raw_ho_df[raw_ho_df['Kategori_Final'] == 'jc fulfilment'][col_qty].sum()
    other = raw_ho_df[raw_ho_df['Kategori_Final'] == 'other'][col_qty].sum()
