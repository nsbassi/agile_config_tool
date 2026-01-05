import os
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Dict, Optional, List, Tuple

from config import Config


@dataclass
class Job:
    id: str
    type: str
    status: str = 'pending'
    created_at: datetime = field(default_factory=datetime.utcnow)
    finished_at: Optional[datetime] = None
    summary: str = ''
    log: str = ''
    output_files: Dict[str, str] = field(default_factory=dict)
    exit_code: Optional[int] = None
    severity: str = 'UNKNOWN'
    analysis: Optional[Dict] = None

    @property
    def finished(self) -> bool:
        return self.status in {'success', 'error'}

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'type': self.type,
            'status': self.status,
            'createdAt': self.created_at.isoformat() + 'Z',
            'finishedAt': self.finished_at.isoformat() + 'Z' if self.finished_at else None,
            'summary': self.summary,
            'exitCode': self.exit_code,
            'severity': self.severity,
            'analysis': self.analysis,
        }


class JobManager:
    def __init__(self):
        self.jobs: Dict[str, Job] = {}
        self._lock = threading.Lock()
        os.makedirs(Config.WORK_DIR, exist_ok=True)

    def create_job(self, job_type: str) -> str:
        job_id = str(uuid.uuid4())
        with self._lock:
            self.jobs[job_id] = Job(id=job_id, type=job_type)
        return job_id

    def get_job(self, job_id: str) -> Optional[Job]:
        return self.jobs.get(job_id)

    def list_jobs(self) -> List[Job]:
        return list(self.jobs.values())

    def get_job_work_dir(self, job_id: str) -> str:
        path = os.path.join(Config.WORK_DIR, job_id)
        os.makedirs(path, exist_ok=True)
        return path

    def append_log(self, job_id: str, text: str) -> None:
        with self._lock:
            job = self.jobs.get(job_id)
            if job:
                job.log += text

    def set_output_files(self, job_id: str, files: Dict[str, str]) -> None:
        with self._lock:
            job = self.jobs.get(job_id)
            if job:
                job.output_files = files

    def get_job_log_chunk(self, job_id: str, offset: int) -> Tuple[str, int]:
        job = self.jobs.get(job_id)
        if not job:
            return '', offset
        data = job.log[offset:]
        return data, offset + len(data)

    def start_job(self, job_id: str, target: Callable[[], Dict[str, str]]) -> None:
        def runner():
            job = self.jobs[job_id]
            job.status = 'running'
            self.append_log(job_id, f'Job {job_id} started\n')
            try:
                result = target()
                self.append_log(job_id, result.get('log', ''))
                self.set_output_files(job_id, result.get('output_files', {}))

                # Store exit code, severity, and analysis
                job.exit_code = result.get('exit_code', 0)
                job.severity = result.get('severity', 'UNKNOWN')
                job.analysis = result.get('analysis')

                # Determine job status based on exit code
                if job.exit_code == 0:
                    job.status = 'success'
                elif job.exit_code == 9:  # Cancelled
                    job.status = 'cancelled'
                else:
                    job.status = 'error'

                job.summary = result.get('summary', 'Completed')
            except Exception as exc:  # noqa
                import traceback
                tb = traceback.format_exc()
                self.append_log(job_id, f'ERROR: {exc}\n{tb}')
                job.status = 'error'
                job.summary = str(exc)
                job.exit_code = 1
                job.severity = 'CRITICAL'
            finally:
                job.finished_at = datetime.utcnow()
                self.append_log(
                    job_id, f'Job {job_id} finished with status {job.status}\n')

        thread = threading.Thread(target=runner, daemon=True)
        thread.start()


job_manager = JobManager()
