import sqlite3
import json
from typing import List, Optional, Dict, Any
from contextlib import contextmanager
import os


class Environment:
    DB_PATH = 'environments.db'

    def __init__(self, id: Optional[int] = None, tag: str = '', agile_plm_url: str = '',
                 propagation_user: str = '', propagation_password: str = '',
                 dest_jdbc_url: str = '', dest_tns_name: str = '', dest_oracle_home: str = '',
                 dest_db_user: str = '', dest_db_password: str = '', acp_project_dir: str = ''):
        self.id = id
        self.tag = tag
        self.agile_plm_url = agile_plm_url
        self.propagation_user = propagation_user
        self.propagation_password = propagation_password
        self.dest_jdbc_url = dest_jdbc_url
        self.dest_tns_name = dest_tns_name
        self.dest_oracle_home = dest_oracle_home
        self.dest_db_user = dest_db_user
        self.dest_db_password = dest_db_password
        self.acp_project_dir = acp_project_dir

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
        """Initialize database table"""
        with cls.get_db() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS environments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tag TEXT NOT NULL UNIQUE,
                    agile_plm_url TEXT NOT NULL,
                    propagation_user TEXT NOT NULL,
                    propagation_password TEXT NOT NULL,
                    dest_jdbc_url TEXT,
                    dest_tns_name TEXT,
                    dest_oracle_home TEXT,
                    dest_db_user TEXT,
                    dest_db_password TEXT,
                    acp_project_dir TEXT
                )
            ''')

            # Migration: Add acp_project_dir column if it doesn't exist
            cursor = conn.execute("PRAGMA table_info(environments)")
            columns = [row[1] for row in cursor.fetchall()]
            if 'acp_project_dir' not in columns:
                conn.execute(
                    'ALTER TABLE environments ADD COLUMN acp_project_dir TEXT')

            conn.commit()

    def to_dict(self) -> Dict[str, Any]:
        """Convert environment to dictionary"""
        return {
            'id': self.id,
            'tag': self.tag,
            'agilePlmUrl': self.agile_plm_url,
            'propagationUser': self.propagation_user,
            'propagationPassword': self.propagation_password,
            'destJdbcUrl': self.dest_jdbc_url,
            'destTnsName': self.dest_tns_name,
            'destOracleHome': self.dest_oracle_home,
            'destDbUser': self.dest_db_user,
            'destDbPassword': self.dest_db_password,
            'acpProjectDir': self.acp_project_dir,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Environment':
        """Create environment from dictionary"""
        return cls(
            id=data.get('id'),
            tag=data.get('tag', ''),
            agile_plm_url=data.get('agilePlmUrl', ''),
            propagation_user=data.get('propagationUser', ''),
            propagation_password=data.get('propagationPassword', ''),
            dest_jdbc_url=data.get('destJdbcUrl', ''),
            dest_tns_name=data.get('destTnsName', ''),
            dest_oracle_home=data.get('destOracleHome', ''),
            dest_db_user=data.get('destDbUser', ''),
            dest_db_password=data.get('destDbPassword', ''),
            acp_project_dir=data.get('acpProjectDir', ''),
        )

    def save(self) -> 'Environment':
        """Save or update environment"""
        with self.get_db() as conn:
            if self.id:
                conn.execute('''
                    UPDATE environments 
                    SET tag = ?, agile_plm_url = ?, propagation_user = ?, 
                        propagation_password = ?, dest_jdbc_url = ?, dest_tns_name = ?, dest_oracle_home = ?,
                        dest_db_user = ?, dest_db_password = ?, acp_project_dir = ?
                    WHERE id = ?
                ''', (self.tag, self.agile_plm_url, self.propagation_user,
                      self.propagation_password, self.dest_jdbc_url, self.dest_tns_name, self.dest_oracle_home,
                      self.dest_db_user, self.dest_db_password, self.acp_project_dir, self.id))
            else:
                cursor = conn.execute('''
                    INSERT INTO environments (tag, agile_plm_url, propagation_user, 
                                            propagation_password, dest_jdbc_url, dest_tns_name, dest_oracle_home,
                                            dest_db_user, dest_db_password, acp_project_dir)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (self.tag, self.agile_plm_url, self.propagation_user,
                      self.propagation_password, self.dest_jdbc_url, self.dest_tns_name, self.dest_oracle_home,
                      self.dest_db_user, self.dest_db_password, self.acp_project_dir))
                self.id = cursor.lastrowid
            conn.commit()
        return self

    @classmethod
    def find_all(cls) -> List['Environment']:
        """Get all environments"""
        with cls.get_db() as conn:
            rows = conn.execute(
                'SELECT * FROM environments ORDER BY tag').fetchall()
            return [cls(
                id=row['id'],
                tag=row['tag'],
                agile_plm_url=row['agile_plm_url'],
                propagation_user=row['propagation_user'],
                propagation_password=row['propagation_password'],
                dest_jdbc_url=row['dest_jdbc_url'] if 'dest_jdbc_url' in row.keys(
                ) else '',
                dest_tns_name=row['dest_tns_name'] if 'dest_tns_name' in row.keys(
                ) else '',
                dest_oracle_home=row['dest_oracle_home'] if 'dest_oracle_home' in row.keys(
                ) else '',
                dest_db_user=row['dest_db_user'] if 'dest_db_user' in row.keys(
                ) else '',
                dest_db_password=row['dest_db_password'] if 'dest_db_password' in row.keys(
                ) else '',
                acp_project_dir=row['acp_project_dir'] if 'acp_project_dir' in row.keys(
                ) else ''
            ) for row in rows]

    @classmethod
    def find_by_id(cls, env_id: int) -> Optional['Environment']:
        """Find environment by ID"""
        with cls.get_db() as conn:
            row = conn.execute(
                'SELECT * FROM environments WHERE id = ?', (env_id,)).fetchone()
            if row:
                return cls(
                    id=row['id'],
                    tag=row['tag'],
                    agile_plm_url=row['agile_plm_url'],
                    propagation_user=row['propagation_user'],
                    propagation_password=row['propagation_password'],
                    dest_jdbc_url=row['dest_jdbc_url'] if 'dest_jdbc_url' in row.keys(
                    ) else '',
                    dest_tns_name=row['dest_tns_name'] if 'dest_tns_name' in row.keys(
                    ) else '',
                    dest_oracle_home=row['dest_oracle_home'] if 'dest_oracle_home' in row.keys(
                    ) else '',
                    dest_db_user=row['dest_db_user'] if 'dest_db_user' in row.keys(
                    ) else '',
                    dest_db_password=row['dest_db_password'] if 'dest_db_password' in row.keys(
                    ) else '',
                    acp_project_dir=row['acp_project_dir'] if 'acp_project_dir' in row.keys(
                    ) else ''
                )
        return None

    @classmethod
    def find_by_tag(cls, tag: str) -> Optional['Environment']:
        """Find environment by tag"""
        with cls.get_db() as conn:
            row = conn.execute(
                'SELECT * FROM environments WHERE tag = ?', (tag,)).fetchone()
            if row:
                return cls(
                    id=row['id'],
                    tag=row['tag'],
                    agile_plm_url=row['agile_plm_url'],
                    propagation_user=row['propagation_user'],
                    propagation_password=row['propagation_password'],
                    dest_jdbc_url=row['dest_jdbc_url'] if 'dest_jdbc_url' in row.keys(
                    ) else '',
                    dest_tns_name=row['dest_tns_name'] if 'dest_tns_name' in row.keys(
                    ) else '',
                    dest_oracle_home=row['dest_oracle_home'] if 'dest_oracle_home' in row.keys(
                    ) else '',
                    dest_db_user=row['dest_db_user'] if 'dest_db_user' in row.keys(
                    ) else '',
                    acp_project_dir=row['acp_project_dir'] if 'acp_project_dir' in row.keys(
                    ) else '',
                    dest_db_password=row['dest_db_password'] if 'dest_db_password' in row.keys(
                    ) else ''
                )
        return None

    def delete(self) -> bool:
        """Delete environment"""
        if not self.id:
            return False
        with self.get_db() as conn:
            conn.execute('DELETE FROM environments WHERE id = ?', (self.id,))
            conn.commit()
        return True


# Initialize database on module import
Environment.init_db()
