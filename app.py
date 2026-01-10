import sqlite3
import os
from vanna.legacy.ollama import Ollama
from vanna.legacy.chromadb import ChromaDB_VectorStore
from vanna.legacy.flask import VannaFlaskApp


class MyVanna(ChromaDB_VectorStore, Ollama):
    """Custom Vanna class combining ChromaDB for vector storage and Ollama for LLM."""
    
    def __init__(self, config=None):
        if config is None:
            config = {}
        
        # Set default config values
        config.setdefault("ollama_host", "http://ollama:11434")
        config.setdefault("model", "qwen2.5-coder:7b")
        config.setdefault("path", "./chroma_db")
        
        # Initialize parent classes
        ChromaDB_VectorStore.__init__(self, config=config)
        Ollama.__init__(self, config=config)


# Create Vanna instance
config = {
    "ollama_host": "http://ollama:11434",
    "model": "qwen2.5-coder:7b",
    "path": "./chroma_db"
}

vn = MyVanna(config=config)

# Add dummy training data - Multiple related tables
employees_ddl = """
CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    department VARCHAR(50),
    salary DECIMAL(10, 2),
    hire_date DATE
);
"""

employee_personal_info_ddl = """
CREATE TABLE employee_personal_info (
    id INTEGER PRIMARY KEY,
    employee_id INTEGER NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    address VARCHAR(200),
    birth_date DATE,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
);
"""

projects_ddl = """
CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    description TEXT,
    start_date DATE,
    end_date DATE,
    budget DECIMAL(12, 2)
);
"""

employee_projects_ddl = """
CREATE TABLE employee_projects (
    id INTEGER PRIMARY KEY,
    employee_id INTEGER NOT NULL,
    project_id INTEGER NOT NULL,
    role VARCHAR(50),
    hours_worked INTEGER,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    UNIQUE(employee_id, project_id)
);
"""

# Example SQL queries for training
example_sql1 = "SELECT name, department, salary FROM employees WHERE department = 'Engineering' ORDER BY salary DESC;"
example_question1 = "Show me all employees in the Engineering department sorted by salary"

example_sql2 = """
SELECT e.name, e.department, epi.email, epi.phone 
FROM employees e 
JOIN employee_personal_info epi ON e.id = epi.employee_id 
WHERE e.department = 'Engineering';
"""
example_question2 = "Show me contact information for all Engineering employees"

example_sql3 = """
SELECT e.name, p.name as project_name, ep.role, ep.hours_worked
FROM employees e
JOIN employee_projects ep ON e.id = ep.employee_id
JOIN projects p ON ep.project_id = p.id
ORDER BY e.name;
"""
example_question3 = "Show me which employees are working on which projects and their roles"

example_sql4 = "SELECT name, description, start_date, end_date FROM projects ORDER BY start_date DESC;"
example_question4 = "List all projects ordered by start date"

# Train with all DDLs
vn.train(ddl=employees_ddl)
vn.train(ddl=employee_personal_info_ddl)
vn.train(ddl=projects_ddl)
vn.train(ddl=employee_projects_ddl)

# Train with question-SQL pairs
vn.train(question=example_question1, sql=example_sql1)
vn.train(question=example_question2, sql=example_sql2)
vn.train(question=example_question3, sql=example_sql3)
vn.train(question=example_question4, sql=example_sql4)

# Create SQLite database and connect
db_dir = "/app/db_data"
db_path = os.path.join(db_dir, "employees.db")  # Dizin içinde dosya
try:
    # Dizinin var olduğundan emin ol
    os.makedirs(db_dir, exist_ok=True)
    if not os.path.exists(db_path):
        # Create database and tables
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create all tables
        cursor.execute(employees_ddl)
        cursor.execute(employee_personal_info_ddl)
        cursor.execute(projects_ddl)
        cursor.execute(employee_projects_ddl)
        
        # Insert employees data
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
        
        # Insert employee personal info (related to employees)
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
        
        # Insert projects data (unrelated table)
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
        
        # Insert employee_projects (many-to-many relationship)
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
        
        conn.commit()
        conn.close()
        print(f"✅ SQLite database created at {db_path} with sample data")
    else:
        print(f"✅ SQLite database already exists at {db_path}")
    
    # Connect to SQLite database
    vn.connect_to_sqlite(db_path)
    print("✅ Connected to SQLite database")
except Exception as e:
    print(f"❌ Error creating/connecting to database: {e}")
    raise

# Create and run Flask app
app = VannaFlaskApp(vn=vn, debug=False)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8084)
