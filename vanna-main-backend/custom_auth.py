"""
Custom Authentication for VannaFlaskApp
SOLID: Single Responsibility - Handles only authentication
"""
from flask import session, jsonify
from vanna.legacy.flask.auth import AuthInterface
from services import AuthService, UserService, DatabaseService


class SessionAuth(AuthInterface):
    """Session-based authentication for VannaFlaskApp."""
    
    def __init__(self, db_service: DatabaseService):
        """
        Initialize session auth.
        
        Args:
            db_service: DatabaseService instance
        """
        self.auth_service = AuthService(db_service)
        self.user_service = UserService(db_service)
    
    def get_user(self, request):
        """
        Get current user from session.
        
        Args:
            request: Flask request object
            
        Returns:
            User dict or None
        """
        user_id = session.get('user_id')
        if user_id:
            return self.user_service.get_user_by_id(user_id)
        return None
    
    def is_logged_in(self, user):
        """
        Check if user is logged in.
        
        Args:
            user: User dict or None
            
        Returns:
            True if logged in, False otherwise
        """
        return user is not None
    
    def override_config_for_user(self, user, config):
        """
        Override config for specific user (not used in our case).
        
        Args:
            user: User dict or None
            config: Current config dict
            
        Returns:
            Config dict (potentially modified)
        """
        # We don't need user-specific config overrides for now
        return config
    
    
    def login_form(self):
        """
        Return login form HTML.
        Deprecated: Frontend handles login UI.
        """
        return "Login via Frontend"
    
    
    def login_handler(self, request):
        """
        Handle login request.
        
        Args:
            request: Flask request object
            
        Returns:
            Flask response
        """
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        user = self.auth_service.authenticate(email, password)
        
        if user:
            session['user_id'] = user['id']
            session['user_email'] = user['email']
            return jsonify({
                'success': True,
                'user': {
                    'id': user['id'],
                    'email': user['email']
                }
            }), 200
        else:
            return jsonify({'error': 'Invalid email or password'}), 401
    
    def logout_handler(self, request):
        """
        Handle logout request.
        
        Args:
            request: Flask request object
            
        Returns:
            Flask response
        """
        session.clear()
        return jsonify({'success': True}), 200
    
    def callback_handler(self, request):
        """
        Handle OAuth callback (not used in session auth).
        
        Args:
            request: Flask request object
            
        Returns:
            Flask response
        """
        return jsonify({'error': 'Not implemented'}), 501
