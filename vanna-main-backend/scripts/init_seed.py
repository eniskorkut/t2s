import asyncio
from prisma import Prisma
from datetime import datetime

async def main():
    db = Prisma()
    await db.connect()

    print("🌱 Seeding database...")

    # 1. Create Employees
    employees_data = [
        {"name": "John Doe", "department": "Engineering", "salary": 75000.00, "hire_date": datetime(2022, 1, 15)},
        {"name": "Jane Smith", "department": "Engineering", "salary": 85000.00, "hire_date": datetime(2021, 6, 20)},
        {"name": "Bob Johnson", "department": "Sales", "salary": 60000.00, "hire_date": datetime(2023, 3, 10)},
        {"name": "Alice Williams", "department": "Engineering", "salary": 90000.00, "hire_date": datetime(2020, 11, 5)},
        {"name": "Charlie Brown", "department": "Marketing", "salary": 65000.00, "hire_date": datetime(2022, 9, 12)},
        {"name": "Diana Prince", "department": "Engineering", "salary": 80000.00, "hire_date": datetime(2021, 4, 18)},
    ]

    employees = []
    for data in employees_data:
        emp = await db.employee.create(data=data)
        employees.append(emp)
        print(f"Created employee: {emp.name}")

    # 2. Create Personal Info (Linked to Employees)
    personal_infos = [
        {"email": "john.doe@company.com", "phone": "+1-555-0101", "address": "123 Main St", "employee_id": employees[0].id},
        {"email": "jane.smith@company.com", "phone": "+1-555-0102", "address": "456 Oak Ave", "employee_id": employees[1].id},
        {"email": "bob.johnson@company.com", "phone": "+1-555-0103", "address": "789 Pine Rd", "employee_id": employees[2].id},
        {"email": "alice.williams@company.com", "phone": "+1-555-0104", "address": "321 Elm St", "employee_id": employees[3].id},
        {"email": "charlie.brown@company.com", "phone": "+1-555-0105", "address": "654 Maple Dr", "employee_id": employees[4].id},
        {"email": "diana.prince@company.com", "phone": "+1-555-0106", "address": "987 Cedar Ln", "employee_id": employees[5].id},
    ]

    for info in personal_infos:
        await db.employeepersonalinfo.create(data=info)
    print("Created personal info for all employees.")

    # 3. Create Projects
    projects_data = [
        {"name": "Website Redesign", "description": "Complete redesign", "budget": 50000.00},
        {"name": "Mobile App Development", "description": "New mobile app for iOS", "budget": 120000.00},
        {"name": "Database Migration", "description": "Migrate legacy database", "budget": 75000.00},
        {"name": "Marketing Campaign", "description": "Q4 marketing campaign", "budget": 30000.00},
    ]

    projects = []
    for p_data in projects_data:
        proj = await db.project.create(data=p_data)
        projects.append(proj)
        print(f"Created project: {proj.name}")

    # 4. Assign Employees to Projects (Many-to-Many via EmployeeProject)
    assignments = [
        # Project 1: Website Redesign
        (employees[0].id, projects[0].id, "Frontend Developer", 320),
        (employees[1].id, projects[0].id, "Backend Developer", 400),
        (employees[3].id, projects[0].id, "Project Manager", 200),
        # Project 2: Mobile App
        (employees[0].id, projects[1].id, "Mobile Developer", 450),
        (employees[1].id, projects[1].id, "Mobile Developer", 500),
        (employees[5].id, projects[1].id, "UI/UX Designer", 380),
        # Project 3: DB Migration
        (employees[1].id, projects[2].id, "Database Architect", 300),
        (employees[3].id, projects[2].id, "Tech Lead", 250),
        # Project 4: Marketing
        (employees[4].id, projects[3].id, "Marketing Specialist", 180),
        (employees[2].id, projects[3].id, "Sales Coordinator", 150),
    ]

    for emp_id, proj_id, role, hours in assignments:
        await db.employeeproject.create(data={
            "employee_id": emp_id,
            "project_id": proj_id,
            "role": role,
            "hours_worked": hours
        })
    print("Assigned employees to projects.")

    await db.disconnect()
    print("✅ Seed completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
