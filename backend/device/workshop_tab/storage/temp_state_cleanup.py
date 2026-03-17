import json
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any
from core.logger import get_logger
from device.workshop_tab.storage.cleanup_config import cleanup_config_manager

logger = get_logger(__name__, "backend")

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
WORKSHOP_TEMP_DIR = PROJECT_ROOT / "local_storage" / "temp_discoveries"


class TempStateCleanup:
    def __init__(self):
        pass
    
    def cleanup_old_temp_states(self, package_id: Optional[str] = None):
        if package_id:
            self._cleanup_package(package_id)
        else:
            self._cleanup_all_packages()
    
    def _cleanup_all_packages(self):
        if not WORKSHOP_TEMP_DIR.exists():
            logger.info("No temp states directory found, skipping cleanup")
            return
        
        processed_packages = set()
        for device_dir in WORKSHOP_TEMP_DIR.iterdir():
            if not device_dir.is_dir():
                continue
            for pkg_dir in device_dir.iterdir():
                if not pkg_dir.is_dir():
                    continue
                package_id = pkg_dir.name.replace("_", ".")
                if package_id not in processed_packages:
                    processed_packages.add(package_id)
                    try:
                        self._cleanup_package(package_id)
                    except Exception as e:
                        logger.error(f"Failed to cleanup package {package_id}: {e}")
    
    def _cleanup_package(self, package_id: str):
        retention_limit = cleanup_config_manager.get_retention_limit(package_id)
        unsaved_temp_count = self._count_unsaved_temps(package_id)
        effective_limit = max(retention_limit, unsaved_temp_count)
        
        saved_temps = self._get_saved_temp_states(package_id)
        
        if len(saved_temps) <= effective_limit:
            return
        
        saved_temps.sort(key=lambda x: x["mtime"], reverse=True)
        
        to_keep = saved_temps[:effective_limit]
        to_delete = saved_temps[effective_limit:]
        
        deleted_count = 0
        for temp_state in to_delete:
            try:
                shutil.rmtree(temp_state["path"])
                deleted_count += 1
                logger.debug(f"Deleted temp state: {temp_state['path']}")
            except Exception as e:
                logger.error(f"Failed to delete temp state {temp_state['path']}: {e}")
        
        if deleted_count > 0:
            logger.info(f"Cleanup: {package_id} - Kept {len(to_keep)}, Deleted {deleted_count} (retention: {retention_limit}, unsaved temps: {unsaved_temp_count})")
    
    def _get_saved_temp_states(self, package_id: str) -> List[Dict[str, Any]]:
        if not WORKSHOP_TEMP_DIR.exists():
            return []
        
        saved_temps = []
        safe_package = package_id.replace(".", "_")
        
        for device_dir in WORKSHOP_TEMP_DIR.iterdir():
            if not device_dir.is_dir():
                continue
            
            pkg_dir = device_dir / safe_package
            if not pkg_dir.is_dir():
                continue
            
            current_dir = pkg_dir / "current"
            if not current_dir.exists():
                continue
            
            checkpoint_file = current_dir / "checkpoint_info.json"
            if not checkpoint_file.exists():
                continue
            
            try:
                with open(checkpoint_file, 'r') as f:
                    checkpoint = json.load(f)
                
                if checkpoint.get("last_saved_folder"):
                    saved_temps.append({
                        "path": current_dir,
                        "device": device_dir.name,
                        "mtime": current_dir.stat().st_mtime,
                        "last_saved": checkpoint.get("last_saved_folder")
                    })
            except Exception as e:
                logger.warning(f"Failed to read checkpoint for {package_id} in {device_dir.name}: {e}")
        
        return saved_temps
    
    def _count_unsaved_temps(self, package_id: str) -> int:
        if not WORKSHOP_TEMP_DIR.exists():
            return 0
        
        unsaved_count = 0
        
        for device_dir in WORKSHOP_TEMP_DIR.iterdir():
            if not device_dir.is_dir():
                continue
            
            for pkg_dir in device_dir.iterdir():
                if not pkg_dir.is_dir():
                    continue
                
                safe_package = package_id.replace(".", "_")
                if pkg_dir.name != safe_package:
                    continue
                
                current_dir = pkg_dir / "current"
                if not current_dir.exists():
                    continue
                
                checkpoint_file = current_dir / "checkpoint_info.json"
                if not checkpoint_file.exists():
                    unsaved_count += 1
                    continue
                
                try:
                    with open(checkpoint_file, 'r') as f:
                        checkpoint = json.load(f)
                    
                    if not checkpoint.get("last_saved_folder"):
                        unsaved_count += 1
                except Exception as e:
                    logger.warning(f"Failed to read checkpoint for {package_id}: {e}")
                    unsaved_count += 1
        
        return unsaved_count


temp_state_cleanup = TempStateCleanup()
