"""
Email Utility - Mock Implementation
"""
import sys

def send_reset_email(email: str, token: str):
    """
    Simulate sending a password reset email by logging the link to stdout.
    
    Args:
        email: Recipient email
        token: Reset token
    """
    reset_link = f"http://localhost:3000/reset-password?token={token}"
    
    print("\n" + "="*60)
    print(f"📧 MOCK EMAIL TO: {email}")
    print(f"🔗 RESET LINK: {reset_link}")
    print("="*60 + "\n")
    sys.stdout.flush()
