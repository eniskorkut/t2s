"""
Database Initialization Script
Creates SQLite database, populates it with sample data, and trains Vanna AI.
This script should be run once before starting the Flask application.
"""
import sqlite3
import os
from vanna_config import MyVanna, get_default_config


def get_ddl_statements():
    """Returns all DDL statements for table creation."""
    return {
        "users": """
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""",
        "user_saved_queries": """
CREATE TABLE user_saved_queries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    sql_query TEXT NOT NULL,
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_trained BOOLEAN DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
""",
        "chat_sessions": """
CREATE TABLE chat_sessions (
    id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    is_pinned BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
""",
        "chat_messages": """
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
);
""",
        "employees": """
CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    department VARCHAR(50),
    salary DECIMAL(10, 2),
    hire_date DATE
);
""",
        "employee_personal_info": """
CREATE TABLE employee_personal_info (
    id INTEGER PRIMARY KEY,
    employee_id INTEGER NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    address VARCHAR(200),
    birth_date DATE,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
);
""",
        "projects": """
CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    description TEXT,
    start_date DATE,
    end_date DATE,
    budget DECIMAL(12, 2)
);
""",
        "employee_projects": """
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
    }


def get_documentation():
    """Returns documentation about database schema and relationships."""
    return """
DATABASE SCHEMA AND RELATIONSHIPS:

1. EMPLOYEES TABLE (Main Table):
   - Primary Key: id
   - Columns: id, name, department, salary, hire_date
   - This is the main employee table containing basic employee information.

2. EMPLOYEE_PERSONAL_INFO TABLE (One-to-One Relationship):
   - Primary Key: id
   - Foreign Key: employee_id → employees(id) ON DELETE CASCADE
   - Columns: id, employee_id, email, phone, address, birth_date
   - Relationship: Each employee has exactly one personal info record
   - To join: JOIN employee_personal_info epi ON employees.id = epi.employee_id
   - Example: SELECT e.name, epi.email FROM employees e JOIN employee_personal_info epi ON e.id = epi.employee_id

3. PROJECTS TABLE (Standalone Table):
   - Primary Key: id
   - Columns: id, name, description, start_date, end_date, budget
   - This table has NO direct relationship with employees table.
   - IMPORTANT: You cannot join employees directly to projects!

4. EMPLOYEE_PROJECTS TABLE (Many-to-Many Junction Table):
   - Primary Key: id
   - Foreign Keys: 
     * employee_id → employees(id) ON DELETE CASCADE
     * project_id → projects(id) ON DELETE CASCADE
   - Columns: id, employee_id, project_id, role, hours_worked
   - UNIQUE constraint: (employee_id, project_id) - prevents duplicate assignments
   - This is a JUNCTION TABLE that connects employees to projects
   - Relationship: Many-to-Many
     * One employee can work on multiple projects
     * One project can have multiple employees
   
   CRITICAL JOINING RULES:
   - To query employees and their projects, you MUST use this junction table
   - Correct pattern:
     SELECT e.name, p.name as project_name, ep.role
     FROM employees e
     JOIN employee_projects ep ON e.id = ep.employee_id
     JOIN projects p ON ep.project_id = p.id
   
   - WRONG (DO NOT DO THIS):
     SELECT * FROM employees e JOIN projects p ON e.project_id = p.id
     (This is incorrect because employees table has NO project_id column!)

COMMON QUERY PATTERNS:

1. Get employees working on a specific project:
   SELECT e.name, e.salary, ep.role, ep.hours_worked
   FROM employees e
   JOIN employee_projects ep ON e.id = ep.employee_id
   JOIN projects p ON ep.project_id = p.id
   WHERE p.name = 'Project Name'
   ORDER BY e.salary DESC

2. Get highest paid employee on a project:
   SELECT e.name, e.salary
   FROM employees e
   JOIN employee_projects ep ON e.id = ep.employee_id
   JOIN projects p ON ep.project_id = p.id
   WHERE p.name = 'Project Name'
   ORDER BY e.salary DESC
   LIMIT 1

3. Get all projects for an employee:
   SELECT p.name, p.description, ep.role, ep.hours_worked
   FROM projects p
   JOIN employee_projects ep ON p.id = ep.project_id
   JOIN employees e ON ep.employee_id = e.id
   WHERE e.name = 'Employee Name'

4. Get employee contact info (one-to-one join):
   SELECT e.name, e.department, epi.email, epi.phone
   FROM employees e
   JOIN employee_personal_info epi ON e.id = epi.employee_id
   WHERE e.department = 'Engineering'
"""


def get_training_examples():
    """Returns question-SQL pairs for training Vanna AI."""
    return [
        {
            "question": "Show me all employees in the Engineering department sorted by salary",
            "sql": "SELECT name, department, salary FROM employees WHERE department = 'Engineering' ORDER BY salary DESC;"
        },
        {
            "question": "Show me contact information for all Engineering employees",
            "sql": """
SELECT e.name, e.department, epi.email, epi.phone 
FROM employees e 
JOIN employee_personal_info epi ON e.id = epi.employee_id 
WHERE e.department = 'Engineering';
"""
        },
        {
            "question": "Show me which employees are working on which projects and their roles",
            "sql": """
SELECT e.name, p.name as project_name, ep.role, ep.hours_worked
FROM employees e
JOIN employee_projects ep ON e.id = ep.employee_id
JOIN projects p ON ep.project_id = p.id
ORDER BY e.name;
"""
        },
        {
            "question": "List all projects ordered by start date",
            "sql": "SELECT name, description, start_date, end_date FROM projects ORDER BY start_date DESC;"
        }
    ]


def create_database(db_path):
    """Creates SQLite database and populates it with sample data."""
    db_dir = os.path.dirname(db_path)
    os.makedirs(db_dir, exist_ok=True)
    
    if os.path.exists(db_path):
        print(f"⚠️  Database already exists at {db_path}. Skipping creation.")
        return
    
    print(f"📦 Creating database at {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get DDL statements
    ddls = get_ddl_statements()
    
    # Create all tables
    print("📋 Creating tables...")
    # User management tables
    cursor.execute(ddls["users"])
    cursor.execute(ddls["user_saved_queries"])
    cursor.execute(ddls["chat_sessions"])
    cursor.execute(ddls["chat_messages"])
    # Business data tables
    cursor.execute(ddls["employees"])
    cursor.execute(ddls["employee_personal_info"])
    cursor.execute(ddls["projects"])
    cursor.execute(ddls["employee_projects"])
    
    # Insert employees data
    print("👥 Inserting employees data...")
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
    
    # Insert employee personal info
    print("📧 Inserting employee personal info...")
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
    
    # Insert projects data
    print("📁 Inserting projects data...")
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
    print("🔗 Inserting employee-project relationships...")
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
    print(f"✅ Database created successfully at {db_path} with sample data")


def train_vanna(vn):
    """Trains Vanna AI with DDL statements, documentation, and example question-SQL pairs."""
    print("🎓 Training Vanna AI...")
    
    # Get DDL statements
    ddls = get_ddl_statements()
    
    # Train with DDLs
    print("  📚 Training with DDL statements...")
    for table_name, ddl in ddls.items():
        vn.train(ddl=ddl)
        print(f"    ✓ Trained with {table_name} DDL")
    
    # Train with documentation (IMPORTANT: This helps model understand relationships)
    print("  📖 Training with database schema documentation...")
    documentation = get_documentation()
    vn.train(documentation=documentation)
    print("    ✓ Trained with database schema documentation")
    
    # Train with question-SQL pairs (few examples for common patterns)
    print("  💬 Training with question-SQL examples...")
    examples = get_training_examples()
    for i, example in enumerate(examples, 1):
        vn.train(question=example["question"], sql=example["sql"])
        print(f"    ✓ Trained with example {i}/{len(examples)}")
    
    print("✅ Vanna AI training completed")


def main():
    """Main initialization function."""
    print("=" * 60)
    print("🚀 Initializing Database and Training Vanna AI")
    print("=" * 60)
    
    # Initialize Vanna
    config = get_default_config()
    vn = MyVanna(config=config)
    print("✅ Vanna AI instance created")
    
    # Database path
    db_dir = "/app/db_data"
    db_path = os.path.join(db_dir, "employees.db")
    
    # Create database
    create_database(db_path)
    
    # Train Vanna
    train_vanna(vn)
    
    # Connect to database
    print(f"🔌 Connecting to database at {db_path}...")
    vn.connect_to_sqlite(db_path)
    print("✅ Connected to SQLite database")
    
    print("=" * 60)
    print("✨ Initialization completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
