# Vanna AI Docker Projesi - Kurulum ve Kullanım Kılavuzu

## 🚀 Projeyi Çalıştırma

### 1. Projeyi Başlatma

```bash
# Proje klasörüne gidin
cd /Users/eniskorkut/Desktop/vanna-main

# Docker Compose ile servisleri başlatın
docker-compose up --build
```

**Not:** İlk çalıştırmada Ollama `llama3.2` modelini indirecek, bu birkaç dakika sürebilir.

### 2. Servislerin Hazır Olduğunu Kontrol Etme

- **Ollama**: http://localhost:11434
- **Vanna AI Web UI**: http://localhost:8084

### 3. Web Arayüzünü Kullanma

Tarayıcınızda `http://localhost:8084` adresine gidin. Vanna AI'nin web arayüzü açılacak ve doğal dil sorularınızı sorabilirsiniz.

## 📊 Veritabanı Durumu

**✅ SQLite Veritabanına Bağlı!**

Proje şu anda **SQLite** veritabanı kullanıyor. `employees.db` adında bir veritabanı otomatik olarak oluşturuluyor ve örnek verilerle dolduruluyor.

### Veritabanı Yapısı

**employees** tablosu:
- `id` (INTEGER PRIMARY KEY)
- `name` (VARCHAR)
- `department` (VARCHAR)
- `salary` (DECIMAL)
- `hire_date` (DATE)

### Örnek Veriler

Veritabanında 6 örnek çalışan kaydı bulunuyor:
- Engineering departmanında 4 çalışan
- Sales ve Marketing departmanlarında 1'er çalışan

### Başka Veritabanı Kullanmak İsterseniz

`app.py` dosyasında `vn.connect_to_sqlite()` satırını değiştirerek başka veritabanlarına bağlanabilirsiniz:

- **PostgreSQL**: `vn.connect_to_postgres(host="...", dbname="...", user="...", password="...", port=5432)`
- **MySQL**: `vn.connect_to_mysql(host="...", dbname="...", user="...", password="...", port=3306)`
- **Snowflake**: `vn.connect_to_snowflake(account="...", username="...", password="...", database="...")`

## 🔧 Servisleri Durdurma

```bash
# Servisleri durdurmak için
docker-compose down

# Verileri de silmek için (dikkatli!)
docker-compose down -v
```

## 📝 Örnek Kullanım

Web arayüzünde şu gibi sorular sorabilirsiniz:

- "Show me all employees in the Engineering department sorted by salary"
- "What is the average salary by department?"
- "List all employees hired in 2023"
- "Who are the highest paid employees?"
- "How many employees are in each department?"

**Not:** Veritabanı bağlantısı yapıldığı için SQL sorguları çalışacak ve sonuçları göreceksiniz!
