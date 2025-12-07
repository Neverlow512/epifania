from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
LOGS_ROOT = PROJECT_ROOT / "logs"

# Main log directories
LOGS_APPLICATION = LOGS_ROOT / "application"
LOGS_DEVICES = LOGS_ROOT / "devices"
LOGS_DIAGNOSTICS = LOGS_ROOT / "diagnostics"
LOGS_SERVICES = LOGS_ROOT / "services"
LOGS_WORKSHOP = LOGS_ROOT / "workshop"

# Application logs
LOG_CENTRAL = LOGS_APPLICATION / "central.log"
LOG_BACKEND = LOGS_APPLICATION / "backend.log"
LOG_ERRORS = LOGS_APPLICATION / "errors.log"

# Device logs
LOG_DEVICES = LOGS_DEVICES / "device.log"

# Service logs
LOG_UVICORN = LOGS_SERVICES / "uvicorn.log"
LOG_VITE = LOGS_SERVICES / "vite.log"

# Diagnostics logs
LOGS_FRIDA_ACTIVATION = LOGS_DIAGNOSTICS / "frida" / "activation"
LOGS_FRIDA_SERVER = LOGS_DIAGNOSTICS / "frida" / "server"

# Workshop logs
LOGS_WORKSHOP_DISCOVERY = LOGS_WORKSHOP / "discovery"
LOGS_WORKSHOP_FRIDA = LOGS_WORKSHOP / "frida"
LOGS_WORKSHOP_CATEGORIZATION = LOGS_WORKSHOP / "categorization"
LOGS_WORKSHOP_ERRORS = LOGS_WORKSHOP / "errors"


def ensure_log_directories():
    LOGS_APPLICATION.mkdir(parents=True, exist_ok=True)
    LOGS_DEVICES.mkdir(parents=True, exist_ok=True)
    LOGS_DIAGNOSTICS.mkdir(parents=True, exist_ok=True)
    LOGS_SERVICES.mkdir(parents=True, exist_ok=True)
    LOGS_FRIDA_ACTIVATION.mkdir(parents=True, exist_ok=True)
    LOGS_FRIDA_SERVER.mkdir(parents=True, exist_ok=True)
    LOGS_WORKSHOP_DISCOVERY.mkdir(parents=True, exist_ok=True)
    LOGS_WORKSHOP_FRIDA.mkdir(parents=True, exist_ok=True)
    LOGS_WORKSHOP_CATEGORIZATION.mkdir(parents=True, exist_ok=True)
    LOGS_WORKSHOP_ERRORS.mkdir(parents=True, exist_ok=True)

