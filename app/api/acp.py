"""
ACP API Routes
"""
from flask import Blueprint, request, jsonify, send_file, Response
from app.api.auth import token_required
from app.services.acp_service import ACPService
from app.services.averify_service import AverifyService
from app.services.job_manager import job_manager
from app.utils.validators import (
    validate_instance_name, validate_operation, validate_filename,
    validate_file_size, validate_job_id, ValidationError
)
from config import get_config
import os
import logging
import time

config = get_config()
logger = logging.getLogger(__name__)

acp_bp = Blueprint('acp', __name__, url_prefix='/api')


@acp_bp.route('/acp/<operation>', methods=['POST'])
@token_required
def acp_operation(user, operation):
    """Execute ACP operation (export, import, deepcompare)"""
    try:
        data = request.get_json()
        instance = data.get('instance')
        config_file = data.get('configFileName')

        # Validate inputs
        validate_operation(operation)
        validate_instance_name(instance)

        if config_file:
            validate_filename(config_file)

        # Execute operation
        job_id = ACPService.execute_acp_operation(operation, instance, config_file)

        logger.info(f"ACP {operation} started by {user.username} for instance {instance}")

        return jsonify({
            'success': True,
            'jobId': job_id
        })

    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"ACP operation error: {str(e)}")
        return jsonify({'error': 'An error occurred'}), 500


@acp_bp.route('/averify', methods=['POST'])
@token_required
def averify_operation(user):
    """Execute Averify operation"""
    try:
        data = request.get_json()
        instance = data.get('instance')

        # Validate inputs
        validate_instance_name(instance)

        # Execute operation
        job_id = AverifyService.execute_averify(instance)

        logger.info(f"Averify started by {user.username} for instance {instance}")

        return jsonify({
            'success': True,
            'jobId': job_id
        })

    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Averify operation error: {str(e)}")
        return jsonify({'error': 'An error occurred'}), 500


@acp_bp.route('/jobs', methods=['GET'])
@token_required
def get_jobs(user):
    """Get all jobs"""
    try:
        job_type = request.args.get('jobType')
        instance = request.args.get('instance')

        jobs = job_manager.get_all_jobs(job_type=job_type, instance=instance)

        return jsonify({
            'success': True,
            'jobs': jobs
        })

    except Exception as e:
        logger.error(f"Get jobs error: {str(e)}")
        return jsonify({'error': 'An error occurred'}), 500


@acp_bp.route('/jobs/<job_id>', methods=['GET'])
@token_required
def get_job(user, job_id):
    """Get job details"""
    try:
        validate_job_id(job_id)

        job = job_manager.get_job(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404

        return jsonify({
            'success': True,
            'job': job.to_dict()
        })

    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Get job error: {str(e)}")
        return jsonify({'error': 'An error occurred'}), 500


@acp_bp.route('/jobs/<job_id>/logs', methods=['GET'])
@token_required
def stream_logs(user, job_id):
    """Stream job logs via Server-Sent Events"""
    try:
        validate_job_id(job_id)

        job = job_manager.get_job(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404

        def generate():
            last_index = 0
            while True:
                logs = job.get_logs(from_index=last_index)
                for log in logs:
                    yield f"data: {log}\n\n"
                    last_index += 1

                # Stop streaming if job is completed or failed
                if job.status in ['completed', 'failed']:
                    # Send final status
                    yield f"data: [STATUS] {job.status.upper()}\n\n"
                    break

                time.sleep(0.5)

        return Response(generate(), mimetype='text/event-stream')

    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Stream logs error: {str(e)}")
        return jsonify({'error': 'An error occurred'}), 500


@acp_bp.route('/jobs/<job_id>/outputs', methods=['GET'])
@token_required
def get_job_outputs(user, job_id):
    """Get job output files"""
    try:
        validate_job_id(job_id)

        job = job_manager.get_job(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404

        return jsonify({
            'success': True,
            'outputs': job.output_files
        })

    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Get outputs error: {str(e)}")
        return jsonify({'error': 'An error occurred'}), 500


@acp_bp.route('/download', methods=['GET'])
@token_required
def download_file(user):
    """Download output file"""
    try:
        file_path = request.args.get('path')

        if not file_path:
            return jsonify({'error': 'File path is required'}), 400

        # Security check: ensure file is within allowed directories
        abs_path = os.path.abspath(file_path)
        allowed_dirs = [
            os.path.abspath(config.OUTPUT_DIR),
            os.path.abspath(config.ACP_WORKING_DIR) if not config.ACP_REMOTE_MODE else None,
            os.path.abspath(config.AVERIFY_WORKING_DIR) if not config.ACP_REMOTE_MODE else None
        ]
        allowed_dirs = [d for d in allowed_dirs if d]

        if not any(abs_path.startswith(d) for d in allowed_dirs):
            logger.warning(f"Unauthorized file access attempt: {file_path}")
            return jsonify({'error': 'Unauthorized file access'}), 403

        if not os.path.exists(abs_path):
            return jsonify({'error': 'File not found'}), 404

        filename = os.path.basename(abs_path)

        logger.info(f"File downloaded by {user.username}: {filename}")

        return send_file(abs_path, as_attachment=True, download_name=filename)

    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return jsonify({'error': 'An error occurred'}), 500


@acp_bp.route('/config-upload', methods=['POST'])
@token_required
def upload_config(user):
    """Upload configuration file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        instance = request.form.get('instance')

        if not file.filename:
            return jsonify({'error': 'No file selected'}), 400

        # Validate inputs
        validate_instance_name(instance)
        filename = validate_filename(file.filename)

        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        validate_file_size(file_size)

        # Save file
        os.makedirs(config.UPLOAD_DIR, exist_ok=True)

        # Generate unique filename
        import uuid
        unique_filename = f"{instance}_{uuid.uuid4().hex[:8]}_{filename}"
        file_path = os.path.join(config.UPLOAD_DIR, unique_filename)

        file.save(file_path)

        logger.info(f"Config file uploaded by {user.username}: {unique_filename}")

        return jsonify({
            'success': True,
            'configFileName': unique_filename
        })

    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': 'An error occurred'}), 500


@acp_bp.route('/instances', methods=['GET'])
@token_required
def get_instances(user):
    """Get allowed instances"""
    return jsonify({
        'success': True,
        'instances': config.ALLOWED_INSTANCES
    })
