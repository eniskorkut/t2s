import sqlite3
import os

DB_PATH = "db_data/employees.db"

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"❌ Veritabanı bulunamadı: {DB_PATH}")
        return

    print(f"📦 Veritabanı güncelleniyor: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Users tablosuna role ekle
    try:
        cursor.execute("SELECT role FROM users LIMIT 1")
        print("✅ 'users' tablosunda 'role' sütunu zaten var.")
    except sqlite3.OperationalError:
        print("⚠️ 'users' tablosunda 'role' sütunu yok. Ekleniyor...")
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user'")
            print("   ✓ 'role' sütunu eklendi.")
        except Exception as e:
            print(f"   ❌ Hata: {e}")

    # 2. schema_definitions tablosunu oluştur
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schema_definitions'")
    if cursor.fetchone():
        print("✅ 'schema_definitions' tablosu zaten var.")
    else:
        print("⚠️ 'schema_definitions' tablosu yok. Oluşturuluyor...")
        try:
            cursor.execute("""
            CREATE TABLE schema_definitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                ddl_content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            """)
            print("   ✓ 'schema_definitions' tablosu oluşturuldu.")
        except Exception as e:
            print(f"   ❌ Hata: {e}")

    # 3. İlk kullanıcıyı Admin yap
    print("🔄 Admin kullanıcısı kontrol ediliyor...")
    cursor.execute("SELECT id, email, role FROM users ORDER BY id ASC LIMIT 1")
    first_user = cursor.fetchone()
    
    if first_user:
        user_id, email, role = first_user
        if role != 'admin':
            print(f"⚠️ İlk kullanıcı ({email}) admin değil. Admin yapılıyor...")
            cursor.execute("UPDATE users SET role = 'admin' WHERE id = ?", (user_id,))
            print("   ✓ İlk kullanıcı admin yapıldı.")
        else:
            print(f"✅ İlk kullanıcı ({email}) zaten admin.")
    else:
        print("ℹ️ Henüz hiç kullanıcı yok. Kayıt olan ilk kullanıcı admin olacak (AuthService mantığı ile).")

    conn.commit()
    conn.close()
    print("\n✨ Migrasyon tamamlandı!")

if __name__ == "__main__":
    migrate()
