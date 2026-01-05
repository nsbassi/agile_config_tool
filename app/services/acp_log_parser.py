"""
ACP Log Parser - Analyzes ACP program logs and extracts meaningful information
Based on ACP Exit Codes and Program Logs documentation
"""
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ACPExitCode(Enum):
    """ACP Exit Codes as documented in ACP documentation"""
    SUCCESS = 0  # Successful completion
    GENERAL_ERROR = 1  # General error
    CONNECTION_ERROR = 2  # Database/Server connection error
    AUTHENTICATION_ERROR = 3  # Authentication failed
    INVALID_CONFIG = 4  # Invalid configuration file
    MISSING_FILE = 5  # Required file not found
    PERMISSION_ERROR = 6  # Permission denied
    DATA_ERROR = 7  # Data validation error
    TIMEOUT_ERROR = 8  # Operation timeout
    CANCELLED = 9  # Operation cancelled by user

    @classmethod
    def get_description(cls, code: int) -> str:
        """Get human-readable description for exit code"""
        descriptions = {
            0: "Operation completed successfully",
            1: "General error occurred during operation",
            2: "Failed to connect to database or server",
            3: "Authentication failed - check credentials",
            4: "Configuration file is invalid or malformed",
            5: "Required file not found - check file paths",
            6: "Permission denied - check file and directory permissions",
            7: "Data validation error - check data integrity",
            8: "Operation timed out - check network and server status",
            9: "Operation was cancelled by user",
        }
        return descriptions.get(code, f"Unknown exit code: {code}")

    @classmethod
    def get_severity(cls, code: int) -> str:
        """Get severity level for exit code"""
        if code == 0:
            return "SUCCESS"
        elif code in [2, 3, 4, 5, 6]:
            return "ERROR"
        elif code in [7, 8]:
            return "WARNING"
        elif code == 9:
            return "CANCELLED"
        else:
            return "CRITICAL"


@dataclass
class LogEntry:
    """Represents a single log entry"""
    timestamp: Optional[str]
    level: str
    message: str
    line_number: int


@dataclass
class ACPLogAnalysis:
    """Analysis result of ACP log"""
    exit_code: int
    exit_description: str
    severity: str
    total_lines: int
    error_count: int
    warning_count: int
    info_count: int
    errors: List[LogEntry]
    warnings: List[LogEntry]
    summary_lines: List[str]
    processed_items: int
    failed_items: int
    skipped_items: int
    duration: Optional[str]

    def to_dict(self) -> Dict:
        """Convert analysis to dictionary"""
        return {
            'exitCode': self.exit_code,
            'exitDescription': self.exit_description,
            'severity': self.severity,
            'stats': {
                'totalLines': self.total_lines,
                'errorCount': self.error_count,
                'warningCount': self.warning_count,
                'infoCount': self.info_count,
                'processedItems': self.processed_items,
                'failedItems': self.failed_items,
                'skippedItems': self.skipped_items,
            },
            'duration': self.duration,
            'errors': [{'level': e.level, 'message': e.message, 'line': e.line_number} for e in self.errors[:10]],
            'warnings': [{'level': w.level, 'message': w.message, 'line': w.line_number} for w in self.warnings[:10]],
            'summary': self.summary_lines,
        }


