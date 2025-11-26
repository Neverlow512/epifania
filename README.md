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
- ✅ Device detail view with comprehensive management interface
- ✅ Frida server start/stop/restart controls
- ✅ Cached Frida server management and deployment
- ✅ Auto-refresh device list with connection state tracking
- ✅ Vue Router integration with multi-page navigation
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

**Planned Features:**
- 🔄 Process enumeration and management
- 🔄 Application listing and package management
- 🔄 Script injection interface with code editor
- 🔄 Memory inspection tools
- 🔄 Network traffic interception

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

Execute the startup script from the project root:

```bash
./start.sh
```

The script automatically uses the virtual environment and starts both services:

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
| Backend Framework | FastAPI | 0.121.3 | RESTful API server |
| Backend Runtime | Python | 3.8+ | Orchestration and business logic |
| ASGI Server | Uvicorn | 0.38.0 | High-performance async server |
| Instrumentation | Frida | 17.5.1 | Dynamic code injection and hooking |
| Device Management | Native ADB | System | Android device communication via subprocess |
| Data Validation | Pydantic | 2.12.4 | Request/response validation |
| WebSocket | websockets | 13.1 | Real-time log streaming |
| Process Management | psutil | 6.1.0 | System and process monitoring |
| Frontend Framework | Vue 3 | 3.5.24 | Reactive user interface |
| Routing | Vue Router | 4.6.3 | Client-side navigation |
| Build Tool | Vite | 7.2.4 | Development server and bundler |
| Styling | Tailwind CSS | 4.1.17 | Utility-first CSS framework |
| UI Components | DaisyUI | 5.5.5 | Component library |
| HTTP Client | Axios | 1.13.2 | API communication |

## Features

### UI Optimization (fix/solve-ui-size branch)

This branch introduces significant UI improvements focused on information density and usability:

**Layout Improvements:**
- Compact card styling throughout the interface for better space utilization
- Reduced log viewer height (from 64 to 48 units) allowing more content on screen
- Consolidated device detail page layout with 4-column grid for summary widgets
- Integrated diagnostics into connection status widget with inline controls
- Combined Install and Push operations in unified compact widget
- Smaller typography and padding adjustments for denser information display

**Architecture-First Workflow:**
- Architecture selection required before version download
- Manual architecture picker (arm, arm64, x86, x86_64) for custom downloads
- Version dropdown disabled until architecture selected
- Direct GitHub API integration fetches latest 10 releases client-side
- Removes backend `/api/frida/versions` dependency for custom downloads

**Modal-Based Details:**
- Install Frida (Auto) details modal showing download configuration, URLs, and paths
- Push Cached Server details modal with version and architecture info
- Frida Controls details modal explaining server management
- ADB Diagnostics details modal with comprehensive test results and expandable details
- Keeps main interface clean while providing access to detailed information

**Information Density:**
- Compact status indicators with inline metrics
- Collapsible sections for detailed information
- Reduced vertical spacing throughout
- Smaller buttons and controls
- Consolidated action groups

