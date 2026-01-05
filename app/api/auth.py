"""
Authentication API Routes
"""
from flask import Blueprint, request, jsonify
from functools import wraps
from app.models.user import User
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid authorization header format'}), 401

        if not token:
            return jsonify({'error': 'Authentication token is missing'}), 401

        # Verify token
        user = User.verify_token(token)
        if not user:
            return jsonify({'error': 'Invalid or expired token'}), 401

        # Pass user to route
        return f(user, *args, **kwargs)

    return decorated


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login endpoint"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({
                'success': False,
                'error': 'Username and password are required'
            }), 400

        # Authenticate user
        user = User.authenticate(username, password)
        if not user:
            logger.warning(f"Failed login attempt for user: {username}")
            return jsonify({
                'success': False,
                'error': 'Invalid username or password'
            }), 401

        # Generate token
        token = user.generate_token()

        logger.info(f"User logged in: {username}")

        return jsonify({
            'success': True,
            'token': token,
            'user': user.to_dict()
        })

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An error occurred during login'
        }), 500


@auth_bp.route('/validate', methods=['GET'])
@token_required
def validate(user):
    """Validate token endpoint"""
    return jsonify({
        'valid': True,
        'user': user.to_dict()
    })


@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(user):
    """Logout endpoint (client-side token removal)"""
    logger.info(f"User logged out: {user.username}")
    return jsonify({'success': True})
