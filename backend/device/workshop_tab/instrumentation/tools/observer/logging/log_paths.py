from pathlib import Path
from datetime import datetime
from core.log_paths import LOGS_INSTRUMENTATION_OBSERVER

INSTRUMENTATION_LOGS_ROOT = LOGS_INSTRUMENTATION_OBSERVER


def generate_session_name() -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    return f"session_{timestamp}"


def get_observer_session_path(app_package: str, session_name: str) -> Path:
    safe_package = app_package.replace(".", "_")
    date_str = datetime.now().strftime("%Y-%m-%d")
    return INSTRUMENTATION_LOGS_ROOT / safe_package / date_str / session_name


def ensure_observer_directories():
    INSTRUMENTATION_LOGS_ROOT.mkdir(parents=True, exist_ok=True)
