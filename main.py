"""
FastAPI Application Entry Point
SOLID Principles: Separation of concerns, dependency injection
"""
import os
import subprocess
import sys
import time
from typing import List, Optional
import requests
from models.schemas import GenerateSqlRequest
import hashlib
import pandas as pd
import sqlite3
import re
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from vanna_config import MyVanna, get_default_config
from services import DatabaseService, AuthService, UserService, QueryService, ChatService
from api import auth, queries, chat


def wait_for_ollama(ollama_host="http://ollama:11434", max_retries=30, retry_delay=2):
    """Wait for Ollama service to be ready."""
    print(f"⏳ Waiting for Ollama service at {ollama_host}...")
    for i in range(max_retries):
        try:
            response = requests.get(f"{ollama_host}/api/tags", timeout=5)
            if response.status_code == 200:
                print(f"✅ Ollama service is ready!")
                return True
        except (requests.exceptions.RequestException, requests.exceptions.ConnectionError):
            if i < max_retries - 1:
                print(f"   Retry {i+1}/{max_retries}...")
                time.sleep(retry_delay)
            else:
                print(f"⚠️  Ollama service not ready after {max_retries} retries, continuing anyway...")
                return False
    return False


def check_and_create_missing_tables(db_path):
    """Check if required tables exist and create missing ones."""
    if not os.path.exists(db_path):
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    missing_tables = []
    
    # Check and create users table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if cursor.fetchone() is None:
        missing_tables.append("users")
        print("⚠️  'users' table not found. Creating...")
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email VARCHAR(255) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    # Check and create user_saved_queries table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_saved_queries'")
    if cursor.fetchone() is None:
        missing_tables.append("user_saved_queries")
        print("⚠️  'user_saved_queries' table not found. Creating...")
        cursor.execute("""
            CREATE TABLE user_saved_queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                question TEXT NOT NULL,
                sql_query TEXT NOT NULL,
                saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_trained BOOLEAN DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
    
    # Check and create employees table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='employees'")
    if cursor.fetchone() is None:
        missing_tables.append("employees")
        print("⚠️  'employees' table not found. Creating...")
        cursor.execute("""
            CREATE TABLE employees (
                id INTEGER PRIMARY KEY,
                name VARCHAR(100),
                department VARCHAR(50),
                salary DECIMAL(10, 2),
                hire_date DATE
            )
        """)
        # Insert sample data
        print("   📊 Inserting sample employee data...")
        employees_data = [
            (1, "John Doe", "Engineering", 75000.00, "2022-01-15"),
            (2, "Jane Smith", "Engineering", 85000.00, "2021-06-20"),
            (3, "Bob Johnson", "Sales", 60000.00, "2023-03-10"),
            (4, "Alice Williams", "Engineering", 90000.00, "2020-11-05"),
            (5, "Charlie Brown", "Marketing", 65000.00, "2022-09-12"),
            (6, "Diana Prince", "Engineering", 80000.00, "2021-04-18"),
        ]
        cursor.executemany(
            "INSERT INTO employees (id, name, department, salary, hire_date) VALUES (?, ?, ?, ?, ?)",
            employees_data
        )
    
    # Check and create employee_personal_info table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='employee_personal_info'")
    if cursor.fetchone() is None:
        missing_tables.append("employee_personal_info")
        print("⚠️  'employee_personal_info' table not found. Creating...")
        cursor.execute("""
            CREATE TABLE employee_personal_info (
                id INTEGER PRIMARY KEY,
                employee_id INTEGER NOT NULL,
                email VARCHAR(100),
                phone VARCHAR(20),
                address VARCHAR(200),
                birth_date DATE,
                FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
            )
        """)
        # Insert sample data
        print("   📊 Inserting sample personal info data...")
        personal_info_data = [
            (1, 1, "john.doe@company.com", "+1-555-0101", "123 Main St, City", "1990-05-15"),
            (2, 2, "jane.smith@company.com", "+1-555-0102", "456 Oak Ave, City", "1988-08-22"),
            (3, 3, "bob.johnson@company.com", "+1-555-0103", "789 Pine Rd, City", "1992-03-10"),
            (4, 4, "alice.williams@company.com", "+1-555-0104", "321 Elm St, City", "1985-11-30"),
            (5, 5, "charlie.brown@company.com", "+1-555-0105", "654 Maple Dr, City", "1991-07-18"),
            (6, 6, "diana.prince@company.com", "+1-555-0106", "987 Cedar Ln, City", "1989-12-05"),
        ]
        cursor.executemany(
            "INSERT INTO employee_personal_info (id, employee_id, email, phone, address, birth_date) VALUES (?, ?, ?, ?, ?, ?)",
            personal_info_data
        )
    
    # Check and create projects table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='projects'")
    if cursor.fetchone() is None:
        missing_tables.append("projects")
        print("⚠️  'projects' table not found. Creating...")
        cursor.execute("""
            CREATE TABLE projects (
                id INTEGER PRIMARY KEY,
                name VARCHAR(100),
                description TEXT,
                start_date DATE,
                end_date DATE,
                budget DECIMAL(12, 2)
            )
        """)
        # Insert sample data
        print("   📊 Inserting sample project data...")
        projects_data = [
            (1, "Website Redesign", "Complete redesign of company website", "2023-01-01", "2023-06-30", 50000.00),
            (2, "Mobile App Development", "New mobile application for iOS and Android", "2023-03-15", "2023-12-31", 120000.00),
            (3, "Database Migration", "Migrate legacy database to cloud", "2023-05-01", "2023-08-15", 75000.00),
            (4, "Marketing Campaign", "Q4 marketing campaign launch", "2023-09-01", "2023-11-30", 30000.00),
        ]
        cursor.executemany(
            "INSERT INTO projects (id, name, description, start_date, end_date, budget) VALUES (?, ?, ?, ?, ?, ?)",
            projects_data
        )
    
    # Check and create employee_projects table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='employee_projects'")
    if cursor.fetchone() is None:
        missing_tables.append("employee_projects")
        print("⚠️  'employee_projects' table not found. Creating...")
        cursor.execute("""
            CREATE TABLE employee_projects (
                id INTEGER PRIMARY KEY,
                employee_id INTEGER NOT NULL,
                project_id INTEGER NOT NULL,
                role VARCHAR(50),
                hours_worked INTEGER,
                FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                UNIQUE(employee_id, project_id)
            )
        """)
        # Insert sample data
        print("   📊 Inserting sample employee-project relationships...")
        employee_projects_data = [
            (1, 1, 1, "Frontend Developer", 320),
            (2, 2, 1, "Backend Developer", 400),
            (3, 4, 1, "Project Manager", 200),
            (4, 1, 2, "Mobile Developer", 450),
            (5, 2, 2, "Mobile Developer", 500),
            (6, 6, 2, "UI/UX Designer", 380),
            (7, 2, 3, "Database Architect", 300),
            (8, 4, 3, "Tech Lead", 250),
            (9, 5, 4, "Marketing Specialist", 180),
            (10, 3, 4, "Sales Coordinator", 150),
        ]
        cursor.executemany(
            "INSERT INTO employee_projects (id, employee_id, project_id, role, hours_worked) VALUES (?, ?, ?, ?, ?)",
            employee_projects_data
        )
    
    # Check and create chat_sessions table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chat_sessions'")
    if cursor.fetchone() is None:
        missing_tables.append("chat_sessions")
        print("⚠️  'chat_sessions' table not found. Creating...")
        cursor.execute("""
            CREATE TABLE chat_sessions (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                title VARCHAR(255) NOT NULL,
                is_pinned BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
    
    # Check and create chat_messages table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chat_messages'")
    if cursor.fetchone() is None:
        missing_tables.append("chat_messages")
        print("⚠️  'chat_messages' table not found. Creating...")
        cursor.execute("""
            CREATE TABLE chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role VARCHAR(20) NOT NULL,
                content TEXT NOT NULL,
                sql_query TEXT,
                data TEXT,
                plotly_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
            )
        """)
    
    if missing_tables:
        conn.commit()
        print(f"✅ Created missing tables: {', '.join(missing_tables)}")
    
    conn.close()
    return len(missing_tables) > 0


def initialize_database_if_needed(db_path):
    """Initialize database if it doesn't exist or has missing tables."""
    if not os.path.exists(db_path):
        print("=" * 60)
        print("⚠️  Database not found. Initializing database...")
        print("=" * 60)
        try:
            result = subprocess.run(
                [sys.executable, "/app/init_db.py"],
                check=True,
                capture_output=True,
                text=True
            )
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            print("✅ Database initialization completed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error initializing database: {e}")
            print(f"STDOUT: {e.stdout}")
            print(f"STDERR: {e.stderr}")
            raise
        except Exception as e:
            print(f"❌ Unexpected error during database initialization: {e}")
            raise
    else:
        # Database exists, check for missing tables
        print("🔍 Checking database for missing tables...")
        check_and_create_missing_tables(db_path)


# Create FastAPI app first (so uvicorn can start immediately)
app = FastAPI(
    title="Vanna AI - SQL Asistanı",
    description="Doğal dilden SQL sorguları oluşturun",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services on startup (so uvicorn starts first)
@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup."""
    import sys
    sys.stdout.flush()
    print("🚀 Starting Vanna AI backend...", flush=True)
    
    # Wait for Ollama service to be ready
    ollama_host = os.getenv("OLLAMA_HOST", "http://ollama:11434")
    wait_for_ollama(ollama_host)
    sys.stdout.flush()
    
    # Initialize Vanna instance
    print("🔧 Initializing Vanna AI instance...", flush=True)
    try:
        config = get_default_config()
        print(f"   Config: model={config.get('model')}, host={config.get('ollama_host')}", flush=True)
        vn = MyVanna(config=config)
        print("✅ Vanna AI instance initialized successfully", flush=True)
    except Exception as e:
        print(f"❌ Error initializing Vanna AI: {e}", flush=True)
        import traceback
        traceback.print_exc()
        sys.stdout.flush()
        raise
    
    # Connect to SQLite database (auto-initialize if needed)
    db_path = os.path.join("/app/db_data", "employees.db")
    try:
        initialize_database_if_needed(db_path)
        vn.connect_to_sqlite(db_path)
        print(f"✅ Connected to SQLite database at {db_path}", flush=True)
    except Exception as e:
        print(f"❌ Error connecting to database: {e}", flush=True)
        sys.stdout.flush()
        raise
    
    # Initialize services (Dependency Injection - SOLID)
    db_service = DatabaseService(db_path)
    auth_service = AuthService(db_service)
    user_service = UserService(db_service)
    query_service = QueryService(db_service)
    chat_service = ChatService(db_service)
    
    # Store services in app state for dependency injection
    app.state.db_service = db_service
    app.state.auth_service = auth_service
    app.state.user_service = user_service
    app.state.query_service = query_service
    app.state.chat_service = chat_service
    app.state.vanna_instance = vn
    
    print("✅ FastAPI application initialized successfully", flush=True)
    print("=" * 60, flush=True)
    print("🌐 Vanna AI is ready! Access the API at http://localhost:8084", flush=True)
    print("📖 API docs available at http://localhost:8084/docs", flush=True)
    print("=" * 60, flush=True)
    sys.stdout.flush()

# Include routers
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(queries.router, prefix="/api", tags=["queries"])
app.include_router(chat.router, prefix="/api", tags=["chat"])


# Simple in-memory cache for SQL queries (for legacy API compatibility)
sql_cache = {}


def is_valid_sql(text: str) -> bool:
    """Check if text is a valid SQL query."""
    sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER', 'WITH']
    text_upper = text.upper().strip()
    # Remove common prefixes like "intermediate_sql" comments
    text_upper = re.sub(r'--.*', '', text_upper)  # Remove comments
    text_upper = text_upper.strip()
    return any(text_upper.startswith(keyword) for keyword in sql_keywords)


def shorten_error_message(error: str, max_length: int = 100) -> str:
    """Kısalt hata mesajını maksimum uzunluğa."""
    if len(error) <= max_length:
        return error
    # İlk cümleyi al veya ilk max_length karakteri
    sentences = error.split('.')
    if sentences and len(sentences[0]) <= max_length:
        return sentences[0].strip() + '.'
    return error[:max_length].strip() + '...'


def generate_query_variations(question: str) -> list:
    """Sorguyu çeşitlendir ve alternatif öneriler oluştur."""
    variations = []
    question_lower = question.lower()
    
    # Proje ile ilgili sorgular
    if 'proje' in question_lower:
        variations.append("Tüm projeleri listele")
        variations.append("Projeleri tarihe göre sırala")
        variations.append("Aktif projeleri göster")
        variations.append("Proje sayısını göster")
    
    # Çalışan ile ilgili sorgular
    if 'çalışan' in question_lower or 'employee' in question_lower:
        variations.append("Tüm çalışanları listele")
        variations.append("Çalışan sayısını göster")
        variations.append("Departmana göre çalışanları göster")
    
    # Genel sorgular
    if not variations:
        variations.append("Tüm kayıtları listele")
        variations.append("Kayıt sayısını göster")
        variations.append("Son kayıtları göster")
    
    return variations[:3]  # Maksimum 3 öneri


def generate_sql_explanation(question: str, sql: str) -> str:
    """
    SQL sorgusunu analiz ederek kısa Türkçe açıklama oluşturur.
    Backend'de tüm mantık işlemleri burada yapılır.
    Açıklamalar kaldırıldı - sadece SQL gösteriliyor.
    """
    sql_upper = sql.upper().strip()
    
    # COUNT sorguları
    if 'COUNT(*)' in sql_upper or 'COUNT(' in sql_upper:
        if 'FROM EMPLOYEES' in sql_upper:
            return 'Toplam çalışan sayısını buluyorum.'
        return 'Kayıt sayısını buluyorum.'
    
    # SELECT sorguları
    if sql_upper.startswith('SELECT'):
        if 'WHERE' in sql_upper:
            return 'Filtrelenmiş verileri getiriyorum.'
        if 'JOIN' in sql_upper:
            return 'Birleştirilmiş verileri getiriyorum.'
        if 'ORDER BY' in sql_upper:
            return 'Sıralanmış verileri getiriyorum.'
        return 'Verileri getiriyorum.'
    
    # Varsayılan açıklama
    return 'SQL sorgusu oluşturuldu.'


# Vanna Legacy API endpoints (for compatibility with frontend)
@app.post("/api/v0/generate_sql")
async def generate_sql(request_data: GenerateSqlRequest, request: Request):
    """
    Generate SQL from natural language question.
    Legacy Vanna API endpoint upgraded to support history.
    Tüm backend mantığı burada işlenir.
    Semantic cache kontrolü ile performans artışı sağlanır.
    """
    try:
        vn = request.app.state.vanna_instance
        question = request_data.question
        history = request_data.history

        # Step 0: Contextualize question if history exists
        if history:
            # Sadece son 5 mesajı al
            recent_history = history[-5:]
            
            # Geçmiş mesajları metne dönüştür
            history_text = ""
            for msg in recent_history:
                history_text += f"{msg.role}: {msg.content}\n"
            
            prompt = f"""
            Konuşma Geçmişi:
            {history_text}
            
            Kullanıcının Son Sorusu: {question}
            
            Görevin: Kullanıcının son sorusunu, geçmiş konuşma bağlamını kullanarak tek başına anlaşılabilir, bağımsız bir soruya dönüştürmek.
            Eğer son soru zaten bağımsızsa, aynen bırak.
            Soru veritabanı ile ilgili olmalı.
            Sadece yeniden yazılmış soruyu döndür, açıklama ekleme.
            
            Örnek:
            Geçmiş: 
            user: İstanbul satışları kaç?
            assistant: SELECT ...
            Son Soru: Peki ya Ankara?
            Çıktı: Ankara satışları kaç?
            """
            
            try:
                # Vanna'nın LLM'ini kullanarak soruyu yeniden yaz
                system_msg = vn.system_message("Sen bir soru netleştirme asistanısın.")
                user_msg = vn.user_message(prompt)
                contextual_question = vn.submit_prompt([system_msg, user_msg])
                
                if contextual_question and contextual_question.strip():
                    print(f"Original Question: {question}")
                    print(f"Contextualized Question: {contextual_question}")
                    question = contextual_question.strip()
            except Exception as e:
                print(f"Warning: Failed to contextualize question: {e}")
                # Hata durumunda orijinal soruyu kullan
        
        # Step 1: Check semantic cache first
        cached_sql = QueryService.check_semantic_cache(vn, question, threshold=0.3)
        if cached_sql:
            # Cache hit - return cached SQL
            sql = cached_sql.strip()
            query_id = hashlib.md5(f"{question}_{sql}".encode()).hexdigest()
            explanation = generate_sql_explanation(question, sql)
            
            return {
                "type": "sql",
                "id": query_id,
                "text": sql,
                "explanation": explanation,
                "from_cache": True
            }
        
        # Step 2: Cache miss - generate SQL using LLM
        llm_response = vn.generate_sql(question=question)
        
        # LLM yanıtının SQL olup olmadığını kontrol et
        if not is_valid_sql(llm_response):
            # SQL değilse, sorguyu çeşitlendir ve öneriler sun
            variations = generate_query_variations(question)
            suggestions_text = " veya ".join([f'"{v}"' for v in variations])
            
            return JSONResponse(
                status_code=200,
                content={
                    "type": "clarification",
                    "message": f"Sorgunuzu tam olarak anlayamadım. Şunu mu demek istiyorsunuz: {suggestions_text}?",
                    "suggestions": variations,
                    "original_question": question
                }
            )
        
        # SQL geçerli, devam et
        sql = llm_response.strip()
        
        # Generate a unique ID for this SQL query
        query_id = hashlib.md5(f"{question}_{sql}".encode()).hexdigest()
        
        # Store SQL in cache for run_sql endpoint (legacy compatibility)
        sql_cache[query_id] = {
            "question": question,
            "sql": sql
        }
        
        # Backend'de kısa SQL açıklaması oluştur
        explanation = generate_sql_explanation(question, sql)
        
        return {
            "type": "sql",
            "id": query_id,
            "text": sql,
            "explanation": explanation,
            "from_cache": False
        }
    except Exception as e:
        error_msg = shorten_error_message(str(e))
        
        # Hata durumunda da sorgu çeşitlendirme öner
        variations = generate_query_variations(question)
        suggestions_text = " veya ".join([f'"{v}"' for v in variations])
        
        return JSONResponse(
            status_code=500,
            content={
                "type": "error",
                "error": error_msg,
                "suggestions": variations,
                "message": f"Sorgu oluşturulamadı. Şunu mu demek istiyorsunuz: {suggestions_text}?"
            }
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "vanna"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8084)
