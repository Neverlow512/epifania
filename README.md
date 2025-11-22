# Epifania

A GUI-based Dynamic Instrumentation Platform wrapping Frida and ADB for security researchers.

## Project Status

**Current Stage:** Active Development

**Implemented Features:**
- ✅ Full ADB integration for accurate Android device detection
- ✅ Backend API with FastAPI serving comprehensive device information
- ✅ Professional security tool UI with refined dark theme (#7100d0 primary color)
- ✅ Device enumeration with detailed specifications (brand, model, Android version, architecture)
- ✅ Frida availability detection per device
- ✅ Real-time ADB connection status monitoring
- ✅ Interactive UI with button feedback, focus states, and disabled state handling
- ✅ Responsive device cards with hover effects and status indicators
- ✅ Comprehensive logging system with categorized log directories
- ✅ Virtual environment setup for Python and Node.js dependency isolation
- ✅ Automated startup scripts for development environment

**In Progress:**
- 🔄 Frida server auto-installation and updates
- 🔄 Advanced device interaction capabilities (process enumeration, app management)
- 🔄 Script injection interface

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
- **Vite**: Fast build tool and development server
- **Tailwind CSS**: Utility-first CSS framework with custom security-focused design
- **DaisyUI**: Component library with custom Epifania dark theme
- **Axios**: HTTP client for API communication
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

### List Devices

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
      "frida_available": true,
      "frida_name": "Pixel 3"
    },
    {
      "id": "1234567890ABCDEF",
      "name": "Samsung Galaxy S21",
      "type": "physical",
      "brand": "Samsung",
      "model": "SM-G991B",
      "android_version": "13",
      "sdk_version": "33",
      "architecture": "arm64-v8a",
      "serial": "1234567890ABCDEF",
      "state": "online",
      "frida_available": true,
      "frida_name": "Galaxy S21"
    }
  ]
}
```

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Backend Framework | FastAPI | RESTful API server |
| Backend Runtime | Python 3.8+ | Orchestration and business logic |
| Instrumentation | Frida | Dynamic code injection and hooking |
| Device Management | pure-python-adb | Android device communication |
| Frontend Framework | Vue 3 | Reactive user interface |
| Build Tool | Vite | Development server and bundler |
| Styling | Tailwind CSS + DaisyUI | Component styling and theming |
| HTTP Client | Axios | API communication |

## Development

### Backend Development

The backend follows a modular architecture with clear separation of concerns:

- `backend/main.py`: FastAPI application entry point with API endpoints
- `backend/core/adb_manager.py`: ADB client wrapper for device communication
- `backend/core/device_manager.py`: Device enumeration combining ADB and Frida data
- `backend/core/installer.py`: Frida server installation and updates (stub)
- `backend/core/logger.py`: Centralized logging with categorized output
- `backend/routers/`: API route handlers (future expansion)

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

- `frontend/src/App.vue`: Main dashboard with device cards and management interface
- `frontend/src/main.js`: Application entry point
- `frontend/src/style.css`: Custom Epifania dark theme with DaisyUI integration

**Design Features:**
- Pure black background (#000000) with subtle transparency layers
- Primary brand color (#7100d0) used consistently across interactive elements
- Space Grotesk display font for brand identity (all-caps, tight letter spacing)
- Interactive button states with press animations and focus rings
- Glassmorphism effects with backdrop blur on cards and panels
- Animated status indicators with pulse effects
- Responsive grid layout adapting to screen sizes
- Professional device cards with comprehensive information display
- Disabled state handling for non-functional buttons (Connect requires Frida)

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

## Security Considerations

- All API endpoints validate input to prevent injection attacks
- CORS is restricted to localhost origins only
- Error messages are sanitized to avoid information disclosure
- Dependencies should be regularly updated for security patches

## License

This project is intended for security research and educational purposes.

