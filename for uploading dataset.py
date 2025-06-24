import pandas as pd
from sqlalchemy import create_engine
import os # Direkomendasikan untuk mengelola kredensial

# 1. KONFIGURASI DATABASE
# REKOMENDASI: Jangan tulis password langsung di kode. Gunakan environment variable.
# Contoh: os.getenv("SUPABASE_DB_PASSWORD")
# Ganti '[YOUR-PASSWORD]' dengan kata sandi database Supabase Anda yang sebenarnya.
DATABASE_URL = "postgresql://postgres.pqypevxwnreixsctyegz:root123@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"

# 2. NAMA FILE CSV DAN NAMA TABEL TUJUAN DI DATABASE
nama_file_csv = "data/top_10_dropout_factors.csv"
# Anda bisa menentukan nama tabel yang diinginkan di database Supabase.
# Jika tabel ini belum ada, SQLAlchemy akan membuatnya (tergantung pada `if_exists`).
nama_tabel_di_db = "top_10_dropout_factors"

# 3. OPSI PENANGANAN JIKA TABEL SUDAH ADA
# 'fail': Operasi gagal jika tabel sudah ada (default).
# 'replace': Hapus tabel yang sudah ada, buat tabel baru, lalu masukkan data.
# 'append': Tambahkan data ke tabel yang sudah ada.
# Pilih salah satu:
aksi_jika_tabel_ada = 'replace' # atau 'append', atau 'fail'

try:
    # Membuat engine database
    engine = create_engine(DATABASE_URL)
    print("Engine SQLAlchemy berhasil dibuat.")

    # Membaca file CSV ke dalam DataFrame Pandas
    print(f"Mencoba membaca file CSV: {nama_file_csv}...")
    
    # =======================================================================
    # PERUBAHAN UTAMA DI SINI: Tambahkan parameter sep=';'
    df_employee = pd.read_csv(nama_file_csv) #, sep=';'
    # =======================================================================

    print("File CSV berhasil dibaca ke dalam DataFrame Pandas.")
    print(f"Jumlah baris data yang dibaca: {len(df_employee)}")
    
    if not df_employee.empty:
        print("Beberapa baris pertama data:")
        print(df_employee.head())
        # Cek nama kolom untuk memastikan parsing berhasil
        print("\nKolom yang terdeteksi:", list(df_employee.columns))
    else:
        print("Peringatan: File CSV kosong atau tidak dapat dibaca dengan benar.")
        exit() # Keluar jika DataFrame kosong

    # Mengirim DataFrame ke tabel SQL di database Supabase
    print(f"Mengirim data ke tabel '{nama_tabel_di_db}' di Supabase dengan opsi if_exists='{aksi_jika_tabel_ada}'...")
    df_employee.to_sql(
        name=nama_tabel_di_db,
        con=engine,
        if_exists=aksi_jika_tabel_ada,
        index=False  # Biasanya kita tidak ingin mengirim index DataFrame sebagai kolom di SQL
    )
    print(f"Data dari '{nama_file_csv}' berhasil diunggah ke tabel '{nama_tabel_di_db}' di database Supabase Anda.")

    # Verifikasi (opsional): Baca beberapa data dari tabel yang baru dibuat/diisi
    with engine.connect() as connection:
        # Gunakan text() untuk query yang lebih aman jika nama tabel kompleks
        from sqlalchemy import text
        result = connection.execute(text(f"SELECT * FROM {nama_tabel_di_db} LIMIT 5"))
        print(f"\nVerifikasi: 5 baris pertama dari tabel '{nama_tabel_di_db}' di database:")
        for row in result:
            print(row)
        # 'with' statement akan otomatis menutup koneksi, connection.close() tidak wajib

except FileNotFoundError:
    print(f"Error: File '{nama_file_csv}' tidak ditemukan. Pastikan file ada di direktori yang benar.")
except pd.errors.EmptyDataError:
    print(f"Error: File '{nama_file_csv}' kosong.")
except Exception as e:
    print(f"Terjadi error saat proses unggah: {e}")
    print("Pastikan detail koneksi DATABASE_URL sudah benar dan database Supabase Anda dapat diakses.")