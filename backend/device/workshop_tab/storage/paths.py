# Workshop data directory paths and management
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
LOCAL_STORAGE_ROOT = PROJECT_ROOT / "local_storage"

WORKSHOP_CONFIG_DIR = LOCAL_STORAGE_ROOT / "config"
WORKSHOP_DISCOVERIES_DIR = LOCAL_STORAGE_ROOT / "saved_discoveries"

CATEGORIZATION_RULES_FILE = WORKSHOP_CONFIG_DIR / "categorization_rules.json"
APP_FOCUSED_CONFIG_DIR = WORKSHOP_CONFIG_DIR / "app_focused"


def ensure_workshop_directories():
    WORKSHOP_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    WORKSHOP_DISCOVERIES_DIR.mkdir(parents=True, exist_ok=True)
    APP_FOCUSED_CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def get_app_focused_config_dir(package_id: str) -> Path:
    safe_package = package_id.replace("/", "_").replace(".", "_")
    config_dir = APP_FOCUSED_CONFIG_DIR / safe_package
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_app_focused_default_config(package_id: str) -> Path:
    return get_app_focused_config_dir(package_id) / "default.json"


def get_app_focused_templates_dir(package_id: str) -> Path:
    templates_dir = get_app_focused_config_dir(package_id) / "templates"
    templates_dir.mkdir(parents=True, exist_ok=True)
    return templates_dir




def get_package_discoveries_dir(package_id: str, subfolder: str = None) -> Path:
    safe_package = package_id.replace("/", "_")
    package_dir = WORKSHOP_DISCOVERIES_DIR / safe_package
    
    if subfolder:
        safe_subfolder = subfolder.replace("\\", "/")
        parts = [p.strip() for p in safe_subfolder.split("/") if p.strip()]
        for part in parts:
            safe_part = part.replace("/", "_").replace("\\", "_")
            package_dir = package_dir / safe_part
    
    package_dir.mkdir(parents=True, exist_ok=True)
    return package_dir


def get_discovery_dir(package_id: str, discovery_folder: str, subfolder: str = None) -> Path:
    package_dir = get_package_discoveries_dir(package_id, subfolder)
    discovery_dir = package_dir / discovery_folder
    return discovery_dir


def get_discovery_dir_by_path(save_path: str, discovery_folder: str) -> Path:
    if save_path:
        safe_path = save_path.replace("\\", "/")
        parts = [p.strip() for p in safe_path.split("/") if p.strip()]
        target_dir = WORKSHOP_DISCOVERIES_DIR
        for part in parts:
            safe_part = part.replace("/", "_").replace("\\", "_")
            target_dir = target_dir / safe_part
    else:
        target_dir = WORKSHOP_DISCOVERIES_DIR
    
    return target_dir / discovery_folder


def create_discovery_folder_name(version: str, custom_name: str = None) -> str:
    from datetime import datetime
    
    if custom_name:
        safe_custom = custom_name.replace("/", "_").replace("\\", "_").replace(" ", "_")
        return safe_custom
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    if not version or version == "None" or version == "null":
        safe_version = "unknown"
    else:
        safe_version = str(version).replace("/", "_").replace(" ", "_")
    return f"{date_str}_{safe_version}"


def list_package_discoveries(package_id: str, subfolder: str = None) -> list:
    package_dir = get_package_discoveries_dir(package_id, subfolder)
    if not package_dir.exists():
        return []
    
    discoveries = []
    for item in sorted(package_dir.iterdir(), reverse=True):
        if item.is_dir():
            metadata_file = item / "metadata.json"
            discoveries.append({
                "folder": item.name,
                "path": str(item),
                "subfolder": subfolder,
                "has_metadata": metadata_file.exists()
            })
    return discoveries


def list_all_packages_with_discoveries() -> list:
    if not WORKSHOP_DISCOVERIES_DIR.exists():
        return []
    
    packages = []
    
    def scan_directory(base_dir: Path, package_id: str, current_subfolder: str = None):
        for item in sorted(base_dir.iterdir()):
            if item.is_dir():
                metadata_file = item / "metadata.json"
                if metadata_file.exists():
                    discoveries = list_package_discoveries(package_id, current_subfolder)
                    if discoveries:
                        return discoveries
                else:
                    subfolder_path = f"{current_subfolder}/{item.name}" if current_subfolder else item.name
                    nested_discoveries = scan_directory(item, package_id, subfolder_path)
                    if nested_discoveries:
                        return nested_discoveries
        return []
    
    for item in sorted(WORKSHOP_DISCOVERIES_DIR.iterdir()):
        if item.is_dir():
            all_discoveries = scan_directory(item, item.name)
            if all_discoveries:
                packages.append({
                    "package_id": item.name,
                    "discovery_count": len(all_discoveries),
                    "discoveries": all_discoveries
                })
    return packages
