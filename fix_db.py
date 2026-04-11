import sqlite3
import os

# Path ke database
db_path = 'db_new.sqlite3'

if not os.path.exists(db_path):
    # Coba di BASE_DIR (parent) jika script dijalankan di subfolder
    db_path = '../db_new.sqlite3'

def fix_manifest_table():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Cek kolom yang ada
        cursor.execute("PRAGMA table_info(finance_manifest)")
        columns = [row[1] for row in cursor.fetchall()]
        
        # List semua kolom yang harus ada di Manifest
        required_columns = [
            ('kategori', 'VARCHAR(50) DEFAULT "HULU"'),
            ('tanggal_kirim', 'DATE'),
            ('no_resi', 'VARCHAR(100) DEFAULT ""'),
            ('pengirim', 'VARCHAR(200)'),
            ('tujuan', 'VARCHAR(200)'),
            ('koli', 'INTEGER DEFAULT 0'),
            ('kg', 'DECIMAL(10, 2) DEFAULT 0'),
            ('penerima', 'VARCHAR(200)'),
            ('tanggal_terima', 'DATE'),
            ('dp', 'DECIMAL(15, 0) DEFAULT 0'),
            ('tarif', 'DECIMAL(15, 0) DEFAULT 0'),
            ('total', 'DECIMAL(15, 0) DEFAULT 0'),
            ('status_bayar', 'BOOLEAN DEFAULT 0'),
            ('armada_ops', 'VARCHAR(100)'),
            ('rute_ops', 'VARCHAR(200)'),
            ('nomor_manifest', 'VARCHAR(100)'),
        ]
        
        for col_name, col_type in required_columns:
            if col_name not in columns:
                print(f"Adding '{col_name}' column to finance_manifest table...")
                try:
                    cursor.execute(f"ALTER TABLE finance_manifest ADD COLUMN {col_name} {col_type}")
                    conn.commit()
                    print(f"Successfully added '{col_name}'.")
                except Exception as e:
                    print(f"Failed to add {col_name}: {e}")
            else:
                print(f"Column '{col_name}' already exists.")

        # FIX: Jika ada kolom 'nomor_manifest' yang NOT NULL di tabel lama (biasanya karena bentrok tabel baru)
        if 'nomor_manifest' in columns:
            print("Detected 'nomor_manifest' in legacy table. Cleaning up constraints...")
            # Kita tidak bisa DROP atau ALTER NULL di SQLite dengan mudah, 
            # tapi kita bisa pastikan ada default-nya atau biarkan saja jika sudah oke.
            # Karena ini IntegrityError NOT NULL, kita coba lari ke signal saja untuk fix-nya.
            pass
            
        conn.close()
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_manifest_table()
