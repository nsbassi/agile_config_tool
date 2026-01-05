import sqlite3
import json
from typing import List, Optional, Dict, Any
from contextlib import contextmanager
from datetime import datetime


class JobModel:
    """Database model for persisting job data"""
    DB_PATH = 'environments.db'  # Using same DB as environments

    @classmethod
    @contextmanager
    def get_db(cls):
        """Context manager for database connection"""
        conn = sqlite3.connect(cls.DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    @classmethod
    def init_db(cls):
        """Initialize jobs table"""
        with cls.get_db() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    finished_at TEXT,
                    summary TEXT,
                    log TEXT,
                    output_files TEXT,
                    exit_code INTEGER,
                    severity TEXT,
                    analysis TEXT
                )
            ''')
            conn.commit()

    @classmethod
    def save_job(cls, job_id: str, job_type: str, status: str, created_at: datetime,
                 finished_at: Optional[datetime] = None, summary: str = '',
                 log: str = '', output_files: Dict[str, str] = None,
                 exit_code: Optional[int] = None, severity: str = 'UNKNOWN',
                 analysis: Optional[Dict] = None):
        """Save or update a job in the database"""
        with cls.get_db() as conn:
            conn.execute('''
                INSERT OR REPLACE INTO jobs 
                (id, type, status, created_at, finished_at, summary, log, 
                 output_files, exit_code, severity, analysis)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job_id,
                job_type,
                status,
                created_at.isoformat(),
                finished_at.isoformat() if finished_at else None,
                summary,
                log,
                json.dumps(output_files or {}),
                exit_code,
                severity,
                json.dumps(analysis) if analysis else None
            ))
            conn.commit()

    @classmethod
    def get_job(cls, job_id: str) -> Optional[Dict[str, Any]]:
        """Get a job from database"""
        with cls.get_db() as conn:
            cursor = conn.execute('SELECT * FROM jobs WHERE id = ?', (job_id,))
            row = cursor.fetchone()
            if row:
                return cls._row_to_dict(row)
            return None

    @classmethod
    def list_jobs(cls, limit: int = 100) -> List[Dict[str, Any]]:
        """List all jobs ordered by creation date"""
        with cls.get_db() as conn:
            cursor = conn.execute(
                'SELECT * FROM jobs ORDER BY created_at DESC LIMIT ?',
                (limit,)
            )
            return [cls._row_to_dict(row) for row in cursor.fetchall()]

    @classmethod
    def delete_job(cls, job_id: str) -> bool:
        """Delete a job from database"""
        with cls.get_db() as conn:
            cursor = conn.execute('DELETE FROM jobs WHERE id = ?', (job_id,))
            conn.commit()
            return cursor.rowcount > 0

    @classmethod
    def append_log(cls, job_id: str, log_text: str):
        """Append text to job log"""
        with cls.get_db() as conn:
            # Get current log
            cursor = conn.execute('SELECT log FROM jobs WHERE id = ?', (job_id,))
            row = cursor.fetchone()
            if row:
                current_log = row['log'] or ''
                new_log = current_log + log_text
                conn.execute('UPDATE jobs SET log = ? WHERE id = ?', (new_log, job_id))
                conn.commit()

    @classmethod
    def update_status(cls, job_id: str, status: str, finished_at: Optional[datetime] = None):
        """Update job status"""
        with cls.get_db() as conn:
            if finished_at:
                conn.execute(
                    'UPDATE jobs SET status = ?, finished_at = ? WHERE id = ?',
                    (status, finished_at.isoformat(), job_id)
                )
            else:
                conn.execute(
                    'UPDATE jobs SET status = ? WHERE id = ?',
                    (status, job_id)
                )
            conn.commit()

    @classmethod
    def _row_to_dict(cls, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert database row to dictionary"""
        return {
            'id': row['id'],
            'type': row['type'],
            'status': row['status'],
            'created_at': row['created_at'],
            'finished_at': row['finished_at'],
            'summary': row['summary'] or '',
            'log': row['log'] or '',
            'output_files': json.loads(row['output_files']) if row['output_files'] else {},
            'exit_code': row['exit_code'],
            'severity': row['severity'] or 'UNKNOWN',
            'analysis': json.loads(row['analysis']) if row['analysis'] else None
        }
