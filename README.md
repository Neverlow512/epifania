# Epifania

A GUI-based Dynamic Instrumentation Platform wrapping Frida and ADB for security researchers.

## Project Status

**Current Stage:** Initial Development

**Implemented Features:**
- Backend API with FastAPI serving device enumeration endpoints
- Frontend dashboard with Vue 3 and DaisyUI for device scanning
- Frida integration for device detection
- Comprehensive logging system with categorized log files
- Virtual environment setup for Python and Node.js dependency isolation
- Automated startup scripts for development environment

**In Progress:**
- Frida server auto-installation and updates
- ADB integration for Android device management
- Advanced device interaction capabilities

## Architecture

Epifania is a local web-based tool designed for security analysis and dynamic instrumentation of mobile applications. The platform consists of two main components:

### Backend (Python/FastAPI)

The backend serves as the orchestration layer, managing device connections and Frida instrumentation. It provides a RESTful API for frontend communication.

- **FastAPI**: High-performance web framework for API endpoints
- **Frida**: Dynamic instrumentation toolkit for runtime analysis
- **pure-python-adb**: Android Debug Bridge integration for device management

### Frontend (Vue.js/Vite)

The frontend provides an intuitive dashboard for interacting with connected devices and managing instrumentation sessions.

- **Vue 3**: Progressive JavaScript framework for reactive UI
- **Vite**: Fast build tool and development server
- **DaisyUI**: Component library built on Tailwind CSS
- **Axios**: HTTP client for API communication

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

Execute the launcher script from the project root:

```bash
python launcher.py
```

The launcher automatically uses the virtual environment and starts both services:

- Backend API: http://127.0.0.1:8000
- Frontend Dashboard: http://127.0.0.1:5173

Access the dashboard in your browser at http://127.0.0.1:5173

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

Returns the operational status of the backend service.

**Response:**
```json
{
  "status": "healthy"
}
```

### List Devices

```
GET /api/devices
```

Enumerates all devices accessible via Frida, including USB-connected Android devices and local system.

**Response:**
```json
{
  "devices": [
    {
      "id": "local",
      "name": "Local System",
      "type": "local"
    },
    {
      "id": "emulator-5554",
      "name": "Android Emulator 5554",
      "type": "usb"
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

The backend follows a modular architecture:

- `backend/main.py`: FastAPI application entry point
- `backend/core/device_manager.py`: Device enumeration and management
- `backend/core/installer.py`: Frida server installation and updates
- `backend/routers/`: API route handlers

### Frontend Development

The frontend uses Vue 3 Composition API:

- `frontend/src/App.vue`: Main dashboard component
- `frontend/src/main.js`: Application entry point
- `frontend/src/style.css`: Global styles and Tailwind imports

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

