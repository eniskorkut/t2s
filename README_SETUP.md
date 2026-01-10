# Vanna AI Docker Projesi - Kurulum ve Kullanım Kılavuzu

## 🚀 Projeyi Çalıştırma

### 1. Veritabanını ve Vanna AI'yı İlk Kez Başlatma

**ÖNEMLİ:** İlk çalıştırmada veritabanını oluşturmak ve Vanna AI'yı eğitmek için `init_db.py` scriptini çalıştırmanız gerekiyor.

```bash
# Proje klasörüne gidin
cd /Users/eniskorkut/Desktop/vanna-main

# Docker Compose ile servisleri başlatın (sadece Ollama ve Vanna-app container'ları)
docker-compose up -d

# Veritabanını oluştur ve Vanna AI'yı eğit
docker exec vanna-app python init_db.py
```

**Not:** İlk çalıştırmada Ollama `qwen2.5-coder:7b` modelini indirecek, bu birkaç dakika sürebilir.

### 2. Normal Kullanım (Veritabanı Zaten Oluşturulmuşsa)

```bash
# Servisleri başlatın
docker-compose up -d

# Vanna-app container'ı otomatik olarak başlayacak ve mevcut veritabanına bağlanacak
```

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

### Proje Yapısı

Proje production-ready hale getirilmiştir ve şu dosyalardan oluşur:

- **`vanna_config.py`**: MyVanna sınıfı ve konfigürasyon ayarları
- **`init_db.py`**: Veritabanı oluşturma ve Vanna AI eğitimi scripti (ilk çalıştırmada kullanılır)
- **`app.py`**: Flask web uygulaması (sadece mevcut veritabanına bağlanır ve uygulamayı başlatır)
- **`docker-compose.yml`**: Docker servisleri yapılandırması
- **`Dockerfile`**: Vanna-app container imajı

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
