"""
Demo Service - Simulates job execution for demo purposes
"""
import time
import random
from typing import Dict
from config import Config


class DemoService:
    """Service for simulating job execution in demo mode"""
    
    @staticmethod
    def simulate_acp_export(host: str, product_line: str, duration: int = None) -> Dict:
        """Simulate ACP export operation"""
        duration = duration or Config.DEMO_JOB_DURATION
        
        log = f"[DEMO MODE] Starting ACP Export\n"
        log += f"Host: {host}\n"
        log += f"Product Line: {product_line}\n"
        log += f"Configuration loaded successfully\n\n"
        
        # Simulate progressive log output
        steps = [
            "Connecting to Agile PLM server...",
            "Authentication successful",
            "Loading configuration from config.xml",
            "Validating export criteria",
            "Fetching data from database",
            "Processing Classes...",
            "Processing Workflows...",
            "Processing Users and Groups...",
            "Processing Attributes...",
            "Generating export bundle...",
            "Compressing data...",
            "Export completed successfully!"
        ]
        
        step_duration = duration / len(steps)
        for i, step in enumerate(steps):
            time.sleep(step_duration)
            log += f"[{i+1}/{len(steps)}] {step}\n"
        
        log += f"\nExport bundle created: export_{product_line}_{int(time.time())}.zip\n"
        log += f"Total objects exported: {random.randint(50, 500)}\n"
        log += f"Operation completed successfully in {duration} seconds\n"
        
        return {
            'log': log,
            'output_files': {
                f'export_{product_line}_{int(time.time())}.zip': f'/demo/output/export_{product_line}.zip'
            },
            'exit_code': 0,
            'severity': 'SUCCESS',
            'analysis': {
                'success': True,
                'objects_exported': random.randint(50, 500),
                'warnings': 0,
                'errors': 0
            },
            'summary': f'Successfully exported {random.randint(50, 500)} objects from {product_line}'
        }
    
    @staticmethod
    def simulate_acp_import(host: str, duration: int = None) -> Dict:
        """Simulate ACP import operation"""
        duration = duration or Config.DEMO_JOB_DURATION
        
        log = f"[DEMO MODE] Starting ACP Import\n"
        log += f"Host: {host}\n"
        log += f"Configuration loaded successfully\n\n"
        
        steps = [
            "Connecting to Agile PLM server...",
            "Authentication successful",
            "Loading import bundle",
            "Validating bundle contents",
            "Checking dependencies...",
            "Importing Classes...",
            "Importing Workflows...",
            "Importing Users and Groups...",
            "Importing Attributes...",
            "Verifying imported data...",
            "Import completed successfully!"
        ]
        
        step_duration = duration / len(steps)
        for i, step in enumerate(steps):
            time.sleep(step_duration)
            log += f"[{i+1}/{len(steps)}] {step}\n"
        
        log += f"\nTotal objects imported: {random.randint(50, 500)}\n"
        log += f"Operation completed successfully in {duration} seconds\n"
        
        return {
            'log': log,
            'output_files': {},
            'exit_code': 0,
            'severity': 'SUCCESS',
            'analysis': {
                'success': True,
                'objects_imported': random.randint(50, 500),
                'warnings': 0,
                'errors': 0
            },
            'summary': f'Successfully imported {random.randint(50, 500)} objects'
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
            'summary': f'Verification complete: {matches}% match between {source_env} and {target_env}'
        }


demo_service = DemoService()
