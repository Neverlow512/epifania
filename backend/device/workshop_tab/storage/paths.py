# Workshop data directory paths and management
from pathlib import Path

BACKEND_ROOT = Path(__file__).parent.parent.parent.parent
WORKSHOP_DATA_ROOT = BACKEND_ROOT / "workshop_data"

WORKSHOP_CONFIG_DIR = WORKSHOP_DATA_ROOT / "config"
WORKSHOP_DISCOVERIES_DIR = WORKSHOP_DATA_ROOT / "discoveries"

CATEGORIZATION_RULES_FILE = WORKSHOP_CONFIG_DIR / "categorization_rules.json"


def ensure_workshop_directories():
    WORKSHOP_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    WORKSHOP_DISCOVERIES_DIR.mkdir(parents=True, exist_ok=True)


def get_package_discoveries_dir(package_id: str) -> Path:
    safe_package = package_id.replace("/", "_")
    package_dir = WORKSHOP_DISCOVERIES_DIR / safe_package
    package_dir.mkdir(parents=True, exist_ok=True)
    return package_dir


def get_discovery_dir(package_id: str, discovery_folder: str) -> Path:
    package_dir = get_package_discoveries_dir(package_id)
    discovery_dir = package_dir / discovery_folder
    return discovery_dir


def create_discovery_folder_name(version: str) -> str:
    from datetime import datetime
    date_str = datetime.now().strftime("%Y-%m-%d")
    safe_version = version.replace("/", "_").replace(" ", "_")
    return f"{date_str}_{safe_version}"


def list_package_discoveries(package_id: str) -> list:
    package_dir = get_package_discoveries_dir(package_id)
    if not package_dir.exists():
        return []
    
    discoveries = []
    for item in sorted(package_dir.iterdir(), reverse=True):
        if item.is_dir():
            metadata_file = item / "metadata.json"
            discoveries.append({
                "folder": item.name,
                "path": str(item),
                "has_metadata": metadata_file.exists()
            })
    return discoveries


def list_all_packages_with_discoveries() -> list:
    if not WORKSHOP_DISCOVERIES_DIR.exists():
        return []
    
    packages = []
    for item in sorted(WORKSHOP_DISCOVERIES_DIR.iterdir()):
        if item.is_dir():
            discoveries = list_package_discoveries(item.name)
            if discoveries:
                packages.append({
                    "package_id": item.name,
                    "discovery_count": len(discoveries),
                    "discoveries": discoveries
                })
    return packages

