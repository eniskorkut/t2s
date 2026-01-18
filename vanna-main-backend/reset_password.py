import sqlite3
import bcrypt
import sys

DB_PATH = "db_data/employees.db"

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def reset_password(email: str, new_password: str):
    print(f"🔄 Parola sıfırlanıyor: {email}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Kullanıcıyı bul
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    
    if not user:
        print(f"❌ Kullanıcı bulunamadı: {email}")
        conn.close()
        return

    # Parolayı güncelle
    new_hash = hash_password(new_password)
    try:
        cursor.execute("UPDATE users SET password_hash = ? WHERE email = ?", (new_hash, email))
        conn.commit()
        print(f"✅ Başarılı! {email} kullanıcısının parolası güncellendi.")
        print(f"👉 Yeni parola: {new_password}")
    except Exception as e:
        print(f"❌ Hata oluştu: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Kullanım: python3 reset_password.py <email> <yeni_parola>")
        # Default kullanım kolaylığı için
        email = input("Email: ")
        password = input("Yeni Parola: ")
        if email and password:
            reset_password(email, password)
    else:
        reset_password(sys.argv[1], sys.argv[2])
