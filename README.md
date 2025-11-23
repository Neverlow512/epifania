# Epifania

A GUI-based Dynamic Instrumentation Platform wrapping Frida and ADB for security researchers.

## Project Status

**Current Stage:** Active Development

**Implemented Features:**
- ✅ Full ADB integration for accurate Android device detection
- ✅ Backend API with FastAPI serving comprehensive device information
- ✅ Professional security tool UI with refined dark theme (#7100d0 primary color)
- ✅ Device enumeration with detailed specifications (brand, model, Android version, architecture, root status)
- ✅ Frida availability detection per device
- ✅ Real-time ADB connection status monitoring
- ✅ Interactive UI with button feedback, focus states, and disabled state handling
- ✅ Responsive device cards with hover effects and status indicators
- ✅ Comprehensive logging system with categorized log directories
- ✅ Virtual environment setup for Python and Node.js dependency isolation
- ✅ Automated startup scripts for development environment
- ✅ Frida server installation, management, and version control
- ✅ Real-time log streaming via WebSocket (logcat, Frida operations, ADB operations)
- ✅ Device detail view with comprehensive management interface
- ✅ Frida server start/stop/restart controls
- ✅ Cached Frida server management and deployment
- ✅ Auto-refresh device list with connection state tracking
- ✅ Vue Router integration with multi-page navigation

**Planned Features:**
- 🔄 Process enumeration and management
- 🔄 Application listing and package management
- 🔄 Script injection interface with code editor
- 🔄 Memory inspection tools
- 🔄 Network traffic interception

## Architecture

Epifania is a local web-based tool designed for security analysis and dynamic instrumentation of mobile applications. The platform consists of two main components:

### Backend (Python/FastAPI)

The backend serves as the orchestration layer, managing device connections and Frida instrumentation. It provides a RESTful API for frontend communication with full ADB integration.

- **FastAPI**: High-performance web framework for API endpoints
- **Frida**: Dynamic instrumentation toolkit for runtime analysis
- **pure-python-adb**: Full Android Debug Bridge integration for device management and communication
- **Modular Architecture**: Separate managers for ADB, devices, and installation tasks

### Frontend (Vue.js/Vite)

The frontend provides a professional, modern dashboard designed for security researchers with a refined dark theme centered around the Epifania brand color (#7100d0) and black backgrounds.

- **Vue 3**: Progressive JavaScript framework with Composition API
- **Vue Router**: Client-side routing for multi-page navigation
- **Vite**: Fast build tool and development server
- **Tailwind CSS**: Utility-first CSS framework with custom security-focused design
- **DaisyUI**: Component library with custom Epifania dark theme
- **Axios**: HTTP client for API communication
- **WebSocket**: Real-time bidirectional communication for log streaming
- **Modern Typography**: Space Grotesk display font for brand identity
- **Interactive Feedback**: Button states with focus rings, press animations, and disabled states

## Prerequisites

Before installing Epifania, ensure the following dependencies are installed:

- **Python 3.8+**: Backend runtime environment
- **Node.js 18+**: Frontend build tooling and development server
- **ADB**: Android Debug Bridge must be installed and available in PATH
- **USB Debugging**: Enable USB debugging on target Android devices

## Installation

### Quick Setup (Recommended)

Use the automated setup script to create isolated virtual environments and install all dependencies:

**Linux/macOS:**
```bash
git clone https://github.com/Neverlow512/epifania.git
cd epifania
./setup.sh
```

**Windows:**
```cmd
git clone https://github.com/Neverlow512/epifania.git
cd epifania
setup.bat
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
source venv/bin/activate  # On Windows: venv\Scripts\activate
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

**Linux/macOS:**
```bash
./start.sh
```

**Windows:**
```bash
python launcher.py
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
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**Frontend:**
```bash
cd frontend
npm run dev
```

## API Endpoints

### Health Check

```
GET /health
```

Returns the operational status of the backend service and ADB connection.

**Response:**
```json
{
  "status": "healthy",
  "adb_connected": true
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

#### Install Frida Server

```
POST /api/devices/{device_id}/frida/install
```

Downloads, installs, and starts Frida server on the target device.

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
| Device Management | pure-python-adb | 0.3.0.dev0 | Android device communication |
| Data Validation | Pydantic | 2.12.4 | Request/response validation |
| WebSocket | websockets | 13.1 | Real-time log streaming |
| Frontend Framework | Vue 3 | 3.5.24 | Reactive user interface |
| Routing | Vue Router | 4.6.3 | Client-side navigation |
| Build Tool | Vite | 7.2.4 | Development server and bundler |
| Styling | Tailwind CSS | 4.1.17 | Utility-first CSS framework |
| UI Components | DaisyUI | 5.5.5 | Component library |
| HTTP Client | Axios | 1.13.2 | API communication |

## Features

### Device Management

- **Automatic Device Detection**: Scans and enumerates all connected Android devices and emulators via ADB
- **Device Information**: Displays comprehensive device specifications including brand, model, Android version, SDK level, architecture, and root status
- **Connection Monitoring**: Real-time tracking of device connection states with auto-refresh
- **Device Persistence**: Maintains device list with disconnection tracking across scans

### Frida Integration

- **Version Management**: Browse and select from available Frida server versions from GitHub releases
- **Automated Installation**: One-click download, installation, and deployment of Frida server to devices
- **Server Lifecycle Control**: Start, stop, and restart Frida server processes on target devices
- **Cached Binary Management**: Store and reuse downloaded Frida server binaries for faster deployment
- **Architecture Detection**: Automatic mapping of Android ABIs to Frida architectures
- **Status Monitoring**: Real-time display of Frida server version and running status

### Real-time Logging

- **WebSocket Streaming**: Bidirectional real-time log streaming with automatic reconnection
- **Multiple Log Types**:
  - **Logcat**: Android system logs (manual-start for performance)
  - **Frida Installation**: Installation process logs (auto-streaming)
  - **Frida Server**: Server lifecycle logs (auto-streaming)
  - **ADB Operations**: All ADB command logs (auto-streaming)
- **Smart Filtering**: Automatic filtering of noisy system logs in logcat
- **Buffer Management**: Configurable log buffer sizes with deduplication
- **Historical Logs**: Access to buffered historical logs on connection
- **Log Controls**: Clear, scroll-to-bottom, and stream start/stop controls

### User Interface

- **Dashboard View**: Grid layout of device cards with quick actions
- **Device Details View**: Comprehensive management interface for individual devices
- **Responsive Design**: Adapts to different screen sizes and resolutions
- **Visual Feedback**: Loading states, status badges, and interactive animations
- **Professional Theme**: Security-focused dark theme with purple accent color
- **Navigation**: Client-side routing with smooth page transitions

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
│   │   └── logger.py             # Centralized logging
│   ├── frida_servers/            # Cached Frida server binaries
│   │   └── {version}/            # Version-specific directories
│   │       └── {arch}/           # Architecture-specific binaries
│   ├── logs/                     # Application logs
│   │   ├── backend/              # Backend logs
│   │   ├── device/               # Device operation logs
│   │   ├── server/               # Server process logs
│   │   └── central.log           # Aggregated logs
│   ├── routers/                  # API route modules (future)
│   ├── venv/                     # Python virtual environment
│   ├── main.py                   # FastAPI application entry
│   └── requirements.txt          # Python dependencies
│
├── frontend/                     # Vue 3 frontend
│   ├── src/
│   │   ├── components/           # Reusable Vue components
│   │   │   ├── DeviceCard.vue    # Device card component
│   │   │   └── LogViewer.vue     # Log streaming component
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
├── logs/                         # Root-level logs
├── history_docs/                 # Project documentation
├── launcher.py                   # Unified application launcher
├── start.sh                      # Linux/macOS startup script
├── setup.sh                      # Linux/macOS setup script
├── setup.bat                     # Windows setup script
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
- `backend/core/installer.py`: Complete Frida server installation, version management, and lifecycle control
- `backend/core/log_streamer.py`: Real-time log streaming with WebSocket support and buffer management
- `backend/core/logger.py`: Centralized logging with categorized output and rotating file handlers
- `backend/routers/`: API route handlers (reserved for future modularization)

### Logging Structure

Logs are organized into categorized directories:

- `logs/central.log`: Aggregated log of all important events
- `logs/backend/`: Backend application logs
  - `backend.log`: General backend operations
  - `error.log`: Error-level logs only
- `logs/device/`: Device management and ADB operations
  - `device.log`: Device enumeration and communication
- `logs/server/`: Server process logs
  - `uvicorn.log`: FastAPI server output
  - `vite.log`: Vite dev server output

### Frontend Development

The frontend uses Vue 3 Composition API with a modern, security-focused design:

**Application Structure:**
- `frontend/src/App.vue`: Root component with navigation header and global state
- `frontend/src/main.js`: Application entry point with router integration
- `frontend/src/router/index.js`: Vue Router configuration for multi-page navigation
- `frontend/src/style.css`: Custom Epifania dark theme with DaisyUI integration

**Views:**
- `frontend/src/views/Dashboard.vue`: Device list with auto-refresh and scanning capabilities
- `frontend/src/views/DeviceDetails.vue`: Comprehensive device management interface with Frida controls

**Components:**
- `frontend/src/components/DeviceCard.vue`: Reusable device card with status indicators and actions
- `frontend/src/components/LogViewer.vue`: Real-time log streaming with WebSocket integration and auto-start capabilities

**Design Features:**
- Pure black background (#000000) with subtle transparency layers
- Primary brand color (#7100d0) used consistently across interactive elements
- Space Grotesk display font for brand identity (all-caps, tight letter spacing)
- Interactive button states with press animations and focus rings
- Glassmorphism effects with backdrop blur on cards and panels
- Animated status indicators with pulse effects
- Responsive grid layout adapting to screen sizes
- Professional device cards with comprehensive information display
- Auto-streaming logs for debugging (Frida Install, Frida Server, ADB Operations)
- Manual-start logcat streaming for performance optimization

### Dependency Management

#### Python Dependencies

All Python dependencies are isolated in `backend/venv/`. To update:

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
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
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Frontend only:
```bash
cd frontend
npm run dev
```

## Troubleshooting

### Backend Issues

**ADB Not Connected:**
- Ensure ADB is installed and available in PATH
- Check that ADB server is running: `adb devices`
- Verify USB debugging is enabled on target devices

**Frida Installation Fails:**
- Verify device has sufficient storage space
- Check that device has root access (for system-level installation)
- Ensure correct architecture is selected
- Try manually pushing the binary via ADB

**WebSocket Connection Fails:**
- Check that backend is running on port 8000
- Verify no firewall is blocking WebSocket connections
- Check browser console for connection errors

### Frontend Issues

**Device List Empty:**
- Click "Scan Devices" to trigger device enumeration
- Verify backend is running and accessible
- Check browser console for API errors

**Logs Not Streaming:**
- Verify WebSocket connection is established
- Check that device is still connected
- Try manually starting the log stream with the play button

**Page Not Loading:**
- Clear browser cache and reload
- Check that frontend dev server is running on port 5173
- Verify no port conflicts with other applications

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

## License

This project is intended for security research and educational purposes.

