import os
import sys

# Add the current directory to sys.path to make imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.database_service import DatabaseService
from services.user_service import UserService

def make_user_admin(email):
    # Path to the database file
    # We use the local path since we are running this script locally
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db_data", "employees.db")
    
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return

    print(f"Connecting to database at {db_path}...")
    db_service = DatabaseService(db_path)
    user_service = UserService(db_service)

    print(f"Looking for user with email: {email}")
    user = user_service.get_user_by_email(email)

    if user:
        print(f"User found: {user['id']} (Current Role: {user['role']})")
        if user['role'] == 'admin':
            print("User is already an admin.")
        else:
            print("Updating user role to 'admin'...")
            success = user_service.update_user_role(user['id'], 'admin')
            if success:
                print("Successfully updated user role to admin.")
                
                # Verify
                updated_user = user_service.get_user_by_id(user['id'])
                print(f"Verification - New Role: {updated_user['role']}")
            else:
                print("Failed to update user role.")
    else:
        print(f"User with email {email} not found.")
        # Optional: Print all users to see who exists
        print("Listing all users:")
        users = user_service.get_all_users()
        for u in users:
            print(f"- {u['id']}: {u['email']} ({u['role']})")

if __name__ == "__main__":
    email = "enis_korkut@hotmail.com"
    make_user_admin(email)
