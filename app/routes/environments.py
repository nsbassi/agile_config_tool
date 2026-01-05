from flask import Blueprint, request, jsonify
from app.models.environment import Environment

bp = Blueprint('environments', __name__, url_prefix='/api/environments')


@bp.route('', methods=['GET'])
def list_environments():
    """Get all environments"""
    try:
        environments = Environment.find_all()
        return jsonify([env.to_dict() for env in environments]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:env_id>', methods=['GET'])
def get_environment(env_id):
    """Get environment by ID"""
    try:
        env = Environment.find_by_id(env_id)
        if env:
            return jsonify(env.to_dict()), 200
        return jsonify({'error': 'Environment not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('', methods=['POST'])
def create_environment():
    """Create new environment"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate required fields
        required_fields = ['tag', 'agilePlmUrl',
                           'propagationUser', 'propagationPassword']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Check if tag already exists
        existing = Environment.find_by_tag(data['tag'])
        if existing:
            return jsonify({'error': f'Environment with tag "{data["tag"]}" already exists'}), 409

        env = Environment.from_dict(data)
        env.save()
        return jsonify(env.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:env_id>', methods=['PUT'])
def update_environment(env_id):
    """Update environment"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        env = Environment.find_by_id(env_id)
        if not env:
            return jsonify({'error': 'Environment not found'}), 404

        # Validate required fields
        required_fields = ['tag', 'agilePlmUrl',
                           'propagationUser', 'propagationPassword']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Check if tag is being changed and if new tag already exists
        if data['tag'] != env.tag:
            existing = Environment.find_by_tag(data['tag'])
            if existing:
                return jsonify({'error': f'Environment with tag "{data["tag"]}" already exists'}), 409

        env.tag = data['tag']
        env.agile_plm_url = data['agilePlmUrl']
        env.propagation_user = data['propagationUser']
        env.propagation_password = data['propagationPassword']
        env.dest_jdbc_url = data.get('destJdbcUrl', '')
        env.dest_tns_name = data.get('destTnsName', '')
        env.dest_oracle_home = data.get('destOracleHome', '')
        env.dest_db_user = data.get('destDbUser', '')
        env.dest_db_password = data.get('destDbPassword', '')
        env.save()
        return jsonify(env.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:env_id>', methods=['DELETE'])
def delete_environment(env_id):
    """Delete environment"""
    try:
        env = Environment.find_by_id(env_id)
        if not env:
            return jsonify({'error': 'Environment not found'}), 404

        env.delete()
        return jsonify({'message': 'Environment deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
