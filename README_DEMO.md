# Agile ACP Tool - Demo Branch

This branch contains a **demo version** of the application that simulates all operations without requiring actual Agile PLM servers or database connections.

## Features

### Demo Mode Capabilities

- **Simulated Job Execution**: All ACP and Averify operations are simulated
- **Realistic Progress**: Jobs show progressive status updates over configurable duration
- **Success Scenarios**: All jobs complete successfully after the configured duration
- **Live Logs**: Simulated log output appears progressively during execution
- **Visual Indicator**: Orange "DEMO MODE" badge displayed in the header

### Simulated Operations

1. **ACP Export**
   - Simulates connection to Agile PLM
   - Shows progressive steps (authentication, data fetching, bundle creation)
   - Generates mock export bundle file
   - Completes after ~60 seconds (configurable)

2. **ACP Import**
   - Simulates bundle import process
   - Shows progressive import steps
   - Displays successful import confirmation
   - Completes after ~60 seconds (configurable)

3. **Averify**
   - Simulates database comparison
   - Shows comparison progress
   - Generates mock comparison statistics
   - Completes after ~60 seconds (configurable)

## Configuration

### Environment Variables

You can customize the demo mode behavior using environment variables:

```bash
# Enable/disable demo mode (default: true on demo branch)
DEMO_MODE=true

# Set job duration in seconds (default: 60)
DEMO_JOB_DURATION=60
```

### Quick Start

1. **Install dependencies**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run the application**:
   ```bash
   python run.py
   ```

3. **Access the application**:
   - Open browser to http://localhost:5000
   - Login with default credentials (if configured)
   - Notice the orange "DEMO MODE" badge in the header

4. **Test the demo**:
   - Go to ACP Operations panel
   - Select any operation (Export/Import)
   - Choose source/target environments
   - Upload any XML file (content doesn't matter in demo mode)
   - Click Execute
   - Navigate to Jobs panel to watch the simulated progress

## Testing Scenarios

### Basic Flow Test
1. Create a test environment in Configuration panel
2. Go to ACP Operations
3. Select "Export" operation
4. Choose the test environment
5. Upload a dummy config.xml file
6. Click Execute
7. Observe job running for ~60 seconds
8. Verify job completes with success status

### Multiple Jobs Test
1. Start multiple jobs quickly
2. Navigate to Jobs panel
3. Observe all jobs running concurrently
4. Watch as each completes after its duration

## Differences from Production

### What Works in Demo Mode
- ✅ All UI interactions
- ✅ Job creation and tracking
- ✅ Progressive log output
- ✅ Job status updates
- ✅ Environment management
- ✅ User authentication

### What's Simulated
- 🎭 ACP command execution
- 🎭 Averify execution
- 🎭 File operations (export bundles)
- 🎭 SSH connections
- 🎭 Database operations

### Not Available in Demo
- ❌ Actual Agile PLM connections
- ❌ Real export/import operations
- ❌ Actual file generation
- ❌ Database verification
- ❌ Error scenarios (all jobs succeed)

## Switching Modes

### To Production Mode
```bash
# Set environment variable
export DEMO_MODE=false

# Or edit config.py
DEMO_MODE = False
```

### To Demo Mode
```bash
# Set environment variable
export DEMO_MODE=true

# Or edit config.py
DEMO_MODE = True
```

## Development

### Adding New Demo Operations

To add a new simulated operation:

1. Add method to `app/services/demo_service.py`:
```python
@staticmethod
def simulate_new_operation(params):
    # Simulate operation logic
    time.sleep(Config.DEMO_JOB_DURATION)
    return {
        'log': 'Operation log...',
        'exit_code': 0,
        'severity': 'SUCCESS',
        'analysis': {...},
        'summary': 'Operation completed'
    }
```

2. Update route in `app/routes/jobs.py`:
```python
def _run():
    if Config.DEMO_MODE:
        return demo_service.simulate_new_operation(params)
    return actual_service.run_operation(params)
```

### Customizing Demo Duration

Different jobs can have different durations:

```python
# In demo_service.py
demo_service.simulate_acp_export(
    host=host,
    product_line=product_line,
    duration=30  # 30 seconds instead of default 60
)
```

## Use Cases

This demo branch is perfect for:

- **Sales Demonstrations**: Show the tool without infrastructure
- **Training Sessions**: Let users practice without risk
- **UI Development**: Test frontend changes without backend
- **Presentations**: Reliable, predictable demonstrations
- **Onboarding**: Help new team members understand the workflow

## Support

For issues or questions about demo mode:
1. Check the console for any JavaScript errors
2. Verify DEMO_MODE=true in config
3. Check Python logs for backend issues
4. Ensure all dependencies are installed

## Branch Management

This is a separate branch maintained for demo purposes:

```bash
# Switch to demo branch
git checkout demo

# Switch back to main
git checkout main

# Update demo from main (if needed)
git checkout demo
git merge main
```

---

**Note**: This demo mode is designed for demonstration and testing purposes only. For production use, switch to the main branch and configure real Agile PLM connections.
