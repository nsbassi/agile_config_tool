import os
import glob
import shlex
import subprocess
from typing import Dict, Optional

from config import Config
from app.utils.ssh_client import SSHClientWrapper
from app.services.acp_log_parser import ACPLogParser


class AcpService:
    def __init__(self):
        self.export_cmd = Config.ACP_EXPORT_CMD
        self.import_cmd = Config.ACP_IMPORT_CMD

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

    def run_acp_export(self, host: str, xml_config_path: str, product_line: str,
                       work_dir: str, remote: bool = False,
                       ssh_config: Optional[Dict] = None) -> Dict:
        xml_name = os.path.basename(xml_config_path)
        local_xml = os.path.join(work_dir, xml_name)
        if os.path.exists(xml_config_path):
            with open(xml_config_path, 'rb') as src, open(local_xml, 'wb') as dst:
                dst.write(src.read())
        cmd = f"{self.export_cmd} --host {shlex.quote(host)} --product-line {shlex.quote(product_line)} --config {shlex.quote(xml_name)}"
        if remote:
            res = self._ssh_run(cmd, work_dir, ssh_config)
        else:
            res = self._local_run(cmd, work_dir)

        # Parse log and analyze outcome
        analysis = ACPLogParser.parse_log(res['log'], res['exit_code'])
        formatted_summary = ACPLogParser.format_summary(analysis)

        bundle_candidates = glob.glob(os.path.join(
            work_dir, '*.xml')) + glob.glob(os.path.join(work_dir, '*.zip'))
        outputs = {os.path.basename(p): p for p in bundle_candidates}

        return {
            'log': res['log'],
            'output_files': outputs,
            'summary': formatted_summary,
            'analysis': analysis.to_dict(),
            'exit_code': analysis.exit_code,
            'severity': analysis.severity,
        }

    def run_acp_import(self, host: str, xml_config_path: str, export_bundle_path: str,
                       work_dir: str, remote: bool = False,
                       ssh_config: Optional[Dict] = None) -> Dict:
        xml_name = os.path.basename(xml_config_path)
        local_xml = os.path.join(work_dir, xml_name)
        if os.path.exists(xml_config_path):
            with open(xml_config_path, 'rb') as src, open(local_xml, 'wb') as dst:
                dst.write(src.read())
        bundle_name = os.path.basename(export_bundle_path)
        local_bundle = os.path.join(work_dir, bundle_name)
        if os.path.exists(export_bundle_path):
            with open(export_bundle_path, 'rb') as src, open(local_bundle, 'wb') as dst:
                dst.write(src.read())
        cmd = f"{self.import_cmd} --host {shlex.quote(host)} --config {shlex.quote(xml_name)} --bundle {shlex.quote(bundle_name)}"
        if remote:
            res = self._ssh_run(cmd, work_dir, ssh_config)
        else:
            res = self._local_run(cmd, work_dir)

        # Parse log and analyze outcome
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
