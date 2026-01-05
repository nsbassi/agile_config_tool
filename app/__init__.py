from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
import jwt
from functools import wraps

from config import Config
from app.routes.auth import bp as auth_bp
from app.routes.jobs import bp as jobs_bp
from app.routes.environments import bp as environments_bp


def create_app(config_class=Config) -> Flask:
    app = Flask(__name__, static_folder='static', static_url_path='')
    app.config.from_object(config_class)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    def require_auth(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if request.path.startswith('/api/auth/'):
                return f(*args, **kwargs)
            auth_header = request.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                return jsonify({'error': 'Missing or invalid Authorization header'}), 401
            token = auth_header.split(' ', 1)[1]
            try:
                jwt.decode(
                    token, app.config['SECRET_KEY'], algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                return jsonify({'error': 'Token expired'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'error': 'Invalid token'}), 401
            return f(*args, **kwargs)
        return wrapper

    # decorate all api view funcs except auth
    for bp in (auth_bp, jobs_bp, environments_bp):
        for endpoint, func in list(bp.view_functions.items()):
            if not endpoint.startswith('auth.'):
                bp.view_functions[endpoint] = require_auth(func)

    app.register_blueprint(auth_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(environments_bp)

    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')

    @app.route('/login')
    def login_page():
        return send_from_directory(app.static_folder, 'login.html')

    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, HTTPException):
            return jsonify({'error': e.description}), e.code
        app.logger.exception('Unhandled exception')
        return jsonify({'error': 'Internal server error'}), 500

    return app
