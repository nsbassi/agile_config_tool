from flask import Blueprint, request, jsonify
from werkzeug.exceptions import Unauthorized, BadRequest

from app.models.user import authenticate
from config import Config

bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        raise BadRequest('Username and password are required')

    user = authenticate(username, password)
    if not user:
        raise Unauthorized('Invalid credentials')

    token = user.generate_jwt(Config.SECRET_KEY, Config.JWT_EXPIRATION_MINUTES)
    return jsonify({'token': token, 'user': {'username': user.username}})
