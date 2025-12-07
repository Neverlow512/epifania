# Main discovery orchestrator - two-pass process with progress tracking
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from core.logger import get_logger
from device.workshop_tab.logging.workshop_logger import get_discovery_logger
from device.workshop_tab.discovery.java_discovery import JavaDiscovery
from device.workshop_tab.discovery.native_discovery import NativeDiscovery
from device.workshop_tab.discovery.filter import DiscoveryFilter
from device.workshop_tab.discovery.categorizer import Categorizer
from device.workshop_tab.frida_session.session_manager import frida_session_manager

logger = get_logger(__name__, "backend")


class DiscoveryState:
    IDLE = "idle"
    RUNNING = "running"
    COMPLETE = "complete"
    ERROR = "error"
    CANCELLED = "cancelled"


class DiscoveryProgress:
    def __init__(self):
        self.progress = 0
        self.phase = "idle"
        self.message = ""
        self.count = 0
        self.total = 0


class Discoverer:
    def __init__(self, device_id: str):
        self.device_id = device_id
        self._state = DiscoveryState.IDLE
        self._progress = DiscoveryProgress()
        self._cancelled = False
        self._current_discovery_id: Optional[str] = None
        self._result: Optional[Dict[str, Any]] = None
        self._error: Optional[str] = None
        self._timestamp: Optional[str] = None
    
    def get_state(self) -> str:
        return self._state
    
    def get_progress(self) -> Dict[str, Any]:
        return {
            "progress": self._progress.progress,
            "phase": self._progress.phase,
            "message": self._progress.message,
            "count": self._progress.count,
            "total": self._progress.total,
            "state": self._state
        }
    
    def cancel(self):
        self._cancelled = True
        self._state = DiscoveryState.CANCELLED
        logger.info(f"Discovery cancelled for device {self.device_id}")
    
    async def discover(
        self,
        package_id: str,
        pid: int,
        include_system_libs: bool = False,
        package_info: Dict[str, Any] = None,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> Dict[str, Any]:
        self._state = DiscoveryState.RUNNING
        self._cancelled = False
        self._timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._current_discovery_id = f"{package_id}_{self._timestamp}"
        
        discovery_logger = get_discovery_logger(package_id, self._timestamp)
        discovery_logger.info(f"Starting discovery for {package_id} (PID: {pid})")
        discovery_logger.info(f"Include system libs: {include_system_libs}")
        
        def update_progress(progress: int, phase: str, message: str, count: int = 0, total: int = 0):
            self._progress.progress = progress
            self._progress.phase = phase
            self._progress.message = message
            self._progress.count = count
            self._progress.total = total
            
            if progress_callback:
                progress_callback(self.get_progress())
        
        try:
            # Phase 1: Attach to process (0-5%)
            update_progress(0, "attaching", "Attaching to process...")
            
            session = frida_session_manager.get_session(self.device_id)
            if not session:
                attach_result = frida_session_manager.attach(self.device_id, pid)
                if not attach_result.get("success"):
                    raise Exception(f"Failed to attach: {attach_result.get('message')}")
                session = frida_session_manager.get_session(self.device_id)
            
            if not session:
                raise Exception("Could not obtain Frida session")
            
            update_progress(5, "attached", "Attached to process")
            discovery_logger.info("Attached to process")
            
            if self._cancelled:
                return self._build_cancelled_result()
            
            # Phase 2: Enumerate Java classes (5-25%)
            update_progress(5, "java_enum", "Enumerating Java classes...")
            
            java_discovery = JavaDiscovery(session, package_id, self._timestamp)
            
            def java_class_progress(count, status):
                pct = min(5 + int((count / max(count, 1)) * 20), 25)
                update_progress(pct, "java_enum", f"Found {count} classes", count)
            
            all_classes = java_discovery.enumerate_classes(java_class_progress)
            discovery_logger.info(f"Enumerated {len(all_classes)} Java classes")
            
            if self._cancelled:
                return self._build_cancelled_result()
            
            # Phase 3: Enumerate Java methods (25-40%)
            update_progress(25, "java_methods", "Enumerating Java methods...")
            
            discovery_filter = DiscoveryFilter(package_id, include_system_libs)
            
            filtered_classes = []
            for class_name in all_classes:
                if discovery_filter.should_include_class(class_name)[0]:
                    filtered_classes.append(class_name)
            
            discovery_logger.info(f"Filtered to {len(filtered_classes)} classes for method enumeration")
            
            def java_method_progress(current, total, class_name):
                pct = 25 + int((current / max(total, 1)) * 15)
                update_progress(pct, "java_methods", f"Processing {class_name}", current, total)
            
            class_data = java_discovery.enumerate_methods(filtered_classes, java_method_progress)
            
            for cls in class_data:
                discovery_filter.filter_class(cls["name"], cls)
            
            if self._cancelled:
                return self._build_cancelled_result()
            
            # Phase 4: Categorize Java classes (40-55%)
            update_progress(40, "java_categorize", "Categorizing Java classes...")
            
            categorizer = Categorizer(package_id, self._timestamp)
            categorized_classes = categorizer.categorize_classes_batch(discovery_filter.included_classes)
            
            update_progress(55, "java_complete", f"Categorized {len(categorized_classes)} classes")
            discovery_logger.info(f"Categorized {len(categorized_classes)} Java classes")
            
            if self._cancelled:
                return self._build_cancelled_result()
            
            # Phase 5: Enumerate native modules (55-70%)
            update_progress(55, "native_enum", "Enumerating native modules...")
            
            native_discovery = NativeDiscovery(session, package_id, self._timestamp)
            
            def native_module_progress(count, status):
                pct = min(55 + int((count / max(count, 1)) * 15), 70)
                update_progress(pct, "native_enum", f"Found {count} modules", count)
            
            all_modules = native_discovery.enumerate_modules(native_module_progress)
            discovery_logger.info(f"Enumerated {len(all_modules)} native modules")
            
            if self._cancelled:
                return self._build_cancelled_result()
            
            # Phase 6: Filter and enumerate exports (70-85%)
            update_progress(70, "native_exports", "Enumerating native exports...")
            
            filtered_modules = []
            for module in all_modules:
                if discovery_filter.should_include_module(module["name"], module["path"])[0]:
                    filtered_modules.append(module)
                    discovery_filter.filter_module(module["name"], module, module["path"])
            
            def native_export_progress(current, total, module_name):
                pct = 70 + int((current / max(total, 1)) * 15)
                update_progress(pct, "native_exports", f"Processing {module_name}", current, total)
            
            modules_with_exports = native_discovery.enumerate_exports(
                discovery_filter.included_modules,
                native_export_progress
            )
            
            if self._cancelled:
                return self._build_cancelled_result()
            
            # Phase 7: Categorize native exports (85-90%)
            update_progress(85, "native_categorize", "Categorizing native exports...")
            
            categorized_modules = categorizer.categorize_exports_batch(modules_with_exports)
            
            update_progress(90, "native_complete", f"Processed {len(categorized_modules)} modules")
            discovery_logger.info(f"Processed {len(categorized_modules)} native modules")
            
            # Phase 8: Build final result (90-100%)
            update_progress(90, "finalizing", "Building final result...")
            
            verification_stats = discovery_filter.get_verification_stats()
            categorizer_stats = categorizer.get_stats()
            java_stats = java_discovery.get_stats()
            native_stats = native_discovery.get_stats()
            
            metadata = {
                "package_id": package_id,
                "package_name": package_info.get("name", package_id) if package_info else package_id,
                "package_version": package_info.get("version", "unknown") if package_info else "unknown",
                "version_code": package_info.get("version_code") if package_info else None,
                "discovery_timestamp": datetime.now().isoformat(),
                "device_serial": self.device_id,
                "device_model": package_info.get("device_model") if package_info else None,
                "android_version": package_info.get("android_version") if package_info else None,
                "pid": pid,
                "stats": {
                    **verification_stats,
                    "total_methods": java_stats["total_methods"],
                    "categorized_classes": categorizer_stats["total_categorized"],
                    "unknown_classes": categorizer_stats["unknown"],
                    "total_native_exports": native_stats["total_exports"]
                },
                "verification": verification_stats["verification"]
            }
            
            java_classes_result = {
                "classes": categorized_classes
            }
            
            native_modules_result = {
                "modules": categorized_modules
            }
            
            self._result = {
                "metadata": metadata,
                "java_classes": java_classes_result,
                "native_modules": native_modules_result,
                "errors": {
                    "java": java_discovery.get_errors(),
                    "native": native_discovery.get_errors()
                }
            }
            
            self._state = DiscoveryState.COMPLETE
            update_progress(100, "complete", "Discovery complete")
            discovery_logger.info("Discovery completed successfully")
            discovery_logger.info(f"Final stats: {metadata['stats']}")
            
            return self._result
            
        except Exception as e:
            self._state = DiscoveryState.ERROR
            self._error = str(e)
            discovery_logger.error(f"Discovery failed: {e}")
            logger.error(f"Discovery failed for {package_id}: {e}")
            
            update_progress(0, "error", str(e))
            
            return {
                "success": False,
                "error": str(e),
                "state": DiscoveryState.ERROR
            }
    
    def _build_cancelled_result(self) -> Dict[str, Any]:
        return {
            "success": False,
            "error": "Discovery cancelled by user",
            "state": DiscoveryState.CANCELLED
        }
    
    def get_result(self) -> Optional[Dict[str, Any]]:
        return self._result
    
    def get_error(self) -> Optional[str]:
        return self._error


# Active discoveries per device
_active_discoveries: Dict[str, Discoverer] = {}


def get_discoverer(device_id: str) -> Discoverer:
    if device_id not in _active_discoveries:
        _active_discoveries[device_id] = Discoverer(device_id)
    return _active_discoveries[device_id]


def cancel_discovery(device_id: str) -> bool:
    if device_id in _active_discoveries:
        _active_discoveries[device_id].cancel()
        return True
    return False


def get_discovery_status(device_id: str) -> Optional[Dict[str, Any]]:
    if device_id in _active_discoveries:
        return _active_discoveries[device_id].get_progress()
    return None

