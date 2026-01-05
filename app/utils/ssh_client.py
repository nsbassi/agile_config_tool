import paramiko
from typing import Optional, Tuple


class SSHClientWrapper:
    def __init__(self, hostname: str, username: str, port: int = 22,
                 password: Optional[str] = None, key_filename: Optional[str] = None):
        self.hostname = hostname
        self.username = username
        self.port = port
        self.password = password
        self.key_filename = key_filename
        self.client: Optional[paramiko.SSHClient] = None

    def __enter__(self):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(
            hostname=self.hostname,
            port=self.port,
            username=self.username,
            password=self.password,
            key_filename=self.key_filename,
            look_for_keys=False,
        )
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.client:
            self.client.close()

    def run(self, command: str, work_dir: Optional[str] = None) -> Tuple[int, str, str]:
        assert self.client
        if work_dir:
            command = f'cd {work_dir} && ' + command
        stdin, stdout, stderr = self.client.exec_command(command)
        out = stdout.read().decode('utf-8', errors='ignore')
        err = stderr.read().decode('utf-8', errors='ignore')
        exit_code = stdout.channel.recv_exit_status()
        return exit_code, out, err
