import os
import shlex
import subprocess
from typing import Dict, Optional

from config import Config
from app.utils.ssh_client import SSHClientWrapper
from app.services.acp_log_parser import ACPLogParser


class AverifyService:
    def __init__(self):
        self.averify_cmd = Config.AVERIFY_CMD

    def _local_run(self, cmd: str, work_dir: str) -> Dict[str, str]:
        proc = subprocess.Popen(
            cmd,
            cwd=work_dir,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        out, _ = proc.communicate()
        log = out.decode('utf-8', errors='ignore')
        return {'exit_code': proc.returncode, 'log': log}

    def _ssh_run(self, cmd: str, work_dir: str, ssh_config: Dict) -> Dict[str, str]:
        with SSHClientWrapper(**ssh_config) as client:
            exit_code, out, err = client.run(cmd, work_dir)
        log = out + ('\n' + err if err else '')
        return {'exit_code': exit_code, 'log': log}

    def run_averify(self, host: str, source_env: str, target_env: str,
                    config_path: Optional[str], work_dir: str,
                    remote: bool = False, ssh_config: Optional[Dict] = None) -> Dict:
        cfg_arg = ''
        if config_path and os.path.exists(config_path):
            name = os.path.basename(config_path)
            local_cfg = os.path.join(work_dir, name)
            with open(config_path, 'rb') as src, open(local_cfg, 'wb') as dst:
                dst.write(src.read())
            cfg_arg = f" --config {shlex.quote(name)}"
        cmd = f"{self.averify_cmd} --host {shlex.quote(host)} --source {shlex.quote(source_env)} --target {shlex.quote(target_env)}{cfg_arg}"
        if remote:
            res = self._ssh_run(cmd, work_dir, ssh_config)
        else:
            res = self._local_run(cmd, work_dir)

        # Parse log and analyze outcome (Averify uses similar logging patterns)
        analysis = ACPLogParser.parse_log(res['log'], res['exit_code'])
        formatted_summary = ACPLogParser.format_summary(analysis)

        return {
            'log': res['log'],
            'output_files': {},
            'summary': formatted_summary,
            'analysis': analysis.to_dict(),
            'exit_code': analysis.exit_code,
            'severity': analysis.severity,
        }
