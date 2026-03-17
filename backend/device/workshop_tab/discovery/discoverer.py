# Main discovery orchestrator - two-pass process with progress tracking
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, Callable, List
from core.logger import get_logger
from device.workshop_tab.logging.workshop_logger import get_discovery_logger
from device.workshop_tab.logging.aggregated_frida_logger import aggregated_frida_logger
from device.workshop_tab.discovery.java_discovery import JavaDiscovery
from device.workshop_tab.discovery.native_discovery import NativeDiscovery
from device.workshop_tab.discovery.filter import DiscoveryFilter, FilterMode
from device.workshop_tab.discovery.categorizer import Categorizer
from device.workshop_tab.frida_session.session_manager import frida_session_manager
from device.workshop_tab.storage.temp_state_manager import temp_state_manager
from device.workshop_tab.config.app_focused_manager import app_focused_manager

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
        self._run_id: Optional[str] = None
    
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
        self.reset()
    
    def reset(self):
        self._state = DiscoveryState.IDLE
        self._result = None
        self._error = None
        self._progress = DiscoveryProgress()
        self._current_discovery_id = None
        self._timestamp = None
        self._run_id = None
        self._cancelled = False
        logger.info(f"Discovery state reset for device {self.device_id}")
    
    async def discover(
        self,
        package_id: str,
        pid: int,
        filter_mode: FilterMode = FilterMode.FOCUSED,
        package_info: Dict[str, Any] = None,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        app_focused_patterns: List[str] = None
    ) -> Dict[str, Any]:
        # Clear any cached results from previous discoveries
        self._result = None
        self._error = None
        
        self._state = DiscoveryState.RUNNING
        self._cancelled = False
        self._timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._current_discovery_id = f"{package_id}_{self._timestamp}"
        
        # Generate unique run_id for this discovery session
        self._run_id = temp_state_manager.generate_run_id(package_id)
        
        discovery_logger = get_discovery_logger(package_id, self._timestamp)
        discovery_logger.info(f"Starting discovery for {package_id} (PID: {pid})")
        discovery_logger.info(f"Filter mode: {filter_mode.value}")
        
        # Get session number for aggregated logging
        session_info = frida_session_manager._sessions.get(self.device_id)
        session_number = session_info.get("session_number") if session_info else None
        
        def update_progress(progress: int, phase: str, message: str, count: int = 0, total: int = 0):
            self._progress.progress = progress
            self._progress.phase = phase
            self._progress.message = message
            self._progress.count = count
            self._progress.total = total
            
            if progress_callback:
                progress_callback(self.get_progress())
        
        try:
            # Log discovery start to aggregated logger
            if session_number:
                aggregated_frida_logger.log_discovery_start(session_number, package_id, pid, filter_mode.value)
            
            # Phase 1: Attach to process (0-5%)
            update_progress(0, "attaching", "Attaching to process...")
            if session_number:
                aggregated_frida_logger.log_discovery_phase(session_number, "Attaching", "Connecting to process", 0)
            
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
            if session_number:
                aggregated_frida_logger.log_discovery_phase(session_number, "Attached", "Process attached successfully", 5)
            
            if self._cancelled:
                if session_number:
                    aggregated_frida_logger.log_discovery_cancelled(session_number, "User cancelled", "attaching")
                return self._build_cancelled_result()
            
            # Phase 2: Enumerate Java classes (5-25%)
            update_progress(5, "java_enum", "Enumerating Java classes...")
            if session_number:
                aggregated_frida_logger.log_discovery_phase(session_number, "Java Enumeration", "Discovering loaded classes", 5)
            
            java_discovery = JavaDiscovery(session, package_id, self._timestamp)
            
            def java_class_progress(count, status):
                pct = min(5 + int((count / max(count, 1)) * 20), 25)
                update_progress(pct, "java_enum", f"Found {count} classes", count)
            
            all_classes = java_discovery.enumerate_classes(java_class_progress)
            total_classes_found = len(all_classes)
            discovery_logger.info(f"Enumerated {total_classes_found} Java classes (raw)")
            if session_number:
                aggregated_frida_logger.log_discovery_phase(session_number, "Java Enumeration", f"Found {total_classes_found} classes", 25)
            
            if self._cancelled:
                if session_number:
                    aggregated_frida_logger.log_discovery_cancelled(session_number, "User cancelled", "java_enumeration")
                return self._build_cancelled_result()
            
            # Phase 3: Filter classes (25-40%) - LAZY: no method extraction
            update_progress(25, "java_filter", "Filtering Java classes...")
            if session_number:
                aggregated_frida_logger.log_discovery_phase(session_number, "Java Filtering", "Applying filter rules", 25)
            
            # Load App Focused patterns from saved config if not provided
            if app_focused_patterns is None and filter_mode == FilterMode.FOCUSED:
                config = app_focused_manager.get_config(package_id)
                app_focused_patterns = config.get("patterns")
                discovery_logger.info(f"Loaded App Focused patterns from config: {app_focused_patterns}")
            
            discovery_filter = DiscoveryFilter(package_id, filter_mode, app_focused_patterns)
            
            # Filter classes by name only (lazy discovery - no ClassLoader info yet)
            filtered_classes = []
            
            for class_name in all_classes:
                include, reason = discovery_filter.should_include_class(class_name)
                
                if include:
                    filtered_classes.append(class_name)
                else:
                    discovery_filter.skipped_classes.append({
                        "name": class_name,
                        "reason": reason
                    })
            
            # Track total counts for accurate statistics
            discovery_filter.set_total_counts(total_classes_found, 0)
            
            discovery_logger.info(f"Filtered to {len(filtered_classes)} classes (skipped {len(discovery_filter.skipped_classes)})")
            if session_number:
                aggregated_frida_logger.log_discovery_phase(session_number, "Java Filtering", f"Filtered to {len(filtered_classes)} classes", 40)
            
            # LAZY DISCOVERY: Create class entries WITHOUT methods
            # Methods will be extracted on-demand via /extract-methods endpoint
            class_data = []
            for class_name in filtered_classes:
                class_data.append({
                    "name": class_name,
                    "method_count": 0,
                    "methods": [],
                    "scanned": False,
                    "extracted": False,
                    "extraction_status": "pending",
                    "is_from_apk": False,
                    "loader_type": None
                })
            
            # Apply filter metadata to each class
            for cls in class_data:
                class_name = cls["name"]
                discovery_filter.filter_class(class_name, cls)
            
            update_progress(40, "java_filter_done", f"Filtered {len(filtered_classes)} classes")
            
            if self._cancelled:
                if session_number:
                    aggregated_frida_logger.log_discovery_cancelled(session_number, "User cancelled", "java_filtering")
                return self._build_cancelled_result()
            
            # Phase 4: Categorize Java classes (40-55%) - LAZY: no methods yet
            update_progress(40, "java_categorize", "Categorizing Java classes...")
            if session_number:
                aggregated_frida_logger.log_discovery_phase(session_number, "Java Categorization", "Categorizing classes", 40)
            
            categorizer = Categorizer(package_id, self._timestamp)
            categorized_classes = categorizer.categorize_classes_batch(discovery_filter.included_classes)
            
            update_progress(55, "java_complete", f"Categorized {len(categorized_classes)} classes (methods not extracted)")
            discovery_logger.info(f"Categorized {len(categorized_classes)} Java classes (lazy mode - no methods)")
            if session_number:
                aggregated_frida_logger.log_discovery_phase(session_number, "Java Complete", f"Categorized {len(categorized_classes)} classes", 55)
            
            if self._cancelled:
                if session_number:
                    aggregated_frida_logger.log_discovery_cancelled(session_number, "User cancelled", "java_categorization")
                return self._build_cancelled_result()
            
            # Phase 5: Enumerate native modules (55-70%)
            update_progress(55, "native_enum", "Enumerating native modules...")
            if session_number:
                aggregated_frida_logger.log_discovery_phase(session_number, "Native Enumeration", "Discovering native modules", 55)
            
            native_discovery = NativeDiscovery(session, package_id, self._timestamp)
            
            def native_module_progress(count, status):
                pct = min(55 + int((count / max(count, 1)) * 15), 70)
                update_progress(pct, "native_enum", f"Found {count} modules", count)
            
            all_modules = native_discovery.enumerate_modules(native_module_progress)
            total_modules_found = len(all_modules)
            discovery_logger.info(f"Enumerated {total_modules_found} native modules (raw)")
            if session_number:
                aggregated_frida_logger.log_discovery_phase(session_number, "Native Enumeration", f"Found {total_modules_found} modules", 70)
            
            if self._cancelled:
                if session_number:
                    aggregated_frida_logger.log_discovery_cancelled(session_number, "User cancelled", "native_enumeration")
                return self._build_cancelled_result()
            
            # Phase 6: Filter and enumerate exports (70-85%)
            update_progress(70, "native_exports", "Filtering and enumerating native exports...")
            if session_number:
                aggregated_frida_logger.log_discovery_phase(session_number, "Native Filtering", "Filtering modules and exports", 70)
            
            # Filter modules and track what was skipped
            filtered_modules = []
            for module in all_modules:
                include, reason = discovery_filter.should_include_module(module["name"], module["path"])
                if include:
                    filtered_modules.append(module)
                    discovery_filter.filter_module(module["name"], module, module["path"])
                else:
                    discovery_filter.skipped_modules.append({
                        "name": module["name"],
                        "path": module["path"],
                        "reason": reason
                    })
            
            # Update module count
            discovery_filter.set_total_counts(total_classes_found, total_modules_found)
            
            discovery_logger.info(f"Filtered to {len(filtered_modules)} modules (skipped {len(discovery_filter.skipped_modules)})")
            
            def native_export_progress(current, total, module_name):
                pct = 70 + int((current / max(total, 1)) * 15)
                update_progress(pct, "native_exports", f"Processing {module_name}", current, total)
            
            modules_with_exports = native_discovery.enumerate_exports(
                discovery_filter.included_modules,
                native_export_progress
            )
            
            if self._cancelled:
                if session_number:
                    aggregated_frida_logger.log_discovery_cancelled(session_number, "User cancelled", "native_exports")
                return self._build_cancelled_result()
            
            # Phase 7: Categorize native modules and exports (85-90%)
            update_progress(85, "native_categorize", "Categorizing native modules and exports...")
            if session_number:
                aggregated_frida_logger.log_discovery_phase(session_number, "Native Categorization", "Categorizing modules", 85)
            
            categorized_modules = categorizer.categorize_modules_batch(modules_with_exports)
            
            update_progress(90, "native_complete", f"Processed {len(categorized_modules)} modules")
            discovery_logger.info(f"Processed {len(categorized_modules)} native modules with exports")
            if session_number:
                aggregated_frida_logger.log_discovery_phase(session_number, "Native Complete", f"Processed {len(categorized_modules)} modules", 90)
            
            # Phase 8: Build final result (90-100%)
            update_progress(90, "finalizing", "Building final result...")
            if session_number:
                aggregated_frida_logger.log_discovery_phase(session_number, "Finalizing", "Building discovery results", 90)
            
            verification_stats = discovery_filter.get_verification_stats()
            categorizer_stats = categorizer.get_stats()
            java_stats = java_discovery.get_stats()
            native_stats = native_discovery.get_stats()
            
            install_markers = package_info.get("install_markers") if package_info else None
            
            metadata = {
                "package_id": package_id,
                "package_name": package_info.get("name", package_id) if package_info else package_id,
                "package_version": install_markers.get("version", "unknown") if install_markers else (package_info.get("version", "unknown") if package_info else "unknown"),
                "version_code": install_markers.get("version_code") if install_markers else (package_info.get("version_code") if package_info else None),
                "discovery_timestamp": datetime.now().isoformat(),
                "timestamp": self._timestamp,
                "run_id": self._run_id,
                "device_serial": self.device_id,
                "device_model": package_info.get("device_model") if package_info else None,
                "android_version": package_info.get("android_version") if package_info else None,
                "pid": pid,
                "install_markers": install_markers,
                "lazy_mode": True,
                "stats": {
                    "java": {
                        "total_classes_found": verification_stats["total_classes_found"],
                        "classes_included": verification_stats["classes_included"],
                        "classes_skipped": verification_stats["classes_skipped"],
                        "classes_by_category": categorizer_stats["classes"]["by_category"],
                        "classes_by_source": verification_stats["source_breakdown"]["classes"],
                        "obfuscated_classes": categorizer_stats["classes"]["obfuscated"],
                        "total_methods": categorizer_stats["methods"]["total"],
                        "methods_by_category": categorizer_stats["methods"]["by_category"],
                        "methods_by_confidence": categorizer_stats["methods"]["by_confidence"]
                    },
                    "native": {
                        "total_modules_found": verification_stats["total_modules_found"],
                        "modules_included": verification_stats["modules_included"],
                        "modules_skipped": verification_stats["modules_skipped"],
                        "modules_by_category": categorizer_stats["modules"]["by_category"],
                        "modules_by_source": verification_stats["source_breakdown"]["modules"],
                        "total_exports": categorizer_stats["exports"]["total"],
                        "exports_by_category": categorizer_stats["exports"]["by_category"],
                        "exports_by_confidence": categorizer_stats["exports"]["by_confidence"]
                    },
                    "filtering": {
                        "filter_mode": verification_stats["filter_mode"],
                        "source_breakdown": verification_stats["source_breakdown"]
                    }
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
            
            # Log discovery completion to aggregated logger
            if session_number:
                discovery_stats = {
                    "total_classes": verification_stats["classes_included"],
                    "total_methods": categorizer_stats["methods"]["total"],
                    "duration": 0
                }
                aggregated_frida_logger.log_discovery_complete(session_number, discovery_stats)
            
            # Create initial temp state for crash recovery and auto-save
            try:
                temp_state_manager.create_temp_state(
                    self.device_id,
                    package_id,
                    metadata,
                    java_classes_result,
                    native_modules_result
                )
                logger.info(f"Created temp state for {package_id} with run_id: {self._run_id}")
            except Exception as e:
                logger.error(f"Failed to create temp state: {e}")
                # Non-fatal - discovery still succeeds
            
            return self._result
            
        except Exception as e:
            self._state = DiscoveryState.ERROR
            self._error = str(e)
            discovery_logger.error(f"Discovery failed: {e}")
            logger.error(f"Discovery failed for {package_id}: {e}")
            
            # Log discovery error to aggregated logger
            if session_number:
                aggregated_frida_logger.log_error(session_number, "discovery", str(e))
            
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
    
    def get_run_id(self) -> Optional[str]:
        return self._run_id


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


def reset_discovery(device_id: str) -> bool:
    if device_id in _active_discoveries:
        _active_discoveries[device_id].reset()
        return True
    return False
