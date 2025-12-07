# Discovery storage - JSON save/load for discovery results
import json
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from core.logger import get_logger
from device.workshop_tab.storage.paths import (
    get_discovery_dir,
    get_package_discoveries_dir,
    create_discovery_folder_name,
    ensure_workshop_directories
)

logger = get_logger(__name__, "backend")

FORMAT_VERSION = "1.0"


class DiscoveryStore:
    def __init__(self):
        ensure_workshop_directories()
    
    def save_discovery(
        self,
        package_id: str,
        package_version: str,
        metadata: Dict[str, Any],
        java_classes: Dict[str, Any],
        native_modules: Dict[str, Any]
    ) -> Optional[str]:
        try:
            folder_name = create_discovery_folder_name(package_version)
            discovery_dir = get_discovery_dir(package_id, folder_name)
            
            if discovery_dir.exists():
                timestamp = datetime.now().strftime("%H%M%S")
                folder_name = f"{folder_name}_{timestamp}"
                discovery_dir = get_discovery_dir(package_id, folder_name)
            
            discovery_dir.mkdir(parents=True, exist_ok=True)
            
            metadata_with_version = {
                "format_version": FORMAT_VERSION,
                **metadata
            }
            self._write_json(discovery_dir / "metadata.json", metadata_with_version)
            
            java_with_version = {
                "format_version": FORMAT_VERSION,
                "classes": java_classes.get("classes", [])
            }
            self._write_json(discovery_dir / "java_classes.json", java_with_version)
            
            native_with_version = {
                "format_version": FORMAT_VERSION,
                "modules": native_modules.get("modules", [])
            }
            self._write_json(discovery_dir / "native_modules.json", native_with_version)
            
            user_data = {
                "format_version": FORMAT_VERSION,
                "recategorized": [],
                "notes": [],
                "bookmarks": []
            }
            self._write_json(discovery_dir / "user_data.json", user_data)
            
            logger.info(f"Saved discovery for {package_id} to {folder_name}")
            return folder_name
            
        except Exception as e:
            logger.error(f"Failed to save discovery for {package_id}: {e}")
            return None
    
    def load_discovery(
        self,
        package_id: str,
        discovery_folder: str
    ) -> Optional[Dict[str, Any]]:
        try:
            discovery_dir = get_discovery_dir(package_id, discovery_folder)
            
            if not discovery_dir.exists():
                logger.warning(f"Discovery not found: {package_id}/{discovery_folder}")
                return None
            
            metadata = self._read_json(discovery_dir / "metadata.json")
            java_classes = self._read_json(discovery_dir / "java_classes.json")
            native_modules = self._read_json(discovery_dir / "native_modules.json")
            user_data = self._read_json(discovery_dir / "user_data.json")
            
            return {
                "metadata": metadata,
                "java_classes": java_classes,
                "native_modules": native_modules,
                "user_data": user_data
            }
            
        except Exception as e:
            logger.error(f"Failed to load discovery {package_id}/{discovery_folder}: {e}")
            return None
    
    def load_metadata_only(
        self,
        package_id: str,
        discovery_folder: str
    ) -> Optional[Dict[str, Any]]:
        try:
            discovery_dir = get_discovery_dir(package_id, discovery_folder)
            metadata_file = discovery_dir / "metadata.json"
            
            if not metadata_file.exists():
                return None
            
            return self._read_json(metadata_file)
            
        except Exception as e:
            logger.error(f"Failed to load metadata for {package_id}/{discovery_folder}: {e}")
            return None
    
    def delete_discovery(self, package_id: str, discovery_folder: str) -> bool:
        try:
            discovery_dir = get_discovery_dir(package_id, discovery_folder)
            
            if not discovery_dir.exists():
                logger.warning(f"Discovery not found for deletion: {package_id}/{discovery_folder}")
                return False
            
            shutil.rmtree(discovery_dir)
            logger.info(f"Deleted discovery: {package_id}/{discovery_folder}")
            
            package_dir = get_package_discoveries_dir(package_id)
            if package_dir.exists() and not any(package_dir.iterdir()):
                package_dir.rmdir()
                logger.info(f"Removed empty package directory: {package_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete discovery {package_id}/{discovery_folder}: {e}")
            return False
    
    def _write_json(self, file_path: Path, data: Dict[str, Any]):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _read_json(self, file_path: Path) -> Optional[Dict[str, Any]]:
        if not file_path.exists():
            return None
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)


discovery_store = DiscoveryStore()