class ACPLogParser:
    """Parser for ACP program logs"""

    # Common log patterns
    LOG_LEVEL_PATTERN = re.compile(
        r'\[(ERROR|WARN|WARNING|INFO|DEBUG|SEVERE|FATAL)\]', re.IGNORECASE)
    TIMESTAMP_PATTERN = re.compile(
        r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}|\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2})')

    # Item processing patterns
    PROCESSED_PATTERN = re.compile(
        r'(?:processed|completed|exported|imported)\s+(\d+)\s+(?:item|object|record|row)', re.IGNORECASE)
    FAILED_PATTERN = re.compile(
        r'(?:failed|error)\s+(\d+)\s+(?:item|object|record|row)', re.IGNORECASE)
    SKIPPED_PATTERN = re.compile(
        r'(?:skipped|ignored)\s+(\d+)\s+(?:item|object|record|row)', re.IGNORECASE)

    # Summary patterns
    SUMMARY_START_PATTERN = re.compile(
        r'(?:Summary|Statistics|Results):', re.IGNORECASE)
    DURATION_PATTERN = re.compile(
        r'(?:Duration|Elapsed|Time):\s*(\d+[hms\s]+)', re.IGNORECASE)

    # Error specific patterns
    CONNECTION_ERROR_PATTERNS = [
        r'connection\s+(?:failed|refused|timeout)',
        r'could\s+not\s+connect',
        r'unable\s+to\s+connect',
        r'network\s+(?:error|timeout)',
    ]

    AUTH_ERROR_PATTERNS = [
        r'authentication\s+failed',
        r'invalid\s+(?:credentials|username|password)',
        r'access\s+denied',
        r'login\s+failed',
    ]

    CONFIG_ERROR_PATTERNS = [
        r'(?:invalid|malformed)\s+configuration',
        r'config\s+(?:error|parse\s+error)',
        r'invalid\s+xml',
    ]

    @classmethod
    def parse_log(cls, log_text: str, exit_code: int = 0) -> ACPLogAnalysis:
        """Parse ACP log and extract meaningful information"""
        lines = log_text.split('\n')

        errors: List[LogEntry] = []
        warnings: List[LogEntry] = []
        summary_lines: List[str] = []

        error_count = 0
        warning_count = 0
        info_count = 0

        processed_items = 0
        failed_items = 0
        skipped_items = 0
        duration = None

        in_summary_section = False

        for i, line in enumerate(lines):
            if not line.strip():
                continue

            # Check for summary section
            if cls.SUMMARY_START_PATTERN.search(line):
                in_summary_section = True

            if in_summary_section:
                summary_lines.append(line.strip())

            # Extract timestamp
            timestamp_match = cls.TIMESTAMP_PATTERN.search(line)
            timestamp = timestamp_match.group(1) if timestamp_match else None

            # Extract log level
            level_match = cls.LOG_LEVEL_PATTERN.search(line)
            if level_match:
                level = level_match.group(1).upper()

                entry = LogEntry(
                    timestamp=timestamp,
                    level=level,
                    message=line,
                    line_number=i + 1
                )

                if level in ['ERROR', 'SEVERE', 'FATAL']:
                    error_count += 1
                    errors.append(entry)
                elif level in ['WARN', 'WARNING']:
                    warning_count += 1
                    warnings.append(entry)
                elif level == 'INFO':
                    info_count += 1

            # Extract statistics
            processed_match = cls.PROCESSED_PATTERN.search(line)
            if processed_match:
                processed_items = max(
                    processed_items, int(processed_match.group(1)))

            failed_match = cls.FAILED_PATTERN.search(line)
            if failed_match:
                failed_items = max(failed_items, int(failed_match.group(1)))

            skipped_match = cls.SKIPPED_PATTERN.search(line)
            if skipped_match:
                skipped_items = max(skipped_items, int(skipped_match.group(1)))

            # Extract duration
            duration_match = cls.DURATION_PATTERN.search(line)
            if duration_match and not duration:
                duration = duration_match.group(1)

        # Determine actual exit code if not provided or analyze log for issues
        analyzed_exit_code = cls._analyze_exit_code(log_text, exit_code)

        return ACPLogAnalysis(
            exit_code=analyzed_exit_code,
            exit_description=ACPExitCode.get_description(analyzed_exit_code),
            severity=ACPExitCode.get_severity(analyzed_exit_code),
            total_lines=len(lines),
            error_count=error_count,
            warning_count=warning_count,
            info_count=info_count,
            errors=errors,
            warnings=warnings,
            # Last 20 summary lines
            summary_lines=summary_lines[-20:] if summary_lines else [],
            processed_items=processed_items,
            failed_items=failed_items,
            skipped_items=skipped_items,
            duration=duration,
        )

    @classmethod
    def _analyze_exit_code(cls, log_text: str, reported_exit_code: int) -> int:
        """
        Analyze log content to determine actual exit code
        This helps when exit code is not properly reported or needs verification
        """
        if reported_exit_code == 0:
            # Even if exit code is 0, check for errors in log
            log_lower = log_text.lower()

            # Check for connection errors
            for pattern in cls.CONNECTION_ERROR_PATTERNS:
                if re.search(pattern, log_lower):
                    return 2  # Connection error

            # Check for authentication errors
            for pattern in cls.AUTH_ERROR_PATTERNS:
                if re.search(pattern, log_lower):
                    return 3  # Authentication error

            # Check for config errors
            for pattern in cls.CONFIG_ERROR_PATTERNS:
                if re.search(pattern, log_lower):
                    return 4  # Invalid config

            # Check for general errors
            if re.search(r'\[ERROR\]|\[SEVERE\]|\[FATAL\]', log_text, re.IGNORECASE):
                return 1  # General error

        return reported_exit_code

    @classmethod
    def format_summary(cls, analysis: ACPLogAnalysis) -> str:
        """Format analysis into human-readable summary"""
        lines = []
        lines.append("=" * 60)
        lines.append("ACP OPERATION SUMMARY")
        lines.append("=" * 60)
        lines.append(f"Exit Code: {analysis.exit_code}")
        lines.append(f"Status: {analysis.exit_description}")
        lines.append(f"Severity: {analysis.severity}")
        lines.append("")

        lines.append("STATISTICS:")
        lines.append(f"  Total Log Lines: {analysis.total_lines}")
        lines.append(f"  Errors: {analysis.error_count}")
        lines.append(f"  Warnings: {analysis.warning_count}")
        lines.append(f"  Info Messages: {analysis.info_count}")
        lines.append("")

        if analysis.processed_items > 0 or analysis.failed_items > 0:
            lines.append("PROCESSING RESULTS:")
            if analysis.processed_items > 0:
                lines.append(f"  Processed: {analysis.processed_items}")
            if analysis.failed_items > 0:
                lines.append(f"  Failed: {analysis.failed_items}")
            if analysis.skipped_items > 0:
                lines.append(f"  Skipped: {analysis.skipped_items}")
            lines.append("")

        if analysis.duration:
            lines.append(f"Duration: {analysis.duration}")
            lines.append("")

        if analysis.errors:
            lines.append("TOP ERRORS:")
            for i, error in enumerate(analysis.errors[:5], 1):
                lines.append(
                    f"  {i}. [Line {error.line_number}] {error.message.strip()}")
            if len(analysis.errors) > 5:
                lines.append(
                    f"  ... and {len(analysis.errors) - 5} more errors")
            lines.append("")

        if analysis.warnings:
            lines.append("TOP WARNINGS:")
            for i, warning in enumerate(analysis.warnings[:5], 1):
                lines.append(
                    f"  {i}. [Line {warning.line_number}] {warning.message.strip()}")
            if len(analysis.warnings) > 5:
                lines.append(
                    f"  ... and {len(analysis.warnings) - 5} more warnings")
            lines.append("")

        if analysis.summary_lines:
            lines.append("OPERATION SUMMARY:")
            for line in analysis.summary_lines:
                lines.append(f"  {line}")

        lines.append("=" * 60)
        return '\n'.join(lines)
