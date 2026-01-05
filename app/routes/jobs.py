import os
import uuid
import shutil
from flask import Blueprint, request, jsonify, send_file
from werkzeug.exceptions import BadRequest, NotFound
from werkzeug.utils import secure_filename

from app.services.job_manager import JobManager
from app.services.acp_service import AcpService
from app.services.averify_service import AverifyService
from app.utils.validators import sanitize_filename
from app.models.environment import Environment

bp = Blueprint('jobs', __name__, url_prefix='/api/jobs')

# Directory for temporary uploads
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'work', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

job_manager = JobManager()
acp_service = AcpService()
averify_service = AverifyService()


def _require_json():
    data = request.get_json(silent=True)
    if data is None:
        raise BadRequest('JSON body required')
    return data


@bp.route('/upload', methods=['POST'])
def upload_file():
    """Upload a file (config, bundle, etc.) for use in jobs"""
    if 'file' not in request.files:
        raise BadRequest('No file provided')

    file = request.files['file']
    if file.filename == '':
        raise BadRequest('No file selected')

    # Generate unique filename to avoid conflicts
    original_filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4()}_{original_filename}"
    filepath = os.path.join(UPLOAD_FOLDER, unique_filename)

    file.save(filepath)

    return jsonify({
        'filename': original_filename,
        'path': filepath,
        'uploadId': unique_filename
    })


@bp.route('/', methods=['GET'])
def list_jobs():
    jobs = [job.to_dict() for job in job_manager.list_jobs()]
    return jsonify(jobs)


@bp.route('/<job_id>', methods=['GET'])
def get_job(job_id):
    job = job_manager.get_job(job_id)
    if not job:
        raise NotFound('Job not found')
    return jsonify(job.to_dict())


@bp.route('/<job_id>/log', methods=['GET'])
def get_job_log(job_id):
    job = job_manager.get_job(job_id)
    if not job:
        raise NotFound('Job not found')
    offset = request.args.get('offset', default=0, type=int)
    chunk, new_offset = job_manager.get_job_log_chunk(job_id, offset)
    return jsonify({'chunk': chunk, 'offset': new_offset, 'finished': job.finished})


@bp.route('/<job_id>/analysis', methods=['GET'])
def get_job_analysis(job_id):
    """Get detailed analysis of job outcome including exit codes and parsed logs"""
    job = job_manager.get_job(job_id)
    if not job:
        raise NotFound('Job not found')
    return jsonify({
        'jobId': job.id,
        'exitCode': job.exit_code,
        'severity': job.severity,
        'analysis': job.analysis,
        'summary': job.summary,
    })


@bp.route('/<job_id>/download', methods=['GET'])
def download_output(job_id):
    job = job_manager.get_job(job_id)
    if not job:
        raise NotFound('Job not found')
    if not job.output_files:
        raise NotFound('No output files for this job')
    filename = request.args.get('filename')
    if filename:
        filename = sanitize_filename(filename)
        path = job.output_files.get(filename)
        if not path:
            raise NotFound('Requested file not found for this job')
    else:
        _, path = next(iter(job.output_files.items()))
    if not os.path.exists(path):
        raise NotFound('Output file no longer exists on server')
    return send_file(path, as_attachment=True)


