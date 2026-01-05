# ACP Log Analysis and Exit Code Handling

## Overview

The Agile Configuration Management platform now includes comprehensive log analysis and exit code interpretation for ACP operations. This feature helps users quickly understand the outcome of their operations and identify issues.

## Features

### 1. Exit Code Interpretation

The tool recognizes and interprets standard ACP exit codes:

| Exit Code | Severity | Description |
|-----------|----------|-------------|
| 0 | SUCCESS | Operation completed successfully |
| 1 | CRITICAL | General error occurred during operation |
| 2 | ERROR | Failed to connect to database or server |
| 3 | ERROR | Authentication failed - check credentials |
| 4 | ERROR | Configuration file is invalid or malformed |
| 5 | ERROR | Required file not found - check file paths |
| 6 | ERROR | Permission denied - check file and directory permissions |
| 7 | WARNING | Data validation error - check data integrity |
| 8 | WARNING | Operation timed out - check network and server status |
| 9 | CANCELLED | Operation was cancelled by user |

### 2. Intelligent Log Parsing

The log parser automatically extracts and analyzes:

- **Error Messages**: Captures all ERROR, SEVERE, and FATAL log entries
- **Warnings**: Identifies all WARN and WARNING entries
- **Processing Statistics**: Extracts counts of processed, failed, and skipped items
- **Duration**: Captures operation duration from logs
- **Summary Sections**: Identifies and extracts summary information

### 3. Smart Exit Code Detection

Even when the reported exit code is 0, the parser analyzes log content for:

- Connection errors (returns exit code 2)
- Authentication failures (returns exit code 3)
- Configuration errors (returns exit code 4)
- General errors (returns exit code 1)

This ensures accurate reporting even when the underlying command doesn't properly report its exit status.

## API Usage

### Get Job with Analysis

```http
GET /api/jobs/{jobId}
```

Response includes:
```json
{
  "id": "job-uuid",
  "type": "acp-export",
  "status": "success",
  "exitCode": 0,
  "severity": "SUCCESS",
  "summary": "Operation completed successfully",
  "analysis": {
    "exitCode": 0,
    "exitDescription": "Operation completed successfully",
    "severity": "SUCCESS",
    "stats": {
      "totalLines": 150,
      "errorCount": 0,
      "warningCount": 2,
      "infoCount": 45,
      "processedItems": 100,
      "failedItems": 0,
      "skippedItems": 0
    },
    "duration": "30s"
  }
}
```

### Get Detailed Analysis

```http
GET /api/jobs/{jobId}/analysis
```

Response includes detailed error and warning lists:
```json
{
  "jobId": "job-uuid",
  "exitCode": 1,
  "severity": "CRITICAL",
  "analysis": {
    "errors": [
      {
        "level": "ERROR",
        "message": "Connection timeout - retrying...",
        "line": 45
      }
    ],
    "warnings": [
      {
        "level": "WARN",
        "message": "Skipping invalid data",
        "line": 67
      }
    ],
    "summary": [
      "Total items processed: 98",
      "Failed items: 2"
    ]
  },
  "summary": "Formatted summary text..."
}
```

## Frontend Integration

### Job Status Display

The job list and detail views now show:

1. **Visual Indicators**: Color-coded severity badges
   - GREEN: SUCCESS
   - YELLOW: WARNING
   - RED: ERROR/CRITICAL
   - GRAY: CANCELLED

2. **Exit Code**: Displayed with human-readable description

3. **Quick Stats**: 
   - Error count
   - Warning count
   - Items processed/failed

### Enhanced Log Viewer

The log viewer can now:

1. **Highlight Errors**: Automatically highlights ERROR and SEVERE entries
2. **Show Summary**: Displays formatted summary at the top
3. **Filter by Level**: Filter log entries by INFO, WARN, ERROR
4. **Jump to Errors**: Quick navigation to first error in log

## Benefits

1. **Faster Troubleshooting**: Quickly identify what went wrong
2. **Better Reporting**: Clear summaries for stakeholders
3. **Proactive Monitoring**: Catch issues even when exit code is 0
4. **Historical Analysis**: Analyze past job outcomes efficiently

## Implementation Details

### ACPLogParser Class

Location: `app/services/acp_log_parser.py`

Key methods:
- `parse_log(log_text, exit_code)`: Main parsing method
- `format_summary(analysis)`: Creates human-readable summary
- `ACPExitCode.get_description(code)`: Get exit code description
- `ACPExitCode.get_severity(code)`: Get severity level

### Integration Points

1. **ACP Service** (`app/services/acp_service.py`):
   - Calls log parser after each operation
   - Returns analysis data with results

2. **Averify Service** (`app/services/averify_service.py`):
   - Uses same parser for consistency
   - Returns analysis data

3. **Job Manager** (`app/services/job_manager.py`):
   - Stores exit code, severity, and analysis
   - Determines job status based on exit code

4. **Jobs API** (`app/routes/jobs.py`):
   - Exposes analysis via `/analysis` endpoint
   - Includes analysis in job details

## Testing

Run the test suite:

```bash
python test_log_parser.py
```

This demonstrates:
- Exit code interpretation
- Log parsing with various scenarios
- API format output
- Summary formatting

## Future Enhancements

1. **Email Notifications**: Send alerts for ERROR severity jobs
2. **Metrics Dashboard**: Aggregate statistics across all jobs
3. **Pattern Recognition**: Learn from past logs to predict issues
4. **Custom Rules**: Allow users to define custom error patterns
