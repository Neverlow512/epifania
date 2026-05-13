# Epifania

A web-based GUI for Android dynamic instrumentation using Frida and ADB.

<div align="center">

![Platform](https://img.shields.io/badge/platform-Linux-blue)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![Node](https://img.shields.io/badge/node-18+-green)
![License](https://img.shields.io/badge/license-MIT-green)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/Neverlow512/epifania)
</div>

---

> **⚠️ Project Status: Paused / Research Hobby Project**
>
> Epifania, while nice and useful, was built as a personal research and hobby project to solve my own workflow bottlenecks in dynamic instrumentation. I am a Reverse Engineer, not a full-stack developer.
>
> Please be aware:
> - **Code Quality:** The frontend and backend architectures were built for speed of workflow, not enterprise scalability. Expect some spaghetti code, hacky workarounds, and non-standard implementations.
> - **Bugs & Security:** This is a local analysis tool. It has not been heavily audited for vulnerabilities. Do not expose this dashboard to the internet.
> - **Maintenance:** I am not actively maintaining this, fixing bugs, or accepting feature requests at this time. There might be future updates, but no guarantees.
>
> Use it as a reference, fork it, or strip it for parts at your own risk.

---

## Overview

Epifania provides a local web interface for Android security testing and runtime analysis. It wraps Frida and ADB functionality into a single dashboard, handling the common tasks like device management, process monitoring, and instrumentation setup.

The tool runs entirely on your machine - no cloud services, no external dependencies beyond what you already use for mobile security work.

### What It Does

- Manages Android device connections and monitors their state
- Handles Frida server installation, deployment, and lifecycle
- Provides real-time process monitoring with detailed inspection
- Controls application installation, launching, and data management
- Offers a Workshop mode for runtime class discovery and method extraction
- Hooks selected Java and native methods in a live process with real-time call statistics via the Instrumentation Mode
- Injects Frida scripts and hooks Java and native methods in real-time via the Instrumentation Mode, without leaving the dashboard - working but not fully finished.
- Tracks system resources (CPU, memory, storage, network)
- Streams logs in real-time via WebSocket

The frontend is a Vue.js application, the backend is FastAPI with Python, and everything communicates over a REST API with WebSocket support for live updates.

---

## Installation

### Prerequisites

You'll need:
- Linux system (primary development and testing platform)
- Python 3.8 or newer
- Node.js 18 or newer
- ADB installed and accessible in your PATH
- Android device with USB debugging enabled

### Setup

Clone the repository and run the setup script:

```bash
git clone https://github.com/Neverlow512/epifania.git
cd epifania
./setup.sh
```

The script creates isolated virtual environments for Python and Node.js, then installs all dependencies.

### Running

Start both services with the launcher:

```bash
python3 launcher.py
```

Access the interface at:
- **Frontend**: http://127.0.0.1:5173
- **Backend API**: http://127.0.0.1:8000

The launcher handles graceful shutdown with Ctrl+C.

---

## Core Features

### Device Management

Connects to Android devices via ADB and displays:
- Connection status and device enumeration
- Device specifications (brand, model, Android version, architecture)
- Root status detection
- Multi-device support with per-device tabs

### Frida Server Management

Automates the typical Frida setup workflow:
- Downloads and installs Frida server binaries
- Manages multiple versions with caching
- Provides start/stop/restart controls
- Tests connections and validates functionality
- Discovers existing Frida servers on devices
- Handles permission setup automatically

### Process Monitoring

Real-time view of running processes with:
- Process list with filtering (show/hide kernel threads)
- State detection (foreground, background, cached, persistent)
- Detailed inspection per process:
  - Memory metrics (PSS, USS via smaps_rollup)
  - Thread enumeration with CPU time tracking
  - File descriptor listing (files, sockets, pipes, devices)
  - Network connections (TCP/UDP with state)
  - I/O statistics
  - Process relationships (parent, children, tree depth)
- Process termination controls
- Historical metrics and churn tracking

### Package Management

Standard application lifecycle operations:
- List installed packages (user/system filtering)
- View package details (version, SDK targets, permissions, sizes)
- Install and uninstall APKs
- Launch and force-stop applications
- Extract APK files to local filesystem
- Clear cache and data
- Integration with process list (jump to running processes)

### Workshop Tab

The main analysis workspace. Discover classes and methods from a live process, then feed them directly into the Instrumentation Mode for hooking — all without leaving the tab.

**Lazy Discovery System:**
- Fast initial scan (class names only, completes in under a second)
- On-demand ClassLoader scanning for accurate classification
- Batch method extraction with progress tracking
- Cancellable operations

**Filter Modes:**
- **Focused**: Custom regex patterns for targeting specific packages (useful for obfuscated apps)
- **Package**: App-specific classes only
- **All**: Complete class enumeration

**State Management:**
- Auto-saves discovery state (per-class during operations, periodic backups every 30 seconds)
- Crash recovery with restoration modal
- Configurable retention (keeps latest 10 discoveries per package)
- Install marker detection (warns if app was updated since last discovery)

**Discovery Types:**
- Java classes with source classification (app, bundled, system)
- Obfuscation detection
- Native modules with exports
- Method modifier scanning (access flags, static, abstract, etc.)
- Rule-based categorization engine

**Storage:**
- Persistent results with versioning
- Verbose logging per session with auto-cleanup
- Performance metrics in operation logs

### Instrumentation Mode

Runtime method hooking interface built on top of the Workshop session. Select methods from your discovery results and inject hooks directly into a running process without leaving the dashboard.

**Observer Tool:**
- Hooks Java and native methods simultaneously in the same session
- Live per-hook stats: call count, error count, and smoothed call rate (EMA)
- Speedometer gauge showing aggregate hook activity against a dynamic ceiling
- Hook cards sortable by top activity, most calls, most errors, or alphabetically
- Filterable view: all hooks, active only, or hooks with errors
- Optional time-limited sessions with automatic stop
- Structured session logs written per-run with metadata and aggregated summaries

### System Monitoring

Tracks device resources:
- CPU usage across processes
- Memory consumption with deltas
- Storage partition usage
- Network statistics
- Per-process network connections

All monitoring respects session management to prevent conflicts across browser tabs.

---

## Architecture

### Backend

Python FastAPI application with modular managers:
- Native ADB integration via subprocess
- Frida instrumentation orchestration
- Separate managers for devices, processes, packages, health monitoring, and diagnostics
- WebSocket support for real-time log streaming
- Request-scoped caching (InspectionContext) to deduplicate ADB calls during process inspection

### Frontend

Vue 3 single-page application:
- Composition API with feature-based directory structure
- Vue Router for navigation with deep linking
- Tailwind CSS + DaisyUI for styling
- Axios for HTTP communication
- WebSocket client with auto-reconnect (exponential backoff)
- Tabbed interface with per-device state management

### Communication

REST API for commands and queries, WebSocket for logs and live updates. The backend serves the API on port 8000, the frontend dev server runs on 5173.

---

## Documentation

Complete documentation is in the [Wiki](https://github.com/Neverlow512/epifania/wiki):

**Getting Started:**
- [Introduction](https://github.com/Neverlow512/epifania/wiki/01.01-Getting-Started---Introduction)
- [Architecture Overview](https://github.com/Neverlow512/epifania/wiki/01.02-Getting-Started---Architecture-Overview)
- [Prerequisites](https://github.com/Neverlow512/epifania/wiki/Getting-Started---01.03-Prerequisites)
- [Installation](https://github.com/Neverlow512/epifania/wiki/01.04-Getting-Started---Installation)
- [Running the Application](https://github.com/Neverlow512/epifania/wiki/Getting-Started---01.05-Running-The-Application)

**API Reference:**
- [Device Management](https://github.com/Neverlow512/epifania/wiki/02.02-API---Device-Management)
- [Frida Management](https://github.com/Neverlow512/epifania/wiki/02.03-API---Frida-Management)
- [Process Management](https://github.com/Neverlow512/epifania/wiki/02.04-API---Process-Management)
- [Package Management](https://github.com/Neverlow512/epifania/wiki/02.08-API---Package-Management)
- [Workshop Management](https://github.com/Neverlow512/epifania/wiki/02.10-API---Workshop-Management)
- [System Monitoring](https://github.com/Neverlow512/epifania/wiki/02.11-API---System-Monitoring)

**Development:**
- [Backend Development](https://github.com/Neverlow512/epifania/wiki/04.01-Development---Backend-Development)
- [Frontend Development](https://github.com/Neverlow512/epifania/wiki/04.04-Development---Frontend-Development)
- [Workshop Architecture](https://github.com/Neverlow512/epifania/wiki/04.03-Development---Workshop-Backend-Module-Architecture)

**Troubleshooting:**
- [Backend Issues](https://github.com/Neverlow512/epifania/wiki/05.01-Troubleshooting---Backend-Issues)
- [Frontend Issues](https://github.com/Neverlow512/epifania/wiki/05.02-Troubleshooting---Frontend-Issues)
- [Workshop Limitations](https://github.com/Neverlow512/epifania/wiki/05.04-Troubleshooting---Workshop-Tab-Known-Limitations)

---

## Development

### Running Services Independently

If you want to run services separately for development:

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

### Project Structure

```
epifania/
├── backend/              # FastAPI backend
│   ├── main.py          # Application entry point
│   ├── managers/        # Modular manager classes
│   ├── models/          # Pydantic models
│   └── venv/            # Python virtual environment
├── frontend/            # Vue 3 frontend
│   ├── src/
│   │   ├── views/      # Page components
│   │   ├── components/ # Reusable components
│   │   └── composables/# Shared logic
│   └── node_modules/   # Node dependencies
├── logs/               # Categorized log output
├── launcher.py         # Unified service launcher
└── setup.sh           # Environment setup script
```

See the [Development Guide](https://github.com/Neverlow512/epifania/wiki/Development---06.01-Backend-Development) for detailed architecture documentation.

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Backend Framework | FastAPI |
| Frontend Framework | Vue 3 (Composition API) |
| Build Tool | Vite |
| Styling | Tailwind CSS + DaisyUI |
| Dynamic Instrumentation | Frida |
| Device Communication | ADB (subprocess) |
| Real-time Communication | WebSocket |
| Client-side Routing | Vue Router |
| HTTP Client | Axios |

---

## Status

Development is paused. Core functionality is implemented and stable:

**Implemented:**
- ✅ Device management and monitoring
- ✅ Frida server lifecycle management
- ✅ Process monitoring with detailed inspection
- ✅ Package management and lifecycle control
- ✅ Workshop tab with lazy discovery
- ✅ System resource monitoring
- ✅ Real-time log streaming
- ✅ Crash recovery and state management
- ✅ Session management across browser tabs
- ✅ Real-time hook monitoring dashboard (Observer)
- ✅ Instrumentation mode with live hook statistics and speedometer gauge

**Incomplete / Paused:**
- 🔄 Files tab for device filesystem browsing

---

## Common Issues

**Device not showing up:**
- Verify USB debugging is enabled on the device
- Run `adb devices` to confirm ADB sees it
- Try the built-in diagnostics: `GET /api/diagnostics/adb`

**Frida server fails to start:**
- Check that device is rooted (or app is debuggable)
- Verify Frida server binary has execute permissions
- Check logs in `logs/frida_operations/`

**Frontend won't connect:**
- Confirm backend is running at http://127.0.0.1:8000
- Check browser console for errors
- Look at backend terminal output for API issues

See the [Troubleshooting Guide](https://github.com/Neverlow512/epifania/wiki/Troubleshooting---07.01-Backend-Issues) for more details.

---

## Disclaimer

This tool is intended for security research and educational purposes. Only use it on devices you own or have permission to test.

---

## License

MIT. See [LICENSE](LICENSE) for details.

---

## Acknowledgments

This project relies on [Frida](https://frida.re/) for dynamic instrumentation.