@bp.route('/acp/export', methods=['POST'])
def acp_export():
    body = _require_json()
    xml_config = body.get('xmlConfig')
    product_line = body.get('productLine')
    host = body.get('host')
    source_env_tag = body.get('sourceEnv')
    mode = body.get('mode', 'local')
    ssh = body.get('ssh', {})
    if not xml_config or not product_line or not host:
        raise BadRequest('xmlConfig, productLine and host are required')

    # Get environment to retrieve acp_project_dir
    env = None
    if source_env_tag:
        env = Environment.find_by_tag(source_env_tag)

    acp_project_dir = env.acp_project_dir if env and env.acp_project_dir else None

    remote = (mode == 'ssh')
    ssh_cfg = None
    if remote:
        ssh_host = ssh.get('host') or host
        ssh_user = ssh.get('username')
        ssh_port = ssh.get('port', 22)
        if not ssh_user:
            raise BadRequest('ssh.username required for SSH mode')
        ssh_cfg = {
            'hostname': ssh_host,
            'username': ssh_user,
            'port': ssh_port,
            'password': ssh.get('password'),
            'key_filename': ssh.get('keyFilename'),
        }

    job_id = job_manager.create_job(job_type='acp-export')
    work_dir = job_manager.get_job_work_dir(job_id)

    # If acp_project_dir is specified, copy the uploaded config to it as config.xml
    if acp_project_dir and os.path.exists(acp_project_dir):
        config_dest = os.path.join(acp_project_dir, 'config.xml')
        if os.path.exists(xml_config):
            shutil.copy2(xml_config, config_dest)
            xml_config = config_dest
            work_dir = acp_project_dir

    def _run():
        return acp_service.run_acp_export(
            host=host,
            xml_config_path=xml_config,
            product_line=product_line,
            work_dir=work_dir,
            remote=remote,
            ssh_config=ssh_cfg,
        )

    job_manager.start_job(job_id, _run)
    return jsonify({'jobId': job_id})
    return jsonify({'jobId': job_id})


@bp.route('/acp/import', methods=['POST'])
def acp_import():
    body = _require_json()
    xml_config = body.get('xmlConfig')
    export_bundle = body.get('exportBundle')
    host = body.get('host')
    mode = body.get('mode', 'local')
    ssh = body.get('ssh', {})
    if not xml_config or not export_bundle or not host:
        raise BadRequest('xmlConfig, exportBundle and host are required')
    remote = (mode == 'ssh')
    ssh_cfg = None
    if remote:
        ssh_host = ssh.get('host') or host
        ssh_user = ssh.get('username')
        ssh_port = ssh.get('port', 22)
        if not ssh_user:
            raise BadRequest('ssh.username required for SSH mode')
        ssh_cfg = {
            'hostname': ssh_host,
            'username': ssh_user,
            'port': ssh_port,
            'password': ssh.get('password'),
            'key_filename': ssh.get('keyFilename'),
        }
    job_id = job_manager.create_job(job_type='acp-import')
    work_dir = job_manager.get_job_work_dir(job_id)

    def _run():
        return acp_service.run_acp_import(
            host=host,
            xml_config_path=xml_config,
            export_bundle_path=export_bundle,
            work_dir=work_dir,
            remote=remote,
            ssh_config=ssh_cfg,
        )

    job_manager.start_job(job_id, _run)
    return jsonify({'jobId': job_id})


@bp.route('/averify/run', methods=['POST'])
def run_averify():
    body = _require_json()
    source_env = body.get('sourceEnv')
    target_env = body.get('targetEnv')
    host = body.get('host')
    config = body.get('configPath')
    mode = body.get('mode', 'local')
    ssh = body.get('ssh', {})
    if not source_env or not target_env or not host:
        raise BadRequest('sourceEnv, targetEnv and host are required')
    remote = (mode == 'ssh')
    ssh_cfg = None
    if remote:
        ssh_host = ssh.get('host') or host
        ssh_user = ssh.get('username')
        ssh_port = ssh.get('port', 22)
        if not ssh_user:
            raise BadRequest('ssh.username required for SSH mode')
        ssh_cfg = {
            'hostname': ssh_host,
            'username': ssh_user,
            'port': ssh_port,
            'password': ssh.get('password'),
            'key_filename': ssh.get('keyFilename'),
        }
    job_id = job_manager.create_job(job_type='averify')
    work_dir = job_manager.get_job_work_dir(job_id)

    def _run():
        return averify_service.run_averify(
            host=host,
            source_env=source_env,
            target_env=target_env,
            config_path=config,
            work_dir=work_dir,
            remote=remote,
            ssh_config=ssh_cfg,
        )

    job_manager.start_job(job_id, _run)
    return jsonify({'jobId': job_id})
