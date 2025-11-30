# Epifania

A GUI-based Dynamic Instrumentation Platform wrapping Frida and ADB for security researchers.


## Project Status

**Current Stage:** Active Development

**Implemented Features:**
- ✅ Native ADB integration for reliable Android device detection and communication
- ✅ Full Frida server lifecycle management with operational start/stop/restart controls
- ✅ Backend API with FastAPI serving comprehensive device information
- ✅ Security tool interface with dark theme (#7100d0 primary color)
- ✅ Device enumeration with detailed specifications (brand, model, Android version, architecture, root status)
- ✅ Frida availability detection per device
- ✅ Real-time ADB connection status monitoring
- ✅ Interactive UI with button feedback, focus states, and disabled state handling
- ✅ Responsive device cards with hover effects and status indicators
- ✅ Centralized logging system with categorized directories and automatic Frida failure diagnostics
- ✅ Virtual environment setup for Python and Node.js dependency isolation
- ✅ Automated startup scripts for development environment
- ✅ Frida server installation, management, and version control
- ✅ Real-time log streaming via WebSocket (logcat, Frida operations, ADB operations)
- ✅ Tabbed device details interface with query parameter routing
- ✅ Device tab with Frida server controls and management
- ✅ Frida server start/stop/restart controls
- ✅ Cached Frida server management and deployment
- ✅ Auto-refresh device list with connection state tracking
- ✅ Vue Router integration with multi-page navigation and deep linking
- ✅ Health monitoring system with periodic checks
- ✅ Process management with cleanup and PID tracking
- ✅ Backend auto-reconnect with exponential backoff
- ✅ Toast notification system with pinning capability
- ✅ Frida server discovery and scanning on devices
- ✅ Permission management for Frida binaries
- ✅ Recommended Frida version detection based on device
- ✅ Frida connection testing and validation
- ✅ Multiple Frida server cleanup functionality
- ✅ Comprehensive ADB diagnostics system
- ✅ Custom Frida version download with architecture selection
- ✅ Compact UI with information density optimization
- ✅ Modal-based detailed information views
- ✅ Direct GitHub API integration for Frida releases
- ✅ Tab navigation infrastructure with reusable components
- ✅ Processes tab with real-time process monitoring, inspection, and termination
- ✅ Process metrics collection with historical data tracking
- ✅ System resource monitoring (CPU, memory, storage, network)
- ✅ Process churn tracking (spawned/killed processes over time)
- ✅ Network connection monitoring with per-process TCP connections
- ✅ Storage partition monitoring with usage statistics
- ✅ Android process state detection via ActivityManager (foreground, cached, persistent, etc.)
- ✅ Process State Dictionary with detailed state explanations
- ✅ Kernel thread filtering with show/hide toggle
- ✅ Memory delta tracking with visual change indicators
- ✅ Educational help modals for CPU, Memory, and Process List interpretation
- ✅ Modular frontend architecture with feature-based directory structure
- ✅ Unified launcher script for cross-platform deployment

**In Development:**
- 🔄 Packages tab for application catalog and lifecycle control
- 🔄 Files tab for device filesystem browsing
- 🔄 Workshop tab for script injection and active analysis

## Architecture

Epifania is a local web-based tool designed for security analysis and dynamic instrumentation of mobile applications. The platform consists of two main components:

### Backend (Python/FastAPI)

The backend serves as the orchestration layer, managing device connections and Frida instrumentation. It provides a RESTful API for frontend communication with native ADB integration.

- **FastAPI**: High-performance web framework for API endpoints
- **Frida**: Dynamic instrumentation toolkit for runtime analysis
- **Native ADB**: Direct Android Debug Bridge integration via subprocess for reliable device management and communication
- **Modular Architecture**: Separate managers for ADB, devices, installation tasks, health monitoring, and diagnostics

### Frontend (Vue.js/Vite)

The frontend provides a web-based dashboard for managing devices and Frida operations. It handles real-time communication with the backend via REST API and WebSocket connections.

- **Vue 3**: Progressive JavaScript framework with Composition API
- **Vue Router**: Client-side routing for multi-page navigation
- **Vite**: Fast build tool and development server
- **Tailwind CSS**: Utility-first CSS framework for styling
- **DaisyUI**: Component library with dark theme configuration
- **Axios**: HTTP client for API communication
- **WebSocket**: Real-time bidirectional communication for log streaming
- **Auto-Reconnect**: Automatic backend reconnection with exponential backoff strategy

## Prerequisites

Before installing Epifania, ensure the following dependencies are installed:

- **Python 3.8+**: Backend runtime environment
- **Node.js 18+**: Frontend build tooling and development server
- **ADB**: Android Debug Bridge must be installed and available in PATH
- **USB Debugging**: Enable USB debugging on target Android devices
- **Linux**: This tool is designed for Linux systems

## Installation

### Quick Setup (Recommended)

Use the automated setup script to create isolated virtual environments and install all dependencies:

```bash
git clone https://github.com/Neverlow512/epifania.git
cd epifania
./setup.sh
```

The setup script will:
1. Create a Python virtual environment in `backend/venv`
2. Install Python dependencies in isolation
3. Configure Node.js version (if nvm is available)
4. Install frontend dependencies in `frontend/node_modules`

### Manual Setup

If you prefer manual installation:

#### 1. Clone Repository

```bash
git clone https://github.com/Neverlow512/epifania.git
cd epifania
```

#### 2. Setup Backend (Python Virtual Environment)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
cd ..
```

#### 3. Setup Frontend (Node.js)

Optional: Use nvm for Node.js version management:
```bash
nvm install 20
nvm use 20
```

Install dependencies:
```bash
cd frontend
npm install
cd ..
```

### Running the Application

#### Option 1: Using the Unified Launcher (Recommended)

Execute the Python launcher from the project root:

```bash
python3 launcher.py
```

The launcher automatically:
- Uses the virtual environment
- Starts both backend and frontend services
- Monitors service health
- Handles graceful shutdown with Ctrl+C

#### Option 2: Using the Shell Script (Linux/macOS)

```bash
./start.sh
```

The script starts both services and provides log file paths for monitoring.

**Service URLs:**
- Backend API: http://127.0.0.1:8000
- Frontend Dashboard: http://127.0.0.1:5173

Access the dashboard in your browser at http://127.0.0.1:5173

Logs are written to categorized directories in `logs/` for monitoring and debugging.

### Manual Service Execution

Alternatively, run services independently:

**Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**Frontend:**
```bash
cd frontend
npm run dev
```

## API Endpoints

### Health & System Management

#### Health Check

```
GET /health
```

Returns the operational status of the backend service, ADB connection, and health manager status.

**Response:**
```json
{
  "status": "healthy",
  "adb_connected": true,
  "device_count": 1,
  "timestamp": "2024-11-23T10:30:00.000Z",
  "health_manager": {
    "is_healthy": true,
    "last_check": "2024-11-23T10:29:55.000Z",
    "failure_count": 0,
    "max_failures": 3,
    "running": true
  }
}
```

#### System Health Check

```
GET /api/system/health
```

Runs comprehensive health checks on all registered system components.

**Response:**
```json
{
  "overall_healthy": true,
  "checks": {
    "adb_connection": {
      "status": "healthy",
      "healthy": true
    }
  },
  "timestamp": "2024-11-23T10:30:00.000Z"
}
```

#### Restart ADB Server

```
POST /api/adb/restart
```

Restarts the ADB server daemon to resolve connection issues.

**Response:**
```json
{
  "success": true,
  "message": "ADB server restarted successfully"
}
```

### Device Management

#### List Devices

```
GET /api/devices
```

Enumerates all Android devices and emulators connected via ADB with comprehensive device information and Frida availability status.

**Response:**
```json
{
  "devices": [
    {
      "id": "emulator-5554",
      "name": "Google Pixel 3",
      "type": "emulator",
      "brand": "Google",
      "model": "Pixel 3",
      "android_version": "9",
      "sdk_version": "28",
      "architecture": "x86",
      "serial": "emulator-5554",
      "state": "online",
      "has_root": true,
      "frida_available": true,
      "frida_name": "Pixel 3"
    }
  ]
}
```

#### Get Device Details

```
GET /api/devices/{device_id}
```

Retrieves detailed information about a specific device, including Frida server status.

**Response:**
```json
{
  "id": "emulator-5554",
  "name": "Google Pixel 3",
  "type": "emulator",
  "brand": "Google",
  "model": "Pixel 3",
  "android_version": "9",
  "sdk_version": "28",
  "architecture": "x86",
  "serial": "emulator-5554",
  "state": "online",
  "has_root": true,
  "frida_available": true,
  "frida_server_version": "17.5.1",
  "frida_server_running": true
}
```

#### Connect to Device

```
POST /api/devices/{device_id}/connect
```

Verifies device connection and reachability via ADB.

**Response:**
```json
{
  "connected": true,
  "message": "Device is connected and reachable"
}
```

### Frida Management

#### Get Available Versions

```
GET /api/frida/versions
```

Fetches available Frida server versions from GitHub releases.

**Response:**
```json
{
  "versions": [
    {
      "version": "17.5.1",
      "name": "17.5.1",
      "published_at": "2024-11-20T10:30:00Z",
      "prerelease": false
    }
  ]
}
```

#### Get Cached Versions

```
GET /api/frida/cached
```

Lists locally cached Frida server binaries.

**Response:**
```json
{
  "cached": {
    "17.5.1": ["x86", "arm64"]
  }
}
```

#### Get Recommended Version

```
GET /api/devices/{device_id}/frida/recommended
```

Determines the optimal Frida version for a specific device based on architecture, SDK version, and cached binaries.

**Response:**
```json
{
  "version": "17.5.1",
  "name": "17.5.1",
  "architecture": "x86",
  "sdk_version": 28,
  "android_version": "9",
  "reason": "Latest stable version compatible with device",
  "cached": true
}
```

#### Install Frida Server

```
POST /api/devices/{device_id}/frida/install
```

Downloads, installs, and starts Frida server on the target device. Supports optional architecture parameter for manual architecture specification.

**Request Body:**
```json
{
  "version": "17.5.1",
  "architecture": "x86"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Frida server installed successfully",
  "started": true
}
```

#### Push Cached Server

```
POST /api/devices/{device_id}/frida/push
```

Pushes a previously cached Frida server binary to the device.

**Request Body:**
```json
{
  "version": "17.5.1",
  "architecture": "x86"
}
```

#### Start/Stop/Restart Frida Server

```
POST /api/devices/{device_id}/frida/start
POST /api/devices/{device_id}/frida/stop
POST /api/devices/{device_id}/frida/restart
```

Controls the Frida server process on the device.

**Response:**
```json
{
  "success": true,
  "message": "Frida server started successfully"
}
```

#### Discover Frida Servers

```
GET /api/devices/{device_id}/frida/discover
```

Scans the device for all Frida server binaries in common locations.

**Response:**
```json
{
  "servers": [
    {
      "path": "/data/local/tmp/frida-server",
      "permissions": "-rwxr-xr-x",
      "size": "45678901",
      "is_executable": true,
      "version": "17.5.1"
    }
  ]
}
```

#### Clean Frida Servers

```
POST /api/devices/{device_id}/frida/clean
```

Removes specified Frida server binaries from the device.

**Request Body:**
```json
{
  "paths": [
    "/data/local/tmp/frida-server-old",
    "/system/bin/frida-server"
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully removed 2 server(s)",
  "removed": [
    "/data/local/tmp/frida-server-old",
    "/system/bin/frida-server"
  ],
  "failed": []
}
```

#### Check Permissions

```
GET /api/devices/{device_id}/frida/permissions?path=/data/local/tmp/frida-server
```

Checks the permissions of a Frida server binary on the device.

**Response:**
```json
{
  "exists": true,
  "is_executable": true,
  "permissions": "-rwxr-xr-x",
  "path": "/data/local/tmp/frida-server"
}
```

#### Set Permissions

```
POST /api/devices/{device_id}/frida/permissions?path=/data/local/tmp/frida-server
```

Sets executable permissions (755) on a Frida server binary.

**Response:**
```json
{
  "success": true,
  "message": "Successfully set executable permissions for /data/local/tmp/frida-server",
  "permissions": "-rwxr-xr-x"
}
```

#### Test Frida Connection

```
GET /api/devices/{device_id}/frida/test-connection
```

Tests the Frida connection by attempting to connect and enumerate processes.

**Response:**
```json
{
  "connected": true,
  "message": "Frida connection successful",
  "details": {
    "device_name": "Google Pixel 3",
    "device_type": "usb",
    "process_count": 245
  }
}
```

### Process Management

#### List Processes

```
GET /api/devices/{device_id}/processes
```

Retrieves all running processes on the device with memory usage, state, and user information.

**Response:**
```json
{
  "processes": [
    {
      "pid": 1234,
      "name": "com.example.app",
      "user": "u0_a123",
      "cpu_percent": 0.0,
      "memory_kb": 45678,
      "memory_mb": 44.61,
      "memory_delta_mb": 0.5,
      "vsz_kb": 1234567,
      "state": "cached",
      "kernel_state": "sleeping",
      "ppid": 567,
      "command": "com.example.app",
      "is_kernel_thread": false,
      "android_managed": true
    }
  ],
  "count": 245,
  "stats": {
    "total": 245,
    "user": 89,
    "system": 156,
    "total_memory_mb": 1234.56
  },
  "changes": {
    "spawned": [],
    "killed": [],
    "changed": []
  }
}
```

**Process State Values:**
- Android-managed processes: `foreground`, `visible`, `service`, `bound`, `background`, `cached`, `persistent`, `receiver`
- System processes: `kernel` (kernel threads), `native` (system daemons), `zombie` (terminated but not cleaned up)

#### Get Process Details

```
GET /api/devices/{device_id}/processes/{pid}
```

Retrieves detailed information about a specific process including command line, status, threads, open files, and memory maps.

**Response:**
```json
{
  "pid": 1234,
  "cmdline": "com.example.app --flag value",
  "status": {
    "Name": "com.example.app",
    "State": "S (sleeping)",
    "Uid": "10123",
    "VmRSS": "45678 kB"
  },
  "threads": [
    {"tid": 1234},
    {"tid": 1235}
  ],
  "open_files": [
    {"fd": "0", "path": "/dev/null"},
    {"fd": "1", "path": "/data/data/com.example.app/files/log.txt"}
  ],
  "memory_maps": [
    {
      "address": "12c00000-12d00000",
      "perms": "r-xp",
      "offset": "00000000",
      "dev": "fd:00",
      "inode": "12345",
      "pathname": "/system/lib/libc.so"
    }
  ]
}
```

#### Kill Process

```
POST /api/devices/{device_id}/processes/{pid}/kill
```

Terminates a process on the device. Attempts root access if available.

**Query Parameters:**
- `signal` (optional): Signal number to send (default: 9 for SIGKILL)

**Response:**
```json
{
  "success": true,
  "message": "Process 1234 terminated successfully"
}
```

#### Get Process Metrics

```
GET /api/devices/{device_id}/processes/metrics
```

Retrieves historical metrics for processes on the device.

**Query Parameters:**
- `pid` (optional): Filter metrics for a specific process
- `duration` (optional): Number of data points to return (default: 60)

**Response:**
```json
{
  "device": "emulator-5554",
  "pid": 1234,
  "metrics": [
    {
      "timestamp": "2024-11-23T10:30:00.000Z",
      "cpu_percent": 5.2,
      "memory_mb": 44.61
    }
  ]
}
```

#### Get Process Churn

```
GET /api/devices/{device_id}/processes/churn
```

Retrieves process spawn/kill statistics over a time window.

**Query Parameters:**
- `window` (optional): Time window in seconds (default: 60)

**Response:**
```json
{
  "spawned_count": 5,
  "killed_count": 3,
  "net_change": 2,
  "recent_spawned": [
    {
      "pid": 1234,
      "name": "com.example.app",
      "time_ago": "5s"
    }
  ],
  "recent_killed": [
    {
      "pid": 5678,
      "name": "old.process",
      "time_ago": "12s"
    }
  ]
}
```

### System Monitoring

#### Get CPU Usage

```
GET /api/devices/{device_id}/system/cpu
```

Retrieves overall CPU usage and top CPU-consuming processes.

**Query Parameters:**
- `top_n` (optional): Number of top processes to return (default: 5)

**Response:**
```json
{
  "overall_percent": 45.2,
  "top_consumers": [
    {
      "pid": 1234,
      "name": "com.example.app",
      "cpu_percent": 15.3
    }
  ]
}
```

#### Get Memory Usage

```
GET /api/devices/{device_id}/system/memory
```

Retrieves system memory statistics and optionally per-process memory details.

**Query Parameters:**
- `pid` (optional): Process ID for detailed memory information

**Response:**
```json
{
  "total_mb": 2048.0,
  "used_mb": 1536.0,
  "free_mb": 512.0,
  "available_mb": 768.0,
  "buffers_mb": 128.0,
  "cached_mb": 256.0,
  "focused_process": {
    "pid": 1234,
    "rss_mb": 45.6,
    "vsz_mb": 123.4,
    "peak_mb": 50.2
  }
}
```

#### Get Storage Usage

```
GET /api/devices/{device_id}/system/storage
```

Retrieves storage usage for a specific partition.

**Query Parameters:**
- `partition` (optional): Partition path (default: /data)

**Response:**
```json
{
  "partition": "/data",
  "total_gb": 32.0,
  "used_gb": 18.5,
  "free_gb": 13.5,
  "percent_used": 57.8
}
```

#### Get All Storage Partitions

```
GET /api/devices/{device_id}/system/storage/all
```

Retrieves usage statistics for all mounted partitions.

**Response:**
```json
{
  "partitions": [
    {
      "partition": "/data",
      "total_gb": 32.0,
      "used_gb": 18.5,
      "free_gb": 13.5,
      "percent_used": 57.8
    },
    {
      "partition": "/system",
      "total_gb": 4.0,
      "used_gb": 3.2,
      "free_gb": 0.8,
      "percent_used": 80.0
    }
  ]
}
```

#### Get Network Statistics

```
GET /api/devices/{device_id}/system/network
```

Retrieves network throughput and optionally per-process connection details.

**Query Parameters:**
- `pid` (optional): Process ID for detailed connection information

**Response:**
```json
{
  "throughput": {
    "bytes_sent_per_sec": 1024,
    "bytes_received_per_sec": 2048
  },
  "recent_endpoints": [
    {
      "remote_ip": "192.168.1.100",
      "remote_port": 443,
      "count": 5
    }
  ],
  "focused_process": {
    "pid": 1234,
    "connections": [
      {
        "local_address": "192.168.1.50:12345",
        "remote_address": "192.168.1.100:443",
        "state": "ESTABLISHED"
      }
    ]
  }
}
```

#### Get All Network Connections

```
GET /api/devices/{device_id}/system/network/connections
```

Retrieves all TCP connections on the device.

**Response:**
```json
{
  "connections": [
    {
      "local_address": "192.168.1.50:12345",
      "remote_address": "192.168.1.100:443",
      "state": "ESTABLISHED",
      "pid": 1234
    }
  ]
}
```

### Diagnostics

#### Run ADB Diagnostics

```
GET /api/devices/{device_id}/diagnostics/adb
```

Runs comprehensive ADB diagnostics including connectivity, root access, permissions, SELinux status, storage, and ADB version checks.

**Response:**
```json
{
  "device_id": "emulator-5554",
  "timestamp": "2024-11-23T10:30:00.000Z",
  "tests": [
    {
      "name": "Shell Connectivity",
      "description": "Tests basic ADB shell command execution",
      "status": "pass",
      "message": "Shell commands execute successfully",
      "details": {
        "response": "connectivity_test"
      }
    },
    {
      "name": "Root Access",
      "description": "Checks if device has root access available",
      "status": "pass",
      "message": "Root access is available",
      "details": {
        "uid": "0 (root)"
      }
    },
    {
      "name": "Write Permissions",
      "description": "Tests write access to /data/local/tmp directory",
      "status": "pass",
      "message": "Write permissions to /data/local/tmp are available",
      "details": {
        "path": "/data/local/tmp"
      }
    },
    {
      "name": "SELinux Status",
      "description": "Checks SELinux enforcement mode",
      "status": "pass",
      "message": "SELinux is permissive (optimal for Frida)",
      "details": {
        "mode": "Permissive"
      }
    },
    {
      "name": "Storage Space",
      "description": "Checks available storage in /data partition",
      "status": "pass",
      "message": "Sufficient storage: 2.5G available",
      "details": {
        "available": "2.5G",
        "usage": "45%"
      }
    },
    {
      "name": "ADB Version",
      "description": "Checks ADB daemon version on device",
      "status": "pass",
      "message": "ADB server version: 41",
      "details": {
        "server_version": 41
      }
    }
  ],
  "summary": {
    "passed": 6,
    "failed": 0,
    "total": 6,
    "overall_status": "pass"
  }
}
```

### Log Streaming

#### Get Historical Logs

```
GET /api/devices/{device_id}/logs/{log_type}
```

Retrieves historical logs for a specific log type (logcat, frida_install, frida_server, adb_operations).

**Response:**
```json
{
  "logs": [
    {
      "timestamp": "2024-11-23T10:30:00.000Z",
      "level": "info",
      "message": "Frida server started successfully"
    }
  ]
}
```

#### WebSocket Log Streaming

```
WS /ws/devices/{device_id}/logs
```

Real-time bidirectional WebSocket connection for log streaming.

**Client Messages:**
```json
{"action": "start", "log_type": "logcat"}
{"action": "stop", "log_type": "logcat"}
{"action": "clear", "log_type": "logcat"}
```

**Server Messages:**
```json
{
  "type": "logcat",
  "level": "info",
  "message": "Log message content",
  "timestamp": "2024-11-23T10:30:00.000Z"
}
```

## Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Backend Framework | FastAPI | 0.122.0 | RESTful API server |
| Backend Runtime | Python | 3.8+ | Orchestration and business logic |
| ASGI Server | Uvicorn | 0.38.0 | High-performance async server |
| Instrumentation | Frida | 17.5.1 | Dynamic code injection and hooking |
| Device Management | Native ADB | System | Android device communication via subprocess |
| Data Validation | Pydantic | 2.12.5 | Request/response validation |
| WebSocket | websockets | 13.1 | Real-time log streaming (pinned version) |
| Process Management | psutil | 7.1.3 | System and process monitoring |
| Frontend Framework | Vue 3 | 3.5.25 | Reactive user interface |
| Routing | Vue Router | 4.6.3 | Client-side navigation with query params |
| Build Tool | Vite | 7.2.4 | Development server and bundler |
| Styling | Tailwind CSS | 4.1.17 | Utility-first CSS framework |
| UI Components | DaisyUI | 5.5.5 | Component library |
| HTTP Client | Axios | 1.13.2 | API communication |

## Features

### Tab Navigation Structure

The device details interface is organized into tabbed sections for clear separation of functionality:

**Device Tab (Overview):**
- Compact header showing device name, type badge, connection status, SDK version, and root status
- Complete Frida server lifecycle management (install, start, stop, restart)
- Automatic and manual Frida version installation with architecture selection
- Frida server discovery and cleanup tools
- Permission management for Frida binaries
- Comprehensive ADB diagnostics with detailed test results
- Real-time log streaming (logcat, Frida operations, ADB operations)
- Modal-based detailed information views for complex operations

**Processes Tab:**
- Real-time process list with auto-refresh (configurable 2-second interval)
- Process statistics showing total, user, and system process counts with memory usage
- System resource monitoring dashboard with live metrics:
  - Overall CPU usage percentage with top CPU-consuming processes
  - System memory usage (total, used, free, available, buffers, cached)
  - Storage partition monitoring with usage statistics for all mounted partitions
  - Network throughput tracking (bytes sent/received per second)
  - Recent network endpoints with connection frequency
- Process churn tracking showing spawned and killed processes over configurable time windows
- Search functionality across PID, name, user, and command
- Filter by process type (all, user, system)
- Kernel thread filtering with show/hide toggle (hidden by default)
- Sort by PID, name, memory usage, or user (defaults to memory for identifying resource-heavy processes)
- Paginated process table with 50 processes per page
- Process inspection with detailed information:
  - Command line arguments
  - Process status (/proc/pid/status)
  - Thread listing
  - Open file descriptors
  - Memory maps (first 50 entries)
  - Per-process memory breakdown (RSS, VSZ, peak memory)
  - Per-process TCP connections with local/remote addresses and states
- Process termination with confirmation dialog
- Android process state indicators via ActivityManager:
  - foreground (app on screen), visible (bound to foreground), service (foreground service)
  - cached (can be killed), persistent (system-critical), background, bound, receiver
  - Fallback states for non-Android processes: kernel, native, zombie
- State Dictionary modal with detailed explanations accessible from table header
- Memory delta tracking with visual indicators showing changes between refreshes
- Educational help modals explaining CPU metrics, memory metrics, and process list interpretation
- Change detection for spawned, killed, and resource-intensive processes

**Placeholder Tabs (In Development):**
- **Packages**: Application catalog and lifecycle control
- **Files**: Device filesystem browser
- **Workshop**: Script injection and active analysis workspace

**Navigation Features:**
- Query parameter routing for deep linking (e.g., `?tab=processes`)
- Reusable tab component with keyboard navigation
- Smooth tab switching with state preservation
- URL synchronization for bookmarking specific views

### Device Management

- **Automatic Device Detection**: Scans and enumerates all connected Android devices and emulators via ADB
- **Device Information**: Displays comprehensive device specifications including brand, model, Android version, SDK level, architecture, and root status
- **Connection Monitoring**: Real-time tracking of device connection states with auto-refresh
- **Device Persistence**: Maintains device list with disconnection tracking across scans

### Frida Integration

- **Version Management**: Browse and select from available Frida server versions from GitHub releases
- **Automated Installation**: One-click download, installation, and deployment of Frida server to devices
- **Recommended Versions**: Automatic detection of optimal Frida version based on device specifications
- **Server Lifecycle Control**: Start, stop, and restart Frida server processes on target devices
- **Cached Binary Management**: Store and reuse downloaded Frida server binaries for faster deployment
- **Architecture Detection**: Automatic mapping of Android ABIs to Frida architectures
- **Architecture Selection**: Manual architecture selection (arm, arm64, x86, x86_64) for custom downloads
- **Direct GitHub Integration**: Fetch latest 10 Frida releases directly from GitHub API without backend caching
- **Status Monitoring**: Real-time display of Frida server version and running status
- **Server Discovery**: Scan devices for all Frida server binaries in common locations
- **Permission Management**: Check and set executable permissions on Frida binaries
- **Connection Testing**: Validate Frida connectivity by enumerating processes
- **Cleanup Tools**: Remove old or duplicate Frida server binaries from devices

### Process Monitoring

- **Real-time Process List**: Enumerate all running processes via ADB with automatic refresh
- **Process Statistics**: Display total, user, and system process counts with aggregate memory usage
- **System Resource Monitoring**: Comprehensive device telemetry including:
  - **CPU Monitoring**: Overall CPU usage percentage with top N CPU-consuming processes (uses `top` with `ps` fallback)
  - **Memory Monitoring**: System RAM metrics (total, used, free, available, buffers, cached) with per-process memory details
  - **Storage Monitoring**: Partition usage statistics (total, used, free, percent used) for all mounted partitions
  - **Network Monitoring**: Real-time throughput tracking (bytes sent/received per second), recent network endpoints, and per-process TCP connections
- **Android Process State Classification**: Accurate process states via `dumpsys activity processes`:
  - Maps Android's `curProcState` values (0-20) to user-friendly labels
  - States include: foreground, visible, service, bound, background, cached, persistent, receiver
  - Fallback classification for non-Android processes: kernel threads, native daemons, zombies
  - Kernel thread detection for processes running in kernel space (names in [brackets])
- **Process Churn Tracking**: Monitor process spawn/kill events with configurable time windows and historical event lists
- **Search and Filter**: Find processes by PID, name, user, or command with type filtering (all/user/system)
- **Kernel Thread Filtering**: Toggle to show/hide kernel threads (hidden by default for cleaner view)
- **Sorting Options**: Sort by PID, name, memory usage, or user
- **Pagination**: Navigate large process lists with configurable page size
- **Process Inspection**: View detailed process information including:
  - Full command line arguments
  - Process status from /proc filesystem
  - Thread enumeration
  - Open file descriptors
  - Memory maps (limited to first 50 entries)
  - Detailed per-process memory breakdown (RSS, VSZ, peak, high-water mark)
  - Active TCP connections with local/remote addresses and connection states
- **Process Termination**: Kill processes with confirmation dialog (attempts root access if available)
- **State Dictionary**: Interactive help modal explaining all process states with interpretation guidance
- **Memory Delta Tracking**: Visual indicators showing memory changes between refreshes (+red for increase, -green for decrease)
- **Educational Help Modals**: Detailed explanations for CPU metrics, memory metrics (RSS vs system memory), and process list interpretation
- **Change Detection**: Track spawned, killed, and resource-intensive processes between refreshes
- **Metrics Storage**: Historical process count and system memory data with configurable retention (120 data points); memory history uses actual system RAM (Total - Available) instead of summed RSS
- **Auto-Refresh**: Configurable refresh interval (default 2 seconds) with toggle control

### Health Monitoring & Diagnostics

- **Health Manager**: Periodic health checks with configurable intervals
- **Process Management**: Automatic cleanup of stale processes and PID tracking
- **System Health API**: Comprehensive health status reporting
- **ADB Diagnostics**: Full diagnostic suite including:
  - Shell connectivity tests
  - Root access verification
  - Write permission checks
  - SELinux status monitoring
  - Storage space analysis
  - ADB version checking
- **Failure Tracking**: Consecutive failure counting with configurable thresholds

### Real-time Logging

- **WebSocket Streaming**: Bidirectional real-time log streaming with automatic reconnection
- **Multiple Log Types**:
  - **Logcat**: Android system logs (manual-start for performance, filtered for relevance)
  - **Frida Installation**: Installation process logs (auto-start, event-driven)
  - **Frida Server**: Server output and status logs (auto-start, continuous streaming from `/data/local/tmp/frida-server.log`)
  - **ADB Operations**: All ADB command logs with timestamps (auto-start, event-driven)
- **Auto-Start Behavior**: 
  - Frida Installation, Frida Server, and ADB Operations logs auto-start and auto-expand on page load
  - Logcat requires manual start to prevent overwhelming output
  - Auto-started logs can be paused by user at any time
- **Smart Optimization**:
  - Backend version check caching (30-second TTL) to reduce redundant ADB calls
  - Optimized polling intervals: device details every 15 seconds, Frida connection tests every 30 seconds
  - Reduced `pidof` and `--version` queries to minimize ADB overhead
- **Buffer Management**: Configurable log buffer sizes with deduplication and thread-safe access
- **Historical Logs**: Access to buffered historical logs on connection
- **Log Controls**: Clear, scroll-to-bottom, and stream start/stop controls per log type

### User Interface

- **Dashboard View**: Grid layout of device cards with quick actions
- **Tabbed Device Interface**: Organized sections for device management, processes, packages, files, and workshop
- **Device Tab**: Complete Frida server lifecycle controls with diagnostics and log streaming
- **Compact Layout**: Optimized information density with card-compact styling
- **Modal Dialogs**: Detailed information views for Frida installation, cached server push, and diagnostics
- **Tab Navigation**: Reusable component with keyboard support and URL query parameter routing
- **Deep Linking**: Bookmarkable URLs for specific tabs (e.g., `?tab=processes`)
- **Responsive Design**: Adapts to different screen sizes and resolutions
- **Visual Feedback**: Loading states, status badges, and interactive elements
- **Dark Theme**: Security-focused interface with purple accent color (#7100d0)
- **Navigation**: Client-side routing with page transitions and state preservation
- **Toast Notifications**: Notification system with success, error, warning, and info types
- **Auto-Reconnect**: Automatic backend reconnection with exponential backoff strategy
- **Custom Frida Download**: Download specific Frida versions with manual architecture selection

### Backend Connection Management

- **Auto-Reconnect**: Automatic reconnection with exponential backoff (1s, 2s, 5s, 10s, 30s)
- **Connection Monitoring**: Periodic health checks every 10 seconds
- **Failure Tracking**: Tracks consecutive failures with configurable retry limits
- **Status Indicators**: Real-time connection status display in UI
- **Silent Checks**: Background connection verification without user interruption

## Project Structure

```
epifania/
├── backend/                      # Python FastAPI backend
│   ├── core/                     # Core functionality modules
│   │   ├── __init__.py
│   │   ├── adb_manager.py        # ADB client wrapper
│   │   ├── device_manager.py     # Device enumeration
│   │   ├── installer.py          # Frida server management
│   │   ├── log_streamer.py       # Real-time log streaming
│   │   ├── logger.py             # Centralized logging
│   │   ├── log_paths.py          # Log directory configuration
│   │   └── diagnostics.py        # ADB diagnostics system
│   ├── device/                   # Device-specific feature modules
│   │   ├── __init__.py
│   │   └── processes_tab/        # Process monitoring module
│   │       ├── __init__.py
│   │       ├── routes.py         # Process API endpoints
│   │       └── monitoring/       # Process monitoring logic
│   │           ├── __init__.py
│   │           ├── dprocess_monitor.py  # Process monitor class
│   │           ├── cpu_monitor.py       # CPU usage monitoring
│   │           ├── memory_monitor.py    # Memory usage monitoring
│   │           ├── storage_monitor.py   # Storage monitoring
│   │           └── network_monitor.py   # Network monitoring
│   ├── monitoring/               # Health and process monitoring
│   │   ├── __init__.py
│   │   ├── health_manager.py     # Health check system
│   │   └── process_manager.py    # Process cleanup and PID tracking
│   ├── frida_mgmt/               # Frida server management
│   │   ├── __init__.py
│   │   └── manage/               # Frida management modules
│   │       ├── discovery.py      # Server discovery
│   │       ├── permissions.py    # Permission management
│   │       └── server.py         # Server lifecycle control
│   ├── frida_servers/            # Cached Frida server binaries
│   │   └── {version}/            # Version-specific directories
│   │       └── {arch}/           # Architecture-specific binaries
│   ├── routers/                  # API route modules
│   ├── utils/                    # Utility modules
│   │   └── frida_debug.py        # Frida debugging utilities
│   ├── venv/                     # Python virtual environment
│   ├── main.py                   # FastAPI application entry
│   └── requirements.txt          # Python dependencies
│
├── frontend/                     # Vue 3 frontend
│   ├── src/
│   │   ├── components/           # Reusable Vue components
│   │   │   ├── DeviceCard.vue    # Device card component
│   │   │   ├── TabNavigation.vue # Tab navigation component
│   │   │   ├── LogViewer.vue     # Log streaming component
│   │   │   └── ToastNotification.vue  # Toast notification system
│   │   ├── composables/          # Vue composables
│   │   │   ├── useApiConnection.js    # Backend connection management
│   │   │   └── useToast.js            # Toast notification composable
│   │   ├── router/               # Vue Router configuration
│   │   │   └── index.js          # Route definitions with query params
│   │   ├── views/                # Page components
│   │   │   ├── Dashboard.vue     # Device list view
│   │   │   ├── DeviceDetails.vue # Tab container with routing
│   │   │   └── device/           # Device tab modules (feature-based)
│   │   │       ├── overview/     # Device overview tab
│   │   │       │   ├── DeviceTab.vue
│   │   │       │   ├── components/
│   │   │       │   └── composables/
│   │   │       ├── processes/    # Process monitoring tab
│   │   │       │   ├── ProcessesTab.vue
│   │   │       │   ├── components/
│   │   │       │   │   ├── ProcessControlBar.vue    # Search, filters, kernel toggle, Details modal
│   │   │       │   │   ├── ProcessDetailsModal.vue
│   │   │       │   │   ├── ProcessKillModal.vue
│   │   │       │   │   ├── ProcessStatsBar.vue      # Runtime overview with CPU/Memory help modals
│   │   │       │   │   └── ProcessTable.vue         # Process list with State Dictionary modal
│   │   │       │   └── composables/
│   │   │       │       ├── useProcessActions.js
│   │   │       │       ├── useProcesses.js
│   │   │       │       ├── useProcessFilters.js     # Includes kernel thread filtering
│   │   │       │       ├── useProcessChurn.js
│   │   │       │       └── useSystemMetrics.js
│   │   │       ├── packages/     # Package management (placeholder)
│   │   │       │   └── PackagesTab.vue
│   │   │       ├── files/        # File browser (placeholder)
│   │   │       │   └── FilesTab.vue
│   │   │       └── workshop/     # Analysis workspace (placeholder)
│   │   │           └── WorkshopTab.vue
│   │   ├── App.vue               # Root component
│   │   ├── main.js               # Application entry
│   │   └── style.css             # Global styles
│   ├── node_modules/             # Node.js dependencies
│   ├── index.html                # HTML entry point
│   ├── package.json              # Node.js dependencies
│   ├── vite.config.js            # Vite configuration
│   └── postcss.config.js         # PostCSS configuration
│
├── logs/                         # Centralized logging system
│   ├── application/              # Backend application logs
│   │   ├── central.log
│   │   ├── backend.log
│   │   ├── errors.log
│   │   └── backend.pid
│   ├── devices/                  # Device operation logs
│   │   └── device.log
│   ├── diagnostics/              # Diagnostic logs
│   │   └── frida/
│   │       └── activation/       # Frida server startup diagnostics
│   └── services/                 # Service process logs
│       ├── uvicorn.log
│       └── vite.log
├── tests/                        # Test suite
│   ├── test_logging_system.py   # Logging system validation
│   └── test_adb_migration.py    # ADB functionality tests
├── history_docs/                 # Project documentation
│   └── project_state.md          # Historical project state documentation
├── launcher.py                   # Unified application launcher
├── start.sh                      # Linux/macOS startup script
├── setup.sh                      # Linux/macOS setup script
├── README.md                     # Project documentation
├── ARCHITECTURE.md               # Architecture principles and guidelines
├── DEVELOPMENT_RULES.md          # Development guidelines
├── expansion_plan.md             # Feature expansion roadmap
├── new_backend_feats.md          # Latest backend monitoring features
└── LICENSE                       # License information
```

## Development

### Backend Development

The backend follows a modular architecture with clear separation of concerns:

- `backend/main.py`: FastAPI application entry point with core API endpoints and WebSocket handlers
- `backend/core/adb_manager.py`: ADB client wrapper for device communication and shell command execution
- `backend/core/device_manager.py`: Device enumeration combining ADB and Frida data sources
- `backend/core/installer.py`: Complete Frida server installation, version management, and lifecycle control with intelligent caching
- `backend/core/log_streamer.py`: Real-time log streaming with WebSocket support, buffer management, and separate handling for active streams (logcat, frida_server) vs event-driven logs (adb_operations, frida_install)
- `backend/core/logger.py`: Centralized logging with categorized output and rotating file handlers
- `backend/core/diagnostics.py`: Comprehensive ADB diagnostics with multiple test suites
- `backend/device/`: Feature modules for device-specific functionality
  - `backend/device/processes_tab/routes.py`: Process management API endpoints (list, details, kill, metrics, churn, system monitoring)
  - `backend/device/processes_tab/monitoring/dprocess_monitor.py`: Process monitoring class with ADB-based process enumeration, Android state classification via dumpsys, kernel thread detection, memory delta tracking, and churn tracking
  - `backend/device/processes_tab/monitoring/cpu_monitor.py`: CPU usage monitoring with `top` command parsing (with `ps` fallback) and top consumer tracking
  - `backend/device/processes_tab/monitoring/memory_monitor.py`: System and per-process memory monitoring
  - `backend/device/processes_tab/monitoring/storage_monitor.py`: Storage partition monitoring and usage statistics
  - `backend/device/processes_tab/monitoring/network_monitor.py`: Network throughput, connection tracking, and per-process TCP monitoring
- `backend/frida_mgmt/manage/`: Frida server management modules (discovery, permissions, server lifecycle)
- `backend/monitoring/health_manager.py`: Health monitoring system with periodic checks
- `backend/monitoring/process_manager.py`: Process cleanup and PID file management
- `backend/routers/`: API route handlers for modular endpoint organization

### Logging Structure

The application uses a centralized logging system configured via `backend/core/log_paths.py`. All log directories are created automatically on startup via `ensure_log_directories()`.

**Log Directory Structure:**

- `logs/application/` - Backend application logs
  - `central.log` - Aggregated log of all important events
  - `backend.log` - General backend operations
  - `errors.log` - Error-level logs only
  - `backend.pid` - Process ID file for backend tracking
- `logs/devices/` - Device management and ADB operations
  - `device.log` - Device enumeration and communication logs
- `logs/diagnostics/` - Diagnostic and troubleshooting logs
  - `frida/activation/` - Frida server startup diagnostics (includes failure logs with detailed device info, permissions, and ADB operations)
- `logs/services/` - External service logs
  - `uvicorn.log` - FastAPI server output
  - `vite.log` - Vite dev server output

**Key Features:**
- Centralized path configuration prevents inconsistencies
- Rotating file handlers prevent unbounded log growth
- Frida server failures automatically generate detailed diagnostic logs in `diagnostics/frida/activation/`
- All components reference the same log path constants

### Frontend Development

The frontend uses Vue 3 Composition API with a component-based architecture:

**Application Structure:**
- `frontend/src/App.vue`: Root component with navigation header, global state, and custom Frida download widget
- `frontend/src/main.js`: Application entry point with router integration
- `frontend/src/router/index.js`: Vue Router configuration for multi-page navigation with query parameter support
- `frontend/src/style.css`: Global styles and theme configuration

**Views:**
- `frontend/src/views/Dashboard.vue`: Device list with auto-refresh and scanning capabilities
- `frontend/src/views/DeviceDetails.vue`: Tab container with compact device header and tab navigation
- `frontend/src/views/device/`: Feature-based tab modules with components and composables
  - `overview/DeviceTab.vue`: Device management interface with Frida controls, diagnostics, and log streaming
  - `processes/ProcessesTab.vue`: Process monitoring with real-time updates, system metrics, search, filter, and inspection
  - `packages/PackagesTab.vue`: Placeholder for package management (in development)
  - `files/FilesTab.vue`: Placeholder for file browser (in development)
  - `workshop/WorkshopTab.vue`: Placeholder for analysis workspace (in development)

**Components:**
- `frontend/src/components/DeviceCard.vue`: Reusable device card with status indicators and actions
- `frontend/src/components/TabNavigation.vue`: Reusable tab bar with keyboard navigation and active state styling
- `frontend/src/components/LogViewer.vue`: Compact real-time log streaming with WebSocket integration, auto-start capabilities, and reduced height for better screen utilization
- `frontend/src/components/ToastNotification.vue`: Toast notification display system

**Composables:**
- `frontend/src/composables/useApiConnection.js`: Backend connection management with auto-reconnect
- `frontend/src/composables/useToast.js`: Toast notification state management
- `frontend/src/views/device/processes/composables/useProcesses.js`: Process fetching with auto-refresh and memory history tracking
- `frontend/src/views/device/processes/composables/useProcessFilters.js`: Search, filter, sort, pagination, and kernel thread filtering logic
- `frontend/src/views/device/processes/composables/useProcessActions.js`: Process inspection and termination actions
- `frontend/src/views/device/processes/composables/useProcessChurn.js`: Process spawn/kill event tracking
- `frontend/src/views/device/processes/composables/useSystemMetrics.js`: System resource monitoring (CPU, memory, storage, network)

**Process Tab Components:**
- `ProcessControlBar.vue`: Search, filter, sort controls with kernel thread toggle and Details help modal
- `ProcessStatsBar.vue`: Runtime overview with CPU/Memory/Storage/Network widgets and educational help modals
- `ProcessTable.vue`: Process list with State Dictionary modal and memory delta indicators
- `ProcessDetailsModal.vue`: Detailed process inspection view
- `ProcessKillModal.vue`: Process termination confirmation dialog

**Technical Implementation:**
- Vue 3 Composition API for reactive state management
- Feature-based directory structure: Each tab has its own directory with components and composables
- Component-based architecture with clear separation of concerns
- WebSocket integration for real-time log streaming with connection state tracking
- Automatic reconnection with exponential backoff for backend connectivity
- Client-side routing with Vue Router and query parameter support for deep linking
- Dynamic component rendering for tab content
- Tailwind CSS with DaisyUI components for consistent styling
- Smart auto-streaming: ADB Operations, Frida Install, and Frida Server logs auto-start on page load
- Manual logcat activation to prevent performance impact from verbose system logs
- Optimized polling intervals: 15s for device details, 30s for Frida connection tests, 2s for process list
- Direct GitHub API integration: Fetches latest 10 Frida releases client-side
- Modal-based detail views: Comprehensive information accessible via modals including State Dictionary, CPU explanation, and Memory explanation
- Reusable tab navigation component with keyboard accessibility
- Composable-based state management with separation of data fetching, filtering, and actions
- System metrics integration with real-time CPU, memory, storage, and network monitoring
- Process churn visualization with spawn/kill event tracking
- Android process state integration via ActivityManager for accurate state classification

### Dependency Management

#### Python Dependencies

All Python dependencies are isolated in `backend/venv/`. To update:

```bash
cd backend
source venv/bin/activate
pip install --upgrade <package-name>
pip freeze > requirements.txt
deactivate
```

To update all packages:
```bash
pip list --outdated
pip install --upgrade -r requirements.txt
pip freeze > requirements.txt
```

#### Node.js Dependencies

All Node.js dependencies are isolated in `frontend/node_modules/`. To update:

```bash
cd frontend
npm update <package-name>
```

To update all packages to latest versions:
```bash
npm install -g npm-check-updates
ncu -u
npm install
```

### Running Services Independently

Backend only:
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Frontend only:
```bash
cd frontend
npm run dev
```

### Testing

The project includes test suites for validating core systems.

**Run Logging System Tests:**
```bash
python3 tests/test_logging_system.py
```

This test validates:
- Log path configuration and directory creation
- Logger initialization and file writes
- FridaDebugLogger diagnostic file generation
- Log file structure and organization
- Migration from old log directory structure

**Run ADB Migration Tests:**
```bash
python3 tests/test_adb_migration.py
```

This test validates:
- ADB manager functionality
- Device enumeration
- Command execution and error handling

The test suites provide comprehensive validation that all core components function correctly.

## Troubleshooting

### Backend Issues

**ADB Not Connected:**
- Ensure ADB is installed and available in PATH
- Check that ADB server is running: `adb devices`
- Verify USB debugging is enabled on target devices
- Try restarting ADB via the UI or: `adb kill-server && adb start-server`

**Frida Installation Fails:**
- Select the correct architecture for your device before choosing a version
- Verify device has sufficient storage space
- Check that device has root access (for system-level installation)
- Ensure selected architecture matches device architecture
- Try manually pushing the binary via ADB
- Use the diagnostics tool to identify permission issues

**WebSocket Connection Fails:**
- Check that backend is running on port 8000
- Verify no firewall is blocking WebSocket connections
- Check browser console for connection errors
- Backend will auto-reconnect with exponential backoff

**Health Checks Failing:**
- Check logs in `logs/application/` directory
- Verify ADB server is running
- Ensure no port conflicts on 8000

### Frontend Issues

**Device List Empty:**
- Click "Scan Devices" to trigger device enumeration
- Verify backend is running and accessible
- Check browser console for API errors
- Use the ADB restart button if connection is lost

**Processes Tab Not Loading:**
- Verify device is connected and online
- Check that backend process monitoring endpoints are accessible
- Ensure device has sufficient resources to handle ADB queries
- Try disabling auto-refresh temporarily if experiencing performance issues

**System Metrics Not Updating:**
- Verify device has proper root access for detailed metrics
- Check network tab in browser developer tools for failed API requests
- Ensure device is not in deep sleep or power saving mode

**Logs Not Streaming:**
- Most debug logs (ADB Operations, Frida Install, Frida Server) auto-start on page load
- Logcat requires manual start via the play button to prevent overwhelming output
- Verify WebSocket connection is established (green indicator)
- Check that device is still connected
- Ensure logs haven't been manually paused via the pause button
- Check browser console for WebSocket errors
- Historical logs are sent immediately on connection, real-time logs follow

**Page Not Loading:**
- Clear browser cache and reload
- Check that frontend dev server is running on port 5173
- Verify no port conflicts with other applications
- Check if backend is accessible (connection indicator in header)

**Backend Connection Lost:**
- The UI will automatically attempt to reconnect with exponential backoff
- Check that backend service is running
- Verify no firewall blocking localhost:8000
- Toast notifications will inform you of connection status

### Diagnostics

**Using the Built-in Diagnostics:**
- Device details page includes integrated diagnostics in Connection Status widget
- Inline diagnostic summary shows passed/total test count
- Click "Run" button to execute comprehensive ADB diagnostic tests
- Click "Details" button to open modal with full test results
- Review individual test results with expandable details
- Follow recommendations provided in test details
- Tests include shell connectivity, root access, permissions, SELinux, storage, and ADB version checks

## Security Considerations

### Local-Only Tool
- Designed exclusively for localhost operation
- Not intended for remote access or production deployment
- No authentication required (acceptable for local development tool)

### Network Security
- CORS restricted to localhost origins (127.0.0.1:5173, localhost:5173)
- WebSocket connections limited to localhost
- All communication over unencrypted HTTP (acceptable for local-only use)

### Input Validation
- API endpoints validate request parameters
- Error messages sanitized to prevent information disclosure
- Device serial numbers validated before ADB operations

### Dependency Management
- Regular security updates recommended for all dependencies
- Python virtual environment isolation prevents system-wide conflicts
- Node.js dependencies isolated in project directory

### Best Practices
- Only connect trusted Android devices
- Review Frida scripts before injection (when feature is implemented)
- Monitor logs for unexpected ADB operations
- Keep ADB and Frida versions up to date
- Use diagnostics tool to verify device security settings

## License

This project is intended for security research and educational purposes.
