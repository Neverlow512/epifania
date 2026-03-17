# Temp state manager - auto-save persistence for lazy discovery
import json
import shutil
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
from core.logger import get_logger

logger = get_logger(__name__, "backend")

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
WORKSHOP_TEMP_DIR = PROJECT_ROOT / "local_storage" / "temp_discoveries"


class TempStateManager:
    def __init__(self):
        self._locks = {}
        self._global_lock = threading.Lock()
        WORKSHOP_TEMP_DIR.mkdir(parents=True, exist_ok=True)
        logger.info("TempStateManager initialized")
    
    def _get_lock(self, device_id: str, package_id: str) -> threading.Lock:
        """Get or create a lock for this device+package session"""
        key = f"{device_id}_{package_id}"
        with self._global_lock:
            if key not in self._locks:
                self._locks[key] = threading.Lock()
            return self._locks[key]
    
    def _get_temp_dir(self, device_id: str, package_id: str) -> Path:
        """Get temp directory path for device+package"""
        safe_device = device_id.replace(":", "_").replace(".", "_")
        safe_package = package_id.replace(".", "_")
        return WORKSHOP_TEMP_DIR / safe_device / safe_package / "current"
    
    def generate_run_id(self, package_id: str) -> str:
        """Generate unique run identifier"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        short_uuid = uuid.uuid4().hex[:6]
        return f"{package_id}_{timestamp}_{short_uuid}"
    
    def create_temp_state(
        self,
        device_id: str,
        package_id: str,
        metadata: Dict[str, Any],
        java_classes: Dict[str, Any],
        native_modules: Dict[str, Any]
    ) -> bool:
        """Create initial temp state after discovery"""
        lock = self._get_lock(device_id, package_id)
        
        try:
            logger.info(f"[AUTO-SAVE] Creating initial temp state for {device_id}/{package_id}")
            
            with lock:
                temp_dir = self._get_temp_dir(device_id, package_id)
                temp_dir.mkdir(parents=True, exist_ok=True)
                
                # Generate run_id if not present
                if "run_id" not in metadata:
                    metadata["run_id"] = self.generate_run_id(package_id)
                
                # Save metadata
                metadata_file = temp_dir / "metadata.json"
                with open(metadata_file, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                # Save java classes
                java_file = temp_dir / "java_classes.json"
                with open(java_file, 'w') as f:
                    json.dump(java_classes, f, indent=2)
                
                # Save native modules
                native_file = temp_dir / "native_modules.json"
                with open(native_file, 'w') as f:
                    json.dump(native_modules, f, indent=2)
                
                # Initialize empty state
                state_file = temp_dir / "state.json"
                with open(state_file, 'w') as f:
                    json.dump({"class_states": {}}, f, indent=2)
                
                # Initialize checkpoint info
                checkpoint_file = temp_dir / "checkpoint_info.json"
                with open(checkpoint_file, 'w') as f:
                    json.dump({
                        "last_saved_folder": None,
                        "last_saved_timestamp": None,
                        "created_timestamp": datetime.now().isoformat()
                    }, f, indent=2)
                
                logger.info(f"[AUTO-SAVE] Created temp state for {device_id}/{package_id} at {temp_dir}")
                logger.debug(f"[AUTO-SAVE] Run ID: {metadata.get('run_id')}")
                logger.debug(f"[AUTO-SAVE] Classes: {len(java_classes.get('classes', []))}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to create temp state for {device_id}/{package_id}: {e}")
            return False
    
    def save_temp_state(
        self,
        device_id: str,
        package_id: str,
        class_states: Dict[str, Any],
        full_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update temp state (auto-save trigger)"""
        lock = self._get_lock(device_id, package_id)
        
        try:
            logger.debug(f"[AUTO-SAVE] Starting save for {device_id}/{package_id} - {len(class_states)} class(es)")
            
            with lock:
                temp_dir = self._get_temp_dir(device_id, package_id)
                
                if not temp_dir.exists():
                    logger.warning(f"Temp state doesn't exist for {device_id}/{package_id}")
                    return False
                
                # Load existing state and merge with new class states
                state_file = temp_dir / "state.json"
                existing_states = {}
                if state_file.exists():
                    try:
                        with open(state_file, 'r') as f:
                            existing_data = json.load(f)
                            existing_states = existing_data.get("class_states", {})
                    except Exception as e:
                        logger.warning(f"Failed to load existing state for merge: {e}")
                
                # Merge new states with existing (preserve all fields)
                merged_count = 0
                new_count = 0
                for class_name, new_state in class_states.items():
                    if class_name in existing_states:
                        # Merge: keep existing fields and update with new ones
                        existing_states[class_name].update(new_state)
                        merged_count += 1
                        logger.debug(f"[AUTO-SAVE] Merged state for: {class_name}")
                    else:
                        # New class, add it
                        existing_states[class_name] = new_state
                        new_count += 1
                        logger.debug(f"[AUTO-SAVE] New state for: {class_name}")
                
                logger.info(f"[AUTO-SAVE] Merged {merged_count} existing, added {new_count} new class states")
                
                # Write merged state back
                with open(state_file, 'w') as f:
                    json.dump({
                        "class_states": existing_states,
                        "last_updated": datetime.now().isoformat()
                    }, f, indent=2)
                
                # Update full data if provided
                if full_data:
                    if "java_classes" in full_data:
                        java_file = temp_dir / "java_classes.json"
                        with open(java_file, 'w') as f:
                            json.dump(full_data["java_classes"], f, indent=2)
                    
                    if "native_modules" in full_data:
                        native_file = temp_dir / "native_modules.json"
                        with open(native_file, 'w') as f:
                            json.dump(full_data["native_modules"], f, indent=2)
                        logger.debug(f"[AUTO-SAVE] Updated native_modules.json")
                
                logger.info(f"[AUTO-SAVE] Successfully saved temp state for {device_id}/{package_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to save temp state for {device_id}/{package_id}: {e}")
            return False
    
    def load_temp_state(self, device_id: str, package_id: str) -> Optional[Dict[str, Any]]:
        """Load existing temp state"""
        lock = self._get_lock(device_id, package_id)
        
        try:
            logger.debug(f"[AUTO-SAVE] Loading temp state for {device_id}/{package_id}")
            
            with lock:
                temp_dir = self._get_temp_dir(device_id, package_id)
                
                if not temp_dir.exists():
                    return None
                
                # Load all files
                result = {}
                
                metadata_file = temp_dir / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        result["metadata"] = json.load(f)
                
                java_file = temp_dir / "java_classes.json"
                if java_file.exists():
                    with open(java_file, 'r') as f:
                        result["java_classes"] = json.load(f)
                
                native_file = temp_dir / "native_modules.json"
                if native_file.exists():
                    with open(native_file, 'r') as f:
                        result["native_modules"] = json.load(f)
                
                state_file = temp_dir / "state.json"
                if state_file.exists():
                    with open(state_file, 'r') as f:
                        result["state"] = json.load(f)
                
                checkpoint_file = temp_dir / "checkpoint_info.json"
                if checkpoint_file.exists():
                        with open(checkpoint_file, 'r') as f:
                            result["checkpoint_info"] = json.load(f)
                
                logger.info(f"[AUTO-SAVE] Loaded temp state for {device_id}/{package_id}")
                logger.debug(f"[AUTO-SAVE] Loaded {len(result.get('state', {}).get('class_states', {}))} class states")
                return result
                
        except Exception as e:
            logger.error(f"Failed to load temp state for {device_id}/{package_id}: {e}")
            return None
    
    def get_recoverable_states(self, device_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Find temp states available for recovery"""
        recoverable = []
        
        try:
            if not WORKSHOP_TEMP_DIR.exists():
                return recoverable
            
            # Scan for temp directories
            if device_id:
                safe_device = device_id.replace(":", "_").replace(".", "_")
                device_dir = WORKSHOP_TEMP_DIR / safe_device
                if device_dir.exists():
                    search_dirs = [device_dir]
                else:
                    search_dirs = []
            else:
                search_dirs = [d for d in WORKSHOP_TEMP_DIR.iterdir() if d.is_dir()]
            
            for device_dir in search_dirs:
                for package_dir in device_dir.iterdir():
                    if not package_dir.is_dir():
                        continue
                    
                    current_dir = package_dir / "current"
                    if not current_dir.exists():
                        continue
                    
                    metadata_file = current_dir / "metadata.json"
                    if not metadata_file.exists():
                        continue
                    
                    try:
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                        
                        recoverable.append({
                            "device_id": device_dir.name.replace("_", ":", 1).replace("_", "."),
                            "package_id": metadata.get("package_id", "unknown"),
                            "run_id": metadata.get("run_id"),
                            "timestamp": metadata.get("timestamp"),
                            "path": str(current_dir)
                        })
                    except Exception as e:
                        logger.warning(f"Failed to read temp metadata from {current_dir}: {e}")
            
            return recoverable
            
        except Exception as e:
            logger.error(f"Failed to get recoverable states: {e}")
            return []
    
    def clear_temp_state(self, device_id: str, package_id: str) -> bool:
        """Delete temp directory"""
        lock = self._get_lock(device_id, package_id)
        
        try:
            logger.info(f"[AUTO-SAVE] Clearing temp state for {device_id}/{package_id}")
            
            with lock:
                temp_dir = self._get_temp_dir(device_id, package_id)
                
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
                    logger.info(f"[AUTO-SAVE] Cleared temp state at: {temp_dir}")
                    return True
                
                logger.warning(f"[AUTO-SAVE] No temp state to clear for {device_id}/{package_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to clear temp state for {device_id}/{package_id}: {e}")
            return False
    
    def mark_as_saved(self, device_id: str, package_id: str, saved_folder: str) -> bool:
        """Update checkpoint info after manual save"""
        lock = self._get_lock(device_id, package_id)
        
        try:
            logger.info(f"[AUTO-SAVE] Marking temp state as saved to: {saved_folder}")
            
            with lock:
                temp_dir = self._get_temp_dir(device_id, package_id)
                
                if not temp_dir.exists():
                    logger.warning(f"Temp state doesn't exist for {device_id}/{package_id}")
                    return False
                
                checkpoint_file = temp_dir / "checkpoint_info.json"
                
                # Load existing or create new
                checkpoint_info = {}
                if checkpoint_file.exists():
                    with open(checkpoint_file, 'r') as f:
                        checkpoint_info = json.load(f)
                
                # Update with save info
                checkpoint_info["last_saved_folder"] = saved_folder
                checkpoint_info["last_saved_timestamp"] = datetime.now().isoformat()
                
                # Save updated checkpoint
                with open(checkpoint_file, 'w') as f:
                    json.dump(checkpoint_info, f, indent=2)
                
                logger.info(f"[AUTO-SAVE] Checkpoint updated - saved to: {saved_folder}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to mark temp as saved for {device_id}/{package_id}: {e}")
            return False


# Global instance
temp_state_manager = TempStateManager()