**Functional Changes:**
- Architecture parameter passes to backend installation endpoint
- Client-side Frida version fetching eliminates backend API calls
- Real-time version loading on architecture selection
- Enhanced validation flow requiring architecture before download

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
- **Device Details View**: Comprehensive management interface for individual devices
- **Compact Layout**: Optimized information density with card-compact styling
- **Modal Dialogs**: Detailed information views for Frida installation, cached server push, and diagnostics
- **Integrated Diagnostics**: ADB diagnostics embedded in connection status widget with modal details view
- **Responsive Design**: Adapts to different screen sizes and resolutions
- **Visual Feedback**: Loading states, status badges, and interactive elements
- **Dark Theme**: Security-focused interface with purple accent color (#7100d0)
- **Navigation**: Client-side routing with page transitions
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
│   │   └── diagnostics.py        # ADB diagnostics system
│   ├── monitoring/               # Health and process monitoring
│   │   ├── __init__.py
│   │   ├── health_manager.py     # Health check system
│   │   └── process_manager.py    # Process cleanup and PID tracking
│   ├── frida_servers/            # Cached Frida server binaries
│   │   └── {version}/            # Version-specific directories
│   │       └── {arch}/           # Architecture-specific binaries
│   ├── logs/                     # Application logs (not in backend/)
│   ├── routers/                  # API route modules (future)
│   ├── venv/                     # Python virtual environment
│   ├── main.py                   # FastAPI application entry
│   └── requirements.txt          # Python dependencies
│
├── frontend/                     # Vue 3 frontend
│   ├── src/
│   │   ├── components/           # Reusable Vue components
│   │   │   ├── DeviceCard.vue    # Device card component
│   │   │   ├── LogViewer.vue     # Log streaming component
│   │   │   └── ToastNotification.vue  # Toast notification system
│   │   ├── composables/          # Vue composables
│   │   │   ├── useApiConnection.js    # Backend connection management
│   │   │   └── useToast.js            # Toast notification composable
│   │   ├── router/               # Vue Router configuration
│   │   │   └── index.js          # Route definitions
│   │   ├── views/                # Page components
│   │   │   ├── Dashboard.vue     # Device list view
│   │   │   └── DeviceDetails.vue # Device detail view
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
│   └── test_logging_system.py   # Logging system validation
├── history_docs/                 # Project documentation
├── launcher.py                   # Unified application launcher
├── start.sh                      # Linux startup script
├── setup.sh                      # Linux setup script
├── README.md                     # Project documentation
├── DEVELOPMENT_RULES.md          # Development guidelines
└── LICENSE                       # License information
```

## Development

### Backend Development

The backend follows a modular architecture with clear separation of concerns:

- `backend/main.py`: FastAPI application entry point with all API endpoints and WebSocket handlers
- `backend/core/adb_manager.py`: ADB client wrapper for device communication and shell command execution
- `backend/core/device_manager.py`: Device enumeration combining ADB and Frida data sources
- `backend/core/installer.py`: Complete Frida server installation, version management, and lifecycle control with intelligent caching
- `backend/core/log_streamer.py`: Real-time log streaming with WebSocket support, buffer management, and separate handling for active streams (logcat, frida_server) vs event-driven logs (adb_operations, frida_install)
- `backend/core/logger.py`: Centralized logging with categorized output and rotating file handlers
- `backend/core/diagnostics.py`: Comprehensive ADB diagnostics with multiple test suites
- `backend/monitoring/health_manager.py`: Health monitoring system with periodic checks
- `backend/monitoring/process_manager.py`: Process cleanup and PID file management
- `backend/routers/`: API route handlers (reserved for future modularization)

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
- `frontend/src/App.vue`: Root component with navigation header, global state, and custom Frida download widget with architecture-first selection workflow
- `frontend/src/main.js`: Application entry point with router integration
- `frontend/src/router/index.js`: Vue Router configuration for multi-page navigation
- `frontend/src/style.css`: Global styles and theme configuration

**Views:**
- `frontend/src/views/Dashboard.vue`: Device list with auto-refresh and scanning capabilities
- `frontend/src/views/DeviceDetails.vue`: Compact device management interface with Frida controls, integrated diagnostics, and modal-based detail views for installation options and log streaming

**Components:**
- `frontend/src/components/DeviceCard.vue`: Reusable device card with status indicators and actions
- `frontend/src/components/LogViewer.vue`: Compact real-time log streaming with WebSocket integration, auto-start capabilities, and reduced height for better screen utilization
- `frontend/src/components/ToastNotification.vue`: Toast notification display system

**Composables:**
- `frontend/src/composables/useApiConnection.js`: Backend connection management with auto-reconnect
- `frontend/src/composables/useToast.js`: Toast notification state management

**Technical Implementation:**
- Vue 3 Composition API for reactive state management
- WebSocket integration for real-time log streaming with connection state tracking
- Automatic reconnection with exponential backoff for backend connectivity
- Client-side routing with Vue Router
- Tailwind CSS with DaisyUI components for consistent styling, including card-compact variants
- Smart auto-streaming: ADB Operations, Frida Install, and Frida Server logs auto-start on page load
- Manual logcat activation to prevent performance impact from verbose system logs
- Optimized polling intervals: 15s for device details, 30s for Frida connection tests
- Direct GitHub API integration: Fetches latest 10 Frida releases client-side to avoid backend overhead
- Architecture-first workflow: Users select architecture before version selection for custom downloads
- Modal-based detail views: Comprehensive information accessible via "Details" buttons without cluttering main interface

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

The project includes a test suite for validating the centralized logging system.

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

The test suite provides comprehensive validation that all logging components correctly use the centralized configuration and write to the appropriate directories.

## Troubleshooting

### Backend Issues

**ADB Not Connected:**
- Ensure ADB is installed and available in PATH
- Check that ADB server is running: `adb devices`
- Verify USB debugging is enabled on target devices
- Try restarting ADB via the UI or: `adb kill-server && adb start-server`

**Frida Installation Fails:**
- Select the correct architecture first before choosing a version
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
- Check logs in `logs/backend/health_monitor.log`
- Verify ADB server is running
- Ensure no port conflicts on 8000

### Frontend Issues

**Device List Empty:**
- Click "Scan Devices" to trigger device enumeration
- Verify backend is running and accessible
- Check browser console for API errors
- Use the ADB restart button if connection is lost

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
