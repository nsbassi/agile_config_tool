"""
Demo Service - Simulates job execution for demo purposes
"""
import os
import time
import random
import datetime
from typing import Dict
from config import Config


class DemoService:
    """Service for simulating job execution in demo mode"""

    @staticmethod
    def _read_sample_log(filename: str) -> str:
        """Read sample log file from demo_logs directory"""
        demo_logs_dir = os.path.join(os.path.dirname(
            os.path.dirname(__file__)), 'demo_logs')
        log_path = os.path.join(demo_logs_dir, filename)

        if os.path.exists(log_path):
            try:
                with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            except Exception:
                pass

        # Fallback to simple message if file not found
        return f"[DEMO MODE] Sample log file not found: {filename}\n"

    @staticmethod
    def simulate_acp_export(host: str, product_line: str, work_dir: str = None, duration: int = None) -> Dict:
        """Simulate ACP export operation"""
        duration = duration or Config.DEMO_JOB_DURATION

        # Capture start time
        start_time = datetime.datetime.now()
        start_date_str = start_time.strftime("%b %d, %Y %I:%M:%S %p")

        # Read the actual export.log sample
        log = DemoService._read_sample_log('export.log')

        # Simulate processing time
        time.sleep(duration)

        # Capture end time
        end_time = datetime.datetime.now()
        end_date_str = end_time.strftime("%b %d, %Y %I:%M:%S %p")
        duration_delta = end_time - start_time
        hours, remainder = divmod(int(duration_delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        duration_str = f"{hours}:{minutes}:{seconds}.{duration_delta.microseconds // 1000}"

        # Replace timestamps in log
        log = log.replace('Jan 5, 2026 9:32:16 AM', start_date_str)
        log = log.replace('Jan 5, 2026 9:32:32 AM', end_date_str)
        log = log.replace('0:0:0:16.386', duration_str)

        # Add demo mode header
        demo_header = f"[DEMO MODE] Starting ACP Export\n"
        demo_header += f"Host: {host}\n"
        demo_header += f"Product Line: {product_line}\n"
        demo_header += f"Simulating export process for {duration} seconds...\n\n"
        demo_header += "=" * 70 + "\n\n"

        full_log = demo_header + log

        # Write export.log to work directory if provided
        if work_dir:
            log_path = os.path.join(work_dir, 'export.log')
            try:
                with open(log_path, 'w', encoding='utf-8') as f:
                    f.write(log)
            except Exception:
                pass

        return {
            'log': full_log,
            'output_files': {
                f'export_{product_line}_{int(time.time())}.zip': f'/demo/output/export_{product_line}.zip'
            },
            'exit_code': 0,
            'severity': 'SUCCESS',
            'analysis': {
                'success': True,
                'objects_exported': 2,
                'warnings': 0,
                'errors': 0
            },
            'summary': f'Export completed successfully for {product_line}'
        }

    @staticmethod
    def simulate_acp_import(host: str, work_dir: str = None, duration: int = None) -> Dict:
        """Simulate ACP import operation"""
        duration = duration or Config.DEMO_JOB_DURATION

        # Capture start time
        start_time = datetime.datetime.now()
        start_date_str = start_time.strftime("%b %d, %Y %I:%M:%S %p")

        # Read the actual import.log sample
        log = DemoService._read_sample_log('import.log')

        # Simulate processing time
        time.sleep(duration)

        # Capture end time
        end_time = datetime.datetime.now()
        end_date_str = end_time.strftime("%b %d, %Y %I:%M:%S %p")
        duration_delta = end_time - start_time
        hours, remainder = divmod(int(duration_delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        duration_str = f"{hours}:{minutes}:{seconds}.{duration_delta.microseconds // 1000}"

        # Replace timestamps in log
        log = log.replace('Jan 5, 2026 9:37:28 AM', start_date_str)
        log = log.replace('Jan 5, 2026 9:38:09 AM', end_date_str)
        log = log.replace('0:0:0:40.976', duration_str)

        # Add demo mode header
        demo_header = f"[DEMO MODE] Starting ACP Import\n"
        demo_header += f"Host: {host}\n"
        demo_header += f"Simulating import process for {duration} seconds...\n\n"
        demo_header += "=" * 70 + "\n\n"

        full_log = demo_header + log

        # Write import.log to work directory if provided
        if work_dir:
            log_path = os.path.join(work_dir, 'import.log')
            try:
                with open(log_path, 'w', encoding='utf-8') as f:
                    f.write(log)
            except Exception:
                pass

        return {
            'log': full_log,
            'output_files': {},
            'exit_code': 0,
            'severity': 'SUCCESS',
            'analysis': {
                'success': True,
                'objects_imported': 2,
                'warnings': 0,
                'errors': 0
            },
            'summary': f'Import completed successfully'
        }

    @staticmethod
    def simulate_averify(source_env: str, target_env: str, duration: int = None) -> Dict:
        """Simulate Averify operation"""
        duration = duration or Config.DEMO_JOB_DURATION

        log = f"[DEMO MODE] Starting Averify\n"
        log += f"Source Environment: {source_env}\n"
        log += f"Target Environment: {target_env}\n\n"

        steps = [
            "Connecting to source database...",
            "Connecting to target database...",
            "Loading verification configuration",
            "Comparing schema structures...",
            "Comparing Classes...",
            "Comparing Workflows...",
            "Comparing Users and Groups...",
            "Comparing Attributes...",
            "Analyzing differences...",
            "Generating comparison report...",
            "Verification completed!"
        ]

        step_duration = duration / len(steps)
        for i, step in enumerate(steps):
            time.sleep(step_duration)
            log += f"[{i+1}/{len(steps)}] {step}\n"

        matches = random.randint(80, 95)
        differences = 100 - matches

        log += f"\n=== Verification Summary ===\n"
        log += f"Total objects compared: {random.randint(100, 1000)}\n"
        log += f"Matching: {matches}%\n"
        log += f"Differences found: {differences}\n"
        log += f"Operation completed successfully in {duration} seconds\n"

        return {
            'log': log,
            'output_files': {
                'averify_report.html': '/demo/output/averify_report.html'
            },
            'exit_code': 0,
            'severity': 'SUCCESS',
            'analysis': {
                'success': True,
                'total_compared': random.randint(100, 1000),
                'matches': matches,
                'differences': differences,
                'warnings': differences,
                'errors': 0
            },
            'summary': f'Verification completed for {source_env} and {target_env}'
        }

    @staticmethod
    def simulate_file_copy(target_env: str, work_dir: str = None, duration: int = None) -> Dict:
        """Simulate File Copy operation"""
        duration = duration or Config.DEMO_JOB_DURATION

        # Capture start time
        start_time = datetime.datetime.now()
        start_date_str = start_time.strftime("%b %d, %Y %I:%M:%S %p")

        # Read the actual filecopy.log sample
        log = DemoService._read_sample_log('filecopy.log')

        # Simulate processing time
        time.sleep(duration)

        # Capture end time
        end_time = datetime.datetime.now()
        end_date_str = end_time.strftime("%b %d, %Y %I:%M:%S %p")
        duration_delta = end_time - start_time
        hours, remainder = divmod(int(duration_delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        duration_str = f"{hours}:{minutes}:{seconds}.{duration_delta.microseconds // 1000}"

        # Replace timestamps in log
        log = log.replace('Jan 5, 2026 10:15:30 AM', start_date_str)
        log = log.replace('Jan 5, 2026 10:15:52 AM', end_date_str)
        log = log.replace('0:0:0:22.500', duration_str)

        # Replace target environment
        log = log.replace('Target Environment:     QA',
                          f'Target Environment:     {target_env}')

        # Add demo mode header
        demo_header = f"[DEMO MODE] Starting File Copy\n"
        demo_header += f"Target Environment: {target_env}\n"
        demo_header += f"Simulating file copy process for {duration} seconds...\n\n"
        demo_header += "=" * 70 + "\n\n"

        full_log = demo_header + log

        # Write filecopy.log to work directory if provided
        if work_dir:
            log_path = os.path.join(work_dir, 'filecopy.log')
            try:
                with open(log_path, 'w', encoding='utf-8') as f:
                    f.write(log)
            except Exception:
                pass

        return {
            'log': full_log,
            'output_files': {
                'filecopy_summary.txt': '/demo/output/filecopy_summary.txt'
            },
            'exit_code': 0,
            'severity': 'SUCCESS',
            'analysis': {
                'success': True,
                'files_copied': 178,
                'total_size_mb': 342.7,
                'warnings': 0,
                'errors': 0
            },
            'summary': f'File copy completed successfully to {target_env}'
        }


demo_service = DemoService()
