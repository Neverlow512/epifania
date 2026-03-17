# Discovery storage - JSON save/load for discovery results
import json
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
from core.logger import get_logger
from device.workshop_tab.storage.paths import (
    get_discovery_dir,
    get_discovery_dir_by_path,
    get_package_discoveries_dir,
    create_discovery_folder_name,
    ensure_workshop_directories
)

logger = get_logger(__name__, "backend")

FORMAT_VERSION = "1.2"


class DiscoveryStore:
    def __init__(self):
        ensure_workshop_directories()
    
    def save_discovery(
        self,
        package_id: str,
        package_version: str,
        metadata: Dict[str, Any],
        java_classes: Dict[str, Any],
        native_modules: Dict[str, Any],
        custom_name: Optional[str] = None,
        save_path: Optional[str] = None
    ) -> Optional[str]:
        try:
            folder_name = create_discovery_folder_name(package_version, custom_name)
            discovery_dir = get_discovery_dir_by_path(save_path, folder_name)
            
            if discovery_dir.exists():
                timestamp = datetime.now().strftime("%H%M%S")
                folder_name = f"{folder_name}_{timestamp}"
                discovery_dir = get_discovery_dir_by_path(save_path, folder_name)
            
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
            
            path_info = f" at path '{save_path}'" if save_path else ""
            logger.info(f"Saved discovery for {package_id} to {folder_name}{path_info}")
            return folder_name
            
        except Exception as e:
            logger.error(f"Failed to save discovery for {package_id}: {e}")
            return None
    
    def load_discovery(
        self,
        package_id: str,
        discovery_folder: str,
        subfolder: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        try:
            discovery_dir = get_discovery_dir(package_id, discovery_folder, subfolder)
            
            if not discovery_dir.exists():
                logger.warning(f"Discovery not found: {package_id}/{discovery_folder}")
                return None
            
            metadata = self._read_json(discovery_dir / "metadata.json")
            java_classes = self._read_json(discovery_dir / "java_classes.json")
            native_modules = self._read_json(discovery_dir / "native_modules.json")
            user_data = self._read_json(discovery_dir / "user_data.json")
            
            discovery_data = {
                "metadata": metadata,
                "java_classes": java_classes,
                "native_modules": native_modules,
                "user_data": user_data
            }
            
            return self._migrate_legacy_discovery(discovery_data)
            
        except Exception as e:
            logger.error(f"Failed to load discovery {package_id}/{discovery_folder}: {e}")
            return None
    
    def load_metadata_only(
        self,
        package_id: str,
        discovery_folder: str,
        subfolder: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        try:
            discovery_dir = get_discovery_dir(package_id, discovery_folder, subfolder)
            metadata_file = discovery_dir / "metadata.json"
            
            if not metadata_file.exists():
                return None
            
            return self._read_json(metadata_file)
            
        except Exception as e:
            logger.error(f"Failed to load metadata for {package_id}/{discovery_folder}: {e}")
            return None
    
    def delete_discovery(self, package_id: str, discovery_folder: str, subfolder: Optional[str] = None) -> bool:
        try:
            discovery_dir = get_discovery_dir(package_id, discovery_folder, subfolder)
            
            if not discovery_dir.exists():
                logger.warning(f"Discovery not found for deletion: {package_id}/{discovery_folder}")
                return False
            
            shutil.rmtree(discovery_dir)
            logger.info(f"Deleted discovery: {package_id}/{discovery_folder}")
            
            package_dir = get_package_discoveries_dir(package_id, subfolder)
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
    
    def _migrate_legacy_discovery(self, discovery_data: Dict[str, Any]) -> Dict[str, Any]:
        metadata = discovery_data.get("metadata") or {}
        java_classes = discovery_data.get("java_classes") or {}
        native_modules = discovery_data.get("native_modules") or {}
        
        format_version = metadata.get("format_version", "1.0")
        
        try:
            version_float = float(format_version)
        except (ValueError, TypeError):
            version_float = 1.0
        
        if version_float >= 1.2:
            return discovery_data
        
        logger.info(f"Migrating legacy discovery from format {format_version} to {FORMAT_VERSION}")
        migrated_classes = 0
        migrated_modules = 0
        
        classes = java_classes.get("classes", [])
        for cls in classes:
            if cls.get("source") == "third_party":
                cls["source"] = "bundled"
                migrated_classes += 1
        
        modules = native_modules.get("modules", [])
        for mod in modules:
            if mod.get("source") == "third_party":
                mod["source"] = "bundled"
                migrated_modules += 1
        
        stats = metadata.get("stats", {})
        
        java_stats = stats.get("java", {})
        if "classes_by_source" in java_stats:
            source_breakdown = java_stats["classes_by_source"]
            if "third_party" in source_breakdown:
                source_breakdown["bundled"] = source_breakdown.pop("third_party")
        
        native_stats = stats.get("native", {})
        if "modules_by_source" in native_stats:
            source_breakdown = native_stats["modules_by_source"]
            if "third_party" in source_breakdown:
                source_breakdown["bundled"] = source_breakdown.pop("third_party")
        
        filtering_stats = stats.get("filtering", {})
        if "source_breakdown" in filtering_stats:
            for category in ["classes", "modules"]:
                breakdown = filtering_stats["source_breakdown"].get(category, {})
                if "third_party" in breakdown:
                    breakdown["bundled"] = breakdown.pop("third_party")
        
        metadata["format_version"] = FORMAT_VERSION
        metadata["is_legacy_classification"] = True
        metadata["classification_notice"] = (
            "Legacy discovery using name-based classification. "
            "Re-run discovery for ClassLoader-based accuracy."
        )
        
        java_classes["format_version"] = FORMAT_VERSION
        native_modules["format_version"] = FORMAT_VERSION
        
        logger.info(
            f"Migration complete: {migrated_classes} classes, {migrated_modules} modules "
            f"converted from third_party to bundled"
        )
        
        return {
            "metadata": metadata,
            "java_classes": java_classes,
            "native_modules": native_modules,
            "user_data": discovery_data.get("user_data")
        }


discovery_store = DiscoveryStore()

