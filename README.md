# Epifania

A GUI-based Dynamic Instrumentation Platform wrapping Frida and ADB for security researchers.

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

### 1. Clone Repository

```bash
git clone https://github.com/Neverlow512/epifania.git
cd epifania
```

### 2. Install Backend Dependencies

```bash
pip install -r backend/requirements.txt
```

For isolated environments, consider using a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r backend/requirements.txt
```

### 3. Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

### 4. Run Application

Execute the launcher script from the project root:

```bash
python launcher.py
```

The launcher will start both backend and frontend services concurrently:

- Backend API: http://127.0.0.1:8000
- Frontend Dashboard: http://127.0.0.1:5173

Access the dashboard in your browser at http://127.0.0.1:5173

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

### Running Services Independently

Backend only:
```bash
cd backend
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

