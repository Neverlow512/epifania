# Workshop tab API endpoints
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import asyncio
from core.device_manager import DeviceManager
from core.logger import get_logger
from device.workshop_tab.session.workshop_session import workshop_session
from device.workshop_tab.frida_session.session_manager import frida_session_manager
from device.workshop_tab.config.rules_manager import rules_manager
from device.workshop_tab.config.app_focused_manager import app_focused_manager
from device.workshop_tab.storage.discovery_store import discovery_store
from device.workshop_tab.storage.paths import (
    list_package_discoveries,
    list_all_packages_with_discoveries
)
from device.workshop_tab.discovery.discoverer import (
    get_discoverer,
    cancel_discovery,
    get_discovery_status,
    reset_discovery
)
from device.workshop_tab.discovery.filter import FilterMode
from device.workshop_tab.discovery.install_markers import InstallMarkersCollector
from device.workshop_tab.discovery.classloader_scanner import ClassLoaderScanner
from device.workshop_tab.discovery.modifier_scanner import ModifierScanner
from device.workshop_tab.discovery.java_discovery import JavaDiscovery
from device.workshop_tab.operations.operation_manager import operation_manager
from device.workshop_tab.operations.session_manager import session_manager
from device.workshop_tab.logging.workshop_logger import workshop_logger
from datetime import datetime

logger = get_logger(__name__, "device")

router = APIRouter()

device_manager = DeviceManager()
install_markers_collector = InstallMarkersCollector(adb_manager=device_manager.adb_manager)


def validate_session_ownership(device_id: str, client_id: str):
    if not workshop_session.is_owner(device_id, client_id):
        raise HTTPException(
            status_code=403,
            detail="Workshop session not owned by this client. Another tab has exclusive access."
        )


class SessionRequest(BaseModel):
    client_id: str


class AttachRequest(BaseModel):
    pid: Optional[int] = None
    package_id: Optional[str] = None
    spawn_if_needed: bool = False
    client_id: str


class DetachRequest(BaseModel):
    client_id: str


class SpawnRequest(BaseModel):
    package_id: str
    client_id: str


class CancelDiscoveryRequest(BaseModel):
    client_id: str


class DiscoverRequest(BaseModel):
    package_id: str
    pid: Optional[int] = None
    spawn_if_needed: bool = False
    spawn_delay: Optional[int] = None
    filter_mode: str = "focused"
    package_info: Optional[Dict[str, Any]] = None
    client_id: str
    app_focused_patterns: Optional[list] = None


class SaveDiscoveryRequest(BaseModel):
    package_id: str
    package_version: str
    custom_name: Optional[str] = None
    save_path: Optional[str] = None
    client_id: str
    # Phase 3: Triple redundancy fallback (Backend → Temp → Frontend cache)
    # These fields allow saving from frontend cache when backend/temp data is unavailable
    discovery_data: Optional[Dict[str, Any]] = None
    is_fallback_save: bool = False


class RulesUpdateRequest(BaseModel):
    rules: Dict[str, Any]


class AppFocusedConfigRequest(BaseModel):
    patterns: list


class AppFocusedTemplateRequest(BaseModel):
    name: str
    patterns: list


class ScanClassLoaderRequest(BaseModel):
    class_names: List[str]
    client_id: str
    package_id: str


class ExtractMethodsRequest(BaseModel):
    class_names: List[str]
    client_id: str
    package_id: str


class ScanModifiersRequest(BaseModel):
    class_names: List[str]
    scan_types: List[str]
    client_id: str
    package_id: str


class CancelOperationRequest(BaseModel):
    operation_type: str
    client_id: str


class RetentionConfigRequest(BaseModel):
    retention_limit: int
    client_id: str


# Session Management Endpoints

@router.post("/{device_id}/workshop/session/acquire")
async def acquire_session(device_id: str, request: SessionRequest):
    try:
        if not device_manager.is_device_connected(device_id):
            raise HTTPException(status_code=404, detail="Device not found")
        
        workshop_session.cleanup_expired()
        success, message = workshop_session.acquire(device_id, request.client_id)
        
        if not success:
            session_info = workshop_session.get_session_info(device_id)
            return {
                "success": False,
                "message": message,
                "client_id": request.client_id,
                "lock_owner": session_info.get("client_id") if session_info else None,
                "expires_in": session_info.get("expires_in", 0) if session_info else 0
            }
        
        return {
            "success": True,
            "message": message,
            "client_id": request.client_id,
            "expires_in": 30
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to acquire workshop session for {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{device_id}/workshop/session/heartbeat")
async def heartbeat_session(device_id: str, request: SessionRequest):
    try:
        success, message = workshop_session.heartbeat(device_id, request.client_id)
        
        return {
            "success": success,
            "message": message
        }
        
    except Exception as e:
        logger.error(f"Workshop session heartbeat failed for {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{device_id}/workshop/session/release")
async def release_session(device_id: str, request: SessionRequest):
    try:
        # Auto-detach Frida session if exists when releasing workshop session
        frida_status = frida_session_manager.get_status(device_id)
        if frida_status.get("attached"):
            logger.info(f"Auto-detaching Frida session on workshop release for {device_id}")
            frida_session_manager.detach(device_id)
        
        success, message = workshop_session.release(device_id, request.client_id)
        
        return {
            "success": success,
            "message": message
        }
        
    except Exception as e:
        logger.error(f"Failed to release workshop session for {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{device_id}/workshop/session/info")
async def get_session_info(device_id: str):
    try:
        workshop_session.cleanup_expired()
        
        info = workshop_session.get_session_info(device_id)
        
        if not info:
            return {"locked": False}
        
        return {
            "locked": True,
            **info
        }
        
    except Exception as e:
        logger.error(f"Failed to get workshop session info for {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Frida Control Endpoints

@router.post("/{device_id}/workshop/frida/attach")
async def attach_to_process(device_id: str, request: AttachRequest):
    try:
        if not device_manager.is_device_connected(device_id):
            raise HTTPException(status_code=404, detail="Device not found")
        
        validate_session_ownership(device_id, request.client_id)
        
        if request.pid is not None:
            result = frida_session_manager.attach(device_id, request.pid)
        elif request.package_id:
            result = frida_session_manager.attach_by_package(
                device_id,
                request.package_id,
                spawn_if_needed=request.spawn_if_needed
            )
        else:
            raise HTTPException(status_code=400, detail="Either pid or package_id must be provided")
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("message"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to attach to process on {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{device_id}/workshop/frida/detach")
async def detach_from_process(device_id: str, request: DetachRequest):
    try:
        validate_session_ownership(device_id, request.client_id)
        
        result = frida_session_manager.detach(device_id)
        return result
        
    except Exception as e:
        logger.error(f"Failed to detach from process on {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{device_id}/workshop/frida/spawn")
async def spawn_app(device_id: str, request: SpawnRequest):
    try:
        if not device_manager.is_device_connected(device_id):
            raise HTTPException(status_code=404, detail="Device not found")
        
        validate_session_ownership(device_id, request.client_id)
        
        result = frida_session_manager.spawn_and_attach(device_id, request.package_id)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("message"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to spawn app on {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{device_id}/workshop/frida/cleanup-all")
async def cleanup_all_frida_sessions(device_id: str, request: DetachRequest):
    """
    Emergency cleanup endpoint - detaches ALL Frida sessions across all devices.
    Useful for debugging or recovering from stuck sessions.
    """
    try:
        validate_session_ownership(device_id, request.client_id)
        
        logger.warning(f"Manual cleanup of all Frida sessions requested by client {request.client_id}")
        frida_session_manager.cleanup_all()
        
        return {
            "success": True,
            "message": "All Frida sessions cleaned up"
        }
        
    except Exception as e:
        logger.error(f"Failed to cleanup all Frida sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{device_id}/workshop/frida/status")
async def get_frida_status(device_id: str):
    try:
        status = frida_session_manager.get_status(device_id)
        return status
        
    except Exception as e:
        logger.error(f"Failed to get Frida status for {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{device_id}/workshop/packages")
async def list_packages_for_workshop(device_id: str, filter: str = "user"):
    try:
        if not device_manager.is_device_connected(device_id):
            raise HTTPException(status_code=404, detail="Device not found")
        
        if filter not in ["all", "user", "system"]:
            raise HTTPException(status_code=400, detail="Invalid filter type. Use 'all', 'user', or 'system'")
        
        from device.packages_tab.management.package_manager import PackageManager
        package_manager = PackageManager(device_manager.adb_manager)
        
        packages = package_manager.list_packages(device_id, filter_type=filter)
        
        user_count = sum(1 for p in packages if not p["is_system"])
        system_count = sum(1 for p in packages if p["is_system"])
        
        return {
            "packages": packages,
            "count": len(packages),
            "stats": {
                "user": user_count,
                "system": system_count
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list packages for workshop on {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{device_id}/workshop/frida/logs/live")
async def get_live_frida_logs(device_id: str, max_lines: int = 1000):
    try:
        from device.workshop_tab.logging.aggregated_frida_logger import aggregated_frida_logger
        
        logs = aggregated_frida_logger.get_logs(max_lines)
        return {"success": True, "logs": logs, "count": len(logs)}
        
    except Exception as e:
        logger.error(f"Failed to get live Frida logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{device_id}/workshop/frida/logs/clear")
async def clear_live_frida_logs(device_id: str, request: SessionRequest):
    try:
        validate_session_ownership(device_id, request.client_id)
        
        from device.workshop_tab.logging.aggregated_frida_logger import aggregated_frida_logger
        
        success = aggregated_frida_logger.clear()
        
        if success:
            return {"success": True, "message": "Frida logs cleared"}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear logs")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to clear live Frida logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Configuration Endpoints

@router.get("/workshop/config/rules")
async def get_rules():
    try:
        rules = rules_manager.get_rules()
        return rules
        
    except Exception as e:
        logger.error(f"Failed to get categorization rules: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/workshop/config/rules")
async def update_rules(request: RulesUpdateRequest):
    try:
        success = rules_manager.update_rules(request.rules)
        
        if not success:
            raise HTTPException(status_code=400, detail="Invalid rules format")
        
        return {"success": True, "message": "Rules updated"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update categorization rules: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workshop/config/rules/reset")
async def reset_rules():
    try:
        rules = rules_manager.reset_to_defaults()
        return {"success": True, "rules": rules}
        
    except Exception as e:
        logger.error(f"Failed to reset categorization rules: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# App Focused Configuration Endpoints

@router.get("/workshop/config/app-focused/{package_id}")
async def get_app_focused_config(package_id: str):
    try:
        config = app_focused_manager.get_config(package_id)
        return config
        
    except Exception as e:
        logger.error(f"Failed to get app focused config for {package_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/workshop/config/app-focused/{package_id}")
async def update_app_focused_config(package_id: str, request: AppFocusedConfigRequest):
    try:
        success = app_focused_manager.save_config(package_id, request.patterns)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save config")
        
        return {"success": True, "message": "Config saved"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update app focused config for {package_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workshop/config/app-focused/{package_id}/reset")
async def reset_app_focused_config(package_id: str):
    try:
        config = app_focused_manager.reset_to_default(package_id)
        return {"success": True, "config": config}
        
    except Exception as e:
        logger.error(f"Failed to reset app focused config for {package_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workshop/config/app-focused/{package_id}/templates")
async def list_app_focused_templates(package_id: str):
    try:
        templates = app_focused_manager.list_templates(package_id)
        return {"templates": templates, "count": len(templates)}
        
    except Exception as e:
        logger.error(f"Failed to list templates for {package_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workshop/config/app-focused/{package_id}/templates")
async def save_app_focused_template(package_id: str, request: AppFocusedTemplateRequest):
    try:
        success = app_focused_manager.save_template(package_id, request.name, request.patterns)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save template")
        
        return {"success": True, "message": f"Template '{request.name}' saved"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save template for {package_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workshop/config/app-focused/{package_id}/templates/{template_name}")
async def get_app_focused_template(package_id: str, template_name: str):
    try:
        template = app_focused_manager.get_template(package_id, template_name)
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return template
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get template {template_name} for {package_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/workshop/config/app-focused/{package_id}/templates/{template_name}")
async def delete_app_focused_template(package_id: str, template_name: str):
    try:
        success = app_focused_manager.delete_template(package_id, template_name)
        
        if not success:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return {"success": True, "message": f"Template '{template_name}' deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete template {template_name} for {package_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{device_id}/workshop/config/retention/{package_id}")
async def get_retention_config(device_id: str, package_id: str):
    try:
        if not device_manager.is_device_connected(device_id):
            raise HTTPException(status_code=404, detail="Device not found")
        
        from device.workshop_tab.storage.cleanup_config import cleanup_config_manager
        from device.workshop_tab.storage.temp_state_cleanup import temp_state_cleanup
        
        retention_limit = cleanup_config_manager.get_retention_limit(package_id)
        unsaved_temp_count = temp_state_cleanup._count_unsaved_temps(package_id)
        effective_limit = max(retention_limit, unsaved_temp_count)
        
        return {
            "retention_limit": retention_limit,
            "unsaved_temp_count": unsaved_temp_count,
            "effective_limit": effective_limit
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get retention config for {package_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{device_id}/workshop/config/retention/{package_id}")
async def set_retention_config(device_id: str, package_id: str, request: RetentionConfigRequest):
    try:
        if not device_manager.is_device_connected(device_id):
            raise HTTPException(status_code=404, detail="Device not found")
        
        validate_session_ownership(device_id, request.client_id)
        
        from device.workshop_tab.storage.cleanup_config import cleanup_config_manager
        from device.workshop_tab.storage.temp_state_cleanup import temp_state_cleanup
        
        if request.retention_limit < 1:
            raise HTTPException(status_code=400, detail="Retention limit must be at least 1")
        
        unsaved_temp_count = temp_state_cleanup._count_unsaved_temps(package_id)
        if request.retention_limit < unsaved_temp_count:
            raise HTTPException(
                status_code=400, 
                detail=f"Retention limit must be at least {unsaved_temp_count} (number of unsaved temp states)"
            )
        
        success = cleanup_config_manager.set_retention_limit(package_id, request.retention_limit)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save retention config")
        
        return {
            "success": True,
            "retention_limit": request.retention_limit,
            "unsaved_temp_count": unsaved_temp_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to set retention config for {package_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Install Markers Endpoint

@router.get("/{device_id}/workshop/install-markers/{package_id}")
async def get_install_markers(device_id: str, package_id: str):
    try:
        if not device_manager.is_device_connected(device_id):
            raise HTTPException(status_code=404, detail="Device not found")
        
        markers = install_markers_collector.get_install_markers(device_id, package_id)
        
        if not markers:
            raise HTTPException(status_code=404, detail=f"Package {package_id} not installed")
        
        return markers
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get install markers for {package_id} on {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Discovery Endpoints

@router.post("/{device_id}/workshop/discover")
async def start_discovery(device_id: str, request: DiscoverRequest):
    try:
        if not device_manager.is_device_connected(device_id):
            raise HTTPException(status_code=404, detail="Device not found")
        
        validate_session_ownership(device_id, request.client_id)
        
        discoverer = get_discoverer(device_id)
        
        if discoverer.get_state() == "running":
            raise HTTPException(status_code=409, detail="Discovery already in progress")
        
        # Reset state before starting new discovery to prevent WebSocket race condition
        discoverer.reset()
        
        # Parse filter mode from string
        try:
            filter_mode = FilterMode(request.filter_mode)
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid filter_mode: {request.filter_mode}. Valid values: focused, package, all"
            )
        
        # Resolve PID based on discovery mode
        pid = None
        if request.spawn_if_needed:
            logger.info(f"Spawning app {request.package_id} for discovery on {device_id}")
            spawn_result = frida_session_manager.spawn_and_attach(device_id, request.package_id)
            
            if not spawn_result.get("success"):
                error_msg = spawn_result.get("message", "Failed to spawn app")
                logger.error(f"Failed to spawn {request.package_id}: {error_msg}")
                raise HTTPException(status_code=500, detail=f"Failed to spawn app: {error_msg}")
            
            pid = spawn_result["pid"]
            logger.info(f"Successfully spawned {request.package_id} with PID {pid}")
            
            if request.spawn_delay is None:
                raise HTTPException(
                    status_code=400,
                    detail="spawn_delay must be provided when spawn_if_needed is true"
                )
            
            if request.spawn_delay < 0 or request.spawn_delay > 600:
                raise HTTPException(
                    status_code=400,
                    detail="spawn_delay must be between 0 and 600 seconds"
                )
            
            if request.spawn_delay > 0:
                logger.info(f"Waiting {request.spawn_delay} seconds for app to initialize...")
                await asyncio.sleep(request.spawn_delay)
                logger.info(f"Wait complete, starting discovery for {request.package_id}")
            
        elif request.pid is not None:
            pid = request.pid
            logger.info(f"Using provided PID {pid} for discovery on {device_id}")
            
        else:
            # Neither mode specified - invalid request
            raise HTTPException(
                status_code=400, 
                detail="Either 'pid' must be provided or 'spawn_if_needed' must be true"
            )
        
        asyncio.create_task(
            discoverer.discover(
                package_id=request.package_id,
                pid=pid,
                filter_mode=filter_mode,
                package_info=request.package_info,
                app_focused_patterns=request.app_focused_patterns
            )
        )
        
        return {
            "success": True,
            "message": "Discovery started",
            "filter_mode": filter_mode.value,
            "discovery_id": f"{request.package_id}_{discoverer._timestamp}",
            "pid": pid,
            "spawned": request.spawn_if_needed
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start discovery on {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{device_id}/workshop/discover/cancel")
async def cancel_discovery_endpoint(device_id: str, request: CancelDiscoveryRequest):
    try:
        validate_session_ownership(device_id, request.client_id)
        
        success = cancel_discovery(device_id)
        
        return {
            "success": success,
            "message": "Discovery cancelled" if success else "No active discovery"
        }
        
    except Exception as e:
        logger.error(f"Failed to cancel discovery on {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{device_id}/workshop/discovery/clear")
async def clear_discovery_endpoint(device_id: str, request: SessionRequest):
    try:
        validate_session_ownership(device_id, request.client_id)
        
        success = reset_discovery(device_id)
        
        return {
            "success": success,
            "message": "Discovery state cleared" if success else "No discovery to clear"
        }
        
    except Exception as e:
        logger.error(f"Failed to clear discovery on {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{device_id}/workshop/discovery/status")
async def get_discovery_status_endpoint(device_id: str):
    try:
        status = get_discovery_status(device_id)
        
        if not status:
            return {"state": "idle", "progress": 0}
        
        return status
        
    except Exception as e:
        logger.error(f"Failed to get discovery status for {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{device_id}/workshop/discovery/result")
async def get_discovery_result(device_id: str):
    try:
        discoverer = get_discoverer(device_id)
        result = discoverer.get_result()
        
        if not result:
            raise HTTPException(status_code=404, detail="No discovery result available")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get discovery result for {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{device_id}/workshop/discovery/logs")
async def get_discovery_logs(device_id: str, package_id: str, timestamp: str = None):
    try:
        from device.workshop_tab.logging.workshop_logger import read_discovery_logs
        
        logs, log_file = read_discovery_logs(package_id, timestamp)
        
        return {
            "package_id": package_id,
            "timestamp": timestamp,
            "logs": logs,
            "log_file": log_file,
            "count": len(logs)
        }
        
    except Exception as e:
        logger.error(f"Failed to get discovery logs for {package_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# On-Demand ClassLoader and Method Extraction Endpoints

@router.post("/{device_id}/workshop/scan-classloader")
async def scan_classloader(device_id: str, request: ScanClassLoaderRequest):
    try:
        if not device_manager.is_device_connected(device_id):
            raise HTTPException(status_code=404, detail="Device not found")
        
        validate_session_ownership(device_id, request.client_id)
        
        session = frida_session_manager.get_session(device_id)
        if not session:
            raise HTTPException(status_code=400, detail="No active Frida session. Attach to a process first.")
        
        if not request.class_names:
            return {"success": True, "results": [], "errors": []}
        
        from device.workshop_tab.frida_session.health_monitor import session_health_monitor
        from device.workshop_tab.logging.frida_session_logger import get_aggregate_logger
        from device.workshop_tab.logging.aggregated_frida_logger import aggregated_frida_logger
        
        session_info = frida_session_manager._sessions.get(device_id)
        session_number = session_info.get("session_number") if session_info else None
        
        if session_number:
            aggregated_frida_logger.log_operation_start(session_number, "scan_classloader", len(request.class_names))
        
        session_folder = session_manager.get_session_folder(device_id, request.package_id)
        operation_timestamp = datetime.now().strftime("%H%M%S")
        op_logger = workshop_logger.get_operation_logger(
            request.package_id,
            session_folder,
            "scan_classloader",
            operation_timestamp
        )
        
        session_manager.log_to_session(
            device_id,
            request.package_id,
            f"[OPERATION] scan_classloader started - Target: {len(request.class_names)} classes - Log: scan_classloader/{operation_timestamp}.log"
        )
        
        op_logger.info("=" * 60)
        op_logger.info("Operation: scan_classloader")
        op_logger.info(f"Classes to process: {len(request.class_names)}")
        op_logger.info(f"Device: {device_id}")
        op_logger.info(f"Package: {request.package_id}")
        op_logger.info("=" * 60)
        
        operation_id = operation_manager.register(device_id, "scan_classloader", len(request.class_names))
        start_time = datetime.now()
        
        item_count = len(request.class_names)
        session_health_monitor.start_monitoring(device_id, session, session_number, item_count)
        
        scanner = ClassLoaderScanner(session, device_id, None)
        
        def progress_callback(current, total, class_name):
            if operation_manager.is_cancelled(operation_id):
                scanner.cancel()
                session_health_monitor.stop_monitoring(device_id)
                op_logger.warning(f"Operation cancelled at {current}/{total}")
            
            if not session_health_monitor.is_session_healthy(device_id):
                reason = session_health_monitor.get_failure_reason(device_id)
                scanner.cancel()
                session_health_monitor.stop_monitoring(device_id)
                op_logger.error(f"Session health check failed: {reason}")
                if session_number:
                    agg_logger = get_aggregate_logger(session_number)
                    agg_logger.error(f"[SESSION_LOST] Operation aborted at {current}/{total} - Reason: {reason}")
            
            operation_manager.update_progress(operation_id, current, total, class_name)
            op_logger.info(f"[{current}/{total}] Processing: {class_name}")
        
        def save_callback(class_name: str, result: dict):
            try:
                from device.workshop_tab.storage.temp_state_manager import temp_state_manager
                class_state = {
                    class_name: {
                        "name": result["name"],
                        "scanned": True,
                        "is_from_apk": result.get("is_from_apk", False),
                        "loader_type": result.get("loader_type"),
                        "extracted": False,
                        "methods": None
                    }
                }
                temp_state_manager.save_temp_state(device_id, request.package_id, class_state)
                logger.debug(f"[AUTO-SAVE] Saved scan result for: {class_name}")
            except Exception as e:
                logger.warning(f"[AUTO-SAVE] Per-class save failed for {class_name}: {e}")
        
        results = scanner.scan_classes(request.class_names, progress_callback, save_callback)
        
        session_health_monitor.stop_monitoring(device_id)
        
        success_count = 0
        for result in results:
            if result.get("success"):
                op_logger.info(f"  ✓ {result['name']}")
                op_logger.debug(f"    ClassLoader: {result.get('loader_type', 'unknown')}")
                op_logger.debug(f"    is_from_apk: {result.get('is_from_apk', False)}")
                success_count += 1
            else:
                op_logger.error(f"  ✗ {result['name']}: {result.get('error', 'Unknown error')}")
        
        duration = (datetime.now() - start_time).total_seconds()
        apk_count = sum(1 for r in results if r.get("is_from_apk", False))
        throughput = len(results) / duration if duration > 0 and len(results) > 0 else 0
        
        op_logger.info("=" * 60)
        op_logger.info("OPERATION SUMMARY")
        op_logger.info("=" * 60)
        op_logger.info(f"  Total Classes:     {len(results)}")
        if len(results) > 0:
            op_logger.info(f"  Success:           {success_count} ({success_count/len(results)*100:.1f}%)")
            op_logger.info(f"  Failed:            {len(results) - success_count} ({(len(results)-success_count)/len(results)*100:.1f}%)")
        else:
            op_logger.info(f"  Success:           {success_count}")
            op_logger.info(f"  Failed:            0")
        op_logger.info(f"  APK Classes:       {apk_count}")
        op_logger.info(f"  System Classes:    {len(results) - apk_count}")
        op_logger.info("=" * 60)
        op_logger.info("PERFORMANCE METRICS")
        op_logger.info("=" * 60)
        op_logger.info(f"  Total Duration:    {duration:.3f}s")
        op_logger.info(f"  Throughput:        {throughput:.2f} classes/sec")
        if len(results) > 0:
            op_logger.info(f"  Avg Time/Class:    {duration/len(results)*1000:.1f}ms")
        if operation_manager.is_cancelled(operation_id):
            op_logger.info(f"  Status:            CANCELLED")
        else:
            op_logger.info(f"  Status:            COMPLETED")
        op_logger.info("=" * 60)
        
        metrics = operation_manager.finalize_operation(operation_id, success_count, len(results) - success_count)
        if metrics:
            session_manager.record_operation_metrics(device_id, request.package_id, "scan_classloader", metrics)
        
        success_rate = f"({success_count/len(results)*100:.1f}%)" if len(results) > 0 else "(0.0%)"
        session_manager.log_to_session(
            device_id,
            request.package_id,
            f"[OPERATION] scan_classloader - Success: {success_count}/{len(results)} {success_rate} - Duration: {duration:.2f}s - Throughput: {throughput:.2f} classes/sec"
        )
        
        operation_manager.unregister(operation_id)
        
        errors = [r for r in results if not r.get("success")]
        
        if scanner.is_session_lost():
            scan_errors = scanner.get_errors()
            session_errors = [e for e in scan_errors if e.get("error_type") in ["SESSION_DEAD", "SESSION_DETACHED", "TRANSPORT_ERROR"]]
            if session_errors and session_number:
                agg_logger = get_aggregate_logger(session_number)
                agg_logger.error(f"[SESSION_LOST] Agent crashed during scan - {len(session_errors)} errors")
                aggregated_frida_logger.log_session_lost(session_number, "Agent crashed during scan_classloader", f"{len(results)}/{len(request.class_names)} processed")
            
            if len(results) < len(request.class_names):
                attempted_class = request.class_names[len(results)]
                results.append({
                    "success": False,
                    "name": attempted_class,
                    "attempted": True,
                    "loader_type": "unknown",
                    "loader_path": None,
                    "is_from_apk": False,
                    "error": "session_crashed_during_processing"
                })
            
            return {
                "success": False,
                "results": results,
                "errors": errors,
                "session_lost": True,
                "reattach_needed": True,
                "total": len(results),
                "error_count": len(errors)
            }
        
        success_count = len([r for r in results if r.get("success")])
        if session_number:
            aggregated_frida_logger.log_operation_complete(session_number, "scan_classloader", success_count, len(results))
        
        return {
            "success": True,
            "results": results,
            "errors": errors,
            "session_lost": False,
            "total": len(results),
            "error_count": len(errors)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to scan ClassLoader on {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{device_id}/workshop/extract-methods")
async def extract_methods(device_id: str, request: ExtractMethodsRequest):
    try:
        if not device_manager.is_device_connected(device_id):
            raise HTTPException(status_code=404, detail="Device not found")
        
        validate_session_ownership(device_id, request.client_id)
        
        session = frida_session_manager.get_session(device_id)
        if not session:
            raise HTTPException(status_code=400, detail="No active Frida session. Attach to a process first.")
        
        if not request.class_names:
            return {"success": True, "results": [], "errors": []}
        
        from device.workshop_tab.frida_session.health_monitor import session_health_monitor
        from device.workshop_tab.logging.frida_session_logger import get_aggregate_logger
        from device.workshop_tab.logging.aggregated_frida_logger import aggregated_frida_logger
        
        session_info = frida_session_manager._sessions.get(device_id)
        session_number = session_info.get("session_number") if session_info else None
        
        if session_number:
            aggregated_frida_logger.log_operation_start(session_number, "extract_methods", len(request.class_names))
        
        session_folder = session_manager.get_session_folder(device_id, request.package_id)
        operation_timestamp = datetime.now().strftime("%H%M%S")
        op_logger = workshop_logger.get_operation_logger(
            request.package_id,
            session_folder,
            "extract_methods",
            operation_timestamp
        )
        
        session_manager.log_to_session(
            device_id,
            request.package_id,
            f"[OPERATION] extract_methods started - Target: {len(request.class_names)} classes - Log: extract_methods/{operation_timestamp}.log"
        )
        
        op_logger.info("=" * 60)
        op_logger.info("Operation: extract_methods")
        op_logger.info(f"Classes to process: {len(request.class_names)}")
        op_logger.info(f"Device: {device_id}")
        op_logger.info(f"Package: {request.package_id}")
        op_logger.info("=" * 60)
        
        operation_id = operation_manager.register(device_id, "extract_methods", len(request.class_names))
        start_time = datetime.now()
        
        item_count = len(request.class_names)
        session_health_monitor.start_monitoring(device_id, session, session_number, item_count)
        
        java_discovery = JavaDiscovery(session, device_id, None)
        
        def progress_callback(current, total, class_name):
            if operation_manager.is_cancelled(operation_id):
                java_discovery.cancel()
                session_health_monitor.stop_monitoring(device_id)
                op_logger.warning(f"Operation cancelled at {current}/{total}")
            
            if not session_health_monitor.is_session_healthy(device_id):
                reason = session_health_monitor.get_failure_reason(device_id)
                java_discovery.cancel()
                session_health_monitor.stop_monitoring(device_id)
                op_logger.error(f"Session health check failed: {reason}")
                if session_number:
                    agg_logger = get_aggregate_logger(session_number)
                    agg_logger.error(f"[SESSION_LOST] Operation aborted at {current}/{total} - Reason: {reason}")
            
            operation_manager.update_progress(operation_id, current, total, class_name)
            op_logger.info(f"[{current}/{total}] Processing: {class_name}")
        
        def save_callback(class_name: str, result: dict):
            try:
                from device.workshop_tab.storage.temp_state_manager import temp_state_manager
                class_state = {
                    class_name: {
                        "name": result["name"],
                        "extracted": True,
                        "methods": result.get("methods", []),
                        "method_count": result.get("method_count", 0),
                        "extraction_status": result.get("extraction_status", "completed")
                    }
                }
                temp_state_manager.save_temp_state(device_id, request.package_id, class_state)
                logger.debug(f"[AUTO-SAVE] Saved extract result for: {class_name} ({result.get('method_count', 0)} methods)")
            except Exception as e:
                logger.warning(f"[AUTO-SAVE] Per-class save failed for {class_name}: {e}")
        
        results = java_discovery.enumerate_methods(request.class_names, progress_callback, save_callback)
        
        session_health_monitor.stop_monitoring(device_id)
        
        success_count = 0
        total_methods = 0
        for result in results:
            method_count = result.get("method_count", 0)
            if method_count >= 0:
                op_logger.info(f"  ✓ {result['name']}: {method_count} methods")
                total_methods += method_count
                success_count += 1
            else:
                op_logger.error(f"  ✗ {result['name']}: Failed to extract methods")
        
        errors = java_discovery.get_errors()
        for error in errors:
            op_logger.error(f"  Error in {error.get('class', 'unknown')}: {error.get('error', 'Unknown error')}")
        
        duration = (datetime.now() - start_time).total_seconds()
        throughput = len(results) / duration if duration > 0 and len(results) > 0 else 0
        
        op_logger.info("=" * 60)
        op_logger.info("OPERATION SUMMARY")
        op_logger.info("=" * 60)
        op_logger.info(f"  Total Classes:     {len(results)}")
        if len(results) > 0:
            op_logger.info(f"  Success:           {success_count} ({success_count/len(results)*100:.1f}%)")
            op_logger.info(f"  Failed:            {len(errors)} ({len(errors)/len(results)*100:.1f}%)")
        else:
            op_logger.info(f"  Success:           {success_count}")
            op_logger.info(f"  Failed:            {len(errors)}")
        op_logger.info(f"  Total Methods:     {total_methods}")
        if success_count > 0:
            op_logger.info(f"  Avg Methods/Class: {total_methods/success_count:.1f}")
        op_logger.info("=" * 60)
        op_logger.info("PERFORMANCE METRICS")
        op_logger.info("=" * 60)
        op_logger.info(f"  Total Duration:    {duration:.3f}s")
        op_logger.info(f"  Throughput:        {throughput:.2f} classes/sec")
        if len(results) > 0:
            op_logger.info(f"  Avg Time/Class:    {duration/len(results)*1000:.1f}ms")
        if operation_manager.is_cancelled(operation_id):
            op_logger.info(f"  Status:            CANCELLED")
        else:
            op_logger.info(f"  Status:            COMPLETED")
        op_logger.info("=" * 60)
        
        metrics = operation_manager.finalize_operation(operation_id, success_count, len(errors))
        if metrics:
            session_manager.record_operation_metrics(device_id, request.package_id, "extract_methods", metrics)
        
        success_rate = f"({success_count/len(results)*100:.1f}%)" if len(results) > 0 else "(0.0%)"
        session_manager.log_to_session(
            device_id,
            request.package_id,
            f"[OPERATION] extract_methods - Success: {success_count}/{len(results)} {success_rate} - Methods: {total_methods} - Duration: {duration:.2f}s - Throughput: {throughput:.2f} classes/sec"
        )
        
        operation_manager.unregister(operation_id)
        
        if java_discovery.is_session_lost():
            session_errors = [e for e in errors if e.get("error_type") in ["SESSION_DEAD", "SESSION_DETACHED", "TRANSPORT_ERROR"]]
            if session_errors and session_number:
                agg_logger = get_aggregate_logger(session_number)
                agg_logger.error(f"[SESSION_LOST] Agent crashed during extraction - {len(session_errors)} errors")
                aggregated_frida_logger.log_session_lost(session_number, "Agent crashed during extract_methods", f"{len(results)}/{len(request.class_names)} processed")
            
            if len(results) < len(request.class_names):
                attempted_class = request.class_names[len(results)]
                results.append({
                    "success": False,
                    "name": attempted_class,
                    "attempted": True,
                    "method_count": 0,
                    "methods": [],
                    "error": "session_crashed_during_processing"
                })
            
            return {
                "success": False,
                "results": results,
                "errors": errors,
                "session_lost": True,
                "reattach_needed": True,
                "total": len(results),
                "error_count": len(errors)
            }
        
        if session_number:
            aggregated_frida_logger.log_operation_complete(session_number, "extract_methods", success_count, len(results))
        
        return {
            "success": True,
            "results": results,
            "errors": errors,
            "session_lost": False,
            "total": len(results),
            "error_count": len(errors)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to extract methods on {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{device_id}/workshop/scan-modifiers")
async def scan_modifiers(device_id: str, request: ScanModifiersRequest):
    try:
        if not device_manager.is_device_connected(device_id):
            raise HTTPException(status_code=404, detail="Device not found")
        
        validate_session_ownership(device_id, request.client_id)
        
        session = frida_session_manager.get_session(device_id)
        if not session:
            raise HTTPException(status_code=400, detail="No active Frida session. Attach to a process first.")
        
        if not request.class_names:
            return {"success": True, "results": [], "errors": []}
        
        if not request.scan_types:
            raise HTTPException(status_code=400, detail="No scan types specified")
        
        from device.workshop_tab.logging.frida_session_logger import get_aggregate_logger
        from device.workshop_tab.logging.aggregated_frida_logger import aggregated_frida_logger
        
        session_info = frida_session_manager._sessions.get(device_id)
        session_number = session_info.get("session_number") if session_info else None
        
        if session_number:
            aggregated_frida_logger.log_operation_start(session_number, "scan_modifiers", len(request.class_names))
        
        session_folder = session_manager.get_session_folder(device_id, request.package_id)
        operation_timestamp = datetime.now().strftime("%H%M%S")
        op_logger = workshop_logger.get_operation_logger(
            request.package_id,
            session_folder,
            "scan_modifiers",
            operation_timestamp
        )
        
        session_manager.log_to_session(
            device_id,
            request.package_id,
            f"[OPERATION] scan_modifiers started - Target: {len(request.class_names)} classes - Types: {', '.join(request.scan_types)} - Log: scan_modifiers/{operation_timestamp}.log"
        )
        
        op_logger.info("=" * 60)
        op_logger.info("Operation: scan_modifiers")
        op_logger.info(f"Classes to process: {len(request.class_names)}")
        op_logger.info(f"Scan types: {', '.join(request.scan_types)}")
        op_logger.info(f"Device: {device_id}")
        op_logger.info(f"Package: {request.package_id}")
        op_logger.info("=" * 60)
        
        operation_id = operation_manager.register(device_id, "scan_modifiers", len(request.class_names))
        start_time = datetime.now()
        
        scanner = ModifierScanner(session, device_id, None)
        
        def progress_callback(current, total, class_name):
            if operation_manager.is_cancelled(operation_id):
                scanner.cancel()
                op_logger.warning(f"Operation cancelled at {current}/{total}")
            operation_manager.update_progress(operation_id, current, total, class_name)
            op_logger.info(f"[{current}/{total}] Processing: {class_name}")
        
        def save_callback(class_name: str, result: dict):
            try:
                from device.workshop_tab.storage.temp_state_manager import temp_state_manager
                class_state = {
                    class_name: {
                        "name": result["name"]
                    }
                }
                for scan_type in request.scan_types:
                    if scan_type in result:
                        class_state[class_name][scan_type] = result[scan_type]
                
                temp_state_manager.save_temp_state(device_id, request.package_id, class_state)
                logger.debug(f"[AUTO-SAVE] Saved modifier scan result for: {class_name}")
            except Exception as e:
                logger.warning(f"[AUTO-SAVE] Per-class save failed for {class_name}: {e}")
        
        results = scanner.scan_classes(request.class_names, request.scan_types, progress_callback, save_callback)
        
        success_count = 0
        for result in results:
            if result.get("success"):
                modifiers_found = [k for k in request.scan_types if result.get(k)]
                op_logger.info(f"  ✓ {result['name']}: {', '.join(modifiers_found) if modifiers_found else 'none'}")
                success_count += 1
            else:
                op_logger.error(f"  ✗ {result['name']}: {result.get('error', 'Unknown error')}")
        
        duration = (datetime.now() - start_time).total_seconds()
        throughput = len(results) / duration if duration > 0 and len(results) > 0 else 0
        
        op_logger.info("=" * 60)
        op_logger.info("OPERATION SUMMARY")
        op_logger.info("=" * 60)
        op_logger.info(f"  Total Classes:     {len(results)}")
        if len(results) > 0:
            op_logger.info(f"  Success:           {success_count} ({success_count/len(results)*100:.1f}%)")
            op_logger.info(f"  Failed:            {len(results) - success_count} ({(len(results)-success_count)/len(results)*100:.1f}%)")
        else:
            op_logger.info(f"  Success:           {success_count}")
            op_logger.info(f"  Failed:            0")
        op_logger.info(f"  Scan Types:        {', '.join(request.scan_types)}")
        op_logger.info("=" * 60)
        op_logger.info("PERFORMANCE METRICS")
        op_logger.info("=" * 60)
        op_logger.info(f"  Total Duration:    {duration:.3f}s")
        op_logger.info(f"  Throughput:        {throughput:.2f} classes/sec")
        if len(results) > 0:
            op_logger.info(f"  Avg Time/Class:    {duration/len(results)*1000:.1f}ms")
        if operation_manager.is_cancelled(operation_id):
            op_logger.info(f"  Status:            CANCELLED")
        else:
            op_logger.info(f"  Status:            COMPLETED")
        op_logger.info("=" * 60)
        
        metrics = operation_manager.finalize_operation(operation_id, success_count, len(results) - success_count)
        if metrics:
            session_manager.record_operation_metrics(device_id, request.package_id, "scan_modifiers", metrics)
        
        success_rate = f"({success_count/len(results)*100:.1f}%)" if len(results) > 0 else "(0.0%)"
        session_manager.log_to_session(
            device_id,
            request.package_id,
            f"[OPERATION] scan_modifiers - Success: {success_count}/{len(results)} {success_rate} - Duration: {duration:.2f}s - Throughput: {throughput:.2f} classes/sec"
        )
        
        operation_manager.unregister(operation_id)
        
        errors = [r for r in results if not r.get("success")]
        
        if scanner.is_session_lost():
            scan_errors = scanner.get_errors()
            session_errors = [e for e in scan_errors if e.get("error_type") in ["SESSION_DEAD", "SESSION_DETACHED", "TRANSPORT_ERROR"]]
            if session_errors and session_number:
                agg_logger = get_aggregate_logger(session_number)
                agg_logger.error(f"[SESSION_LOST] Agent crashed during modifier scan - {len(session_errors)} errors")
                aggregated_frida_logger.log_session_lost(session_number, "Agent crashed during scan_modifiers", f"{len(results)}/{len(request.class_names)} processed")
            
            if len(results) < len(request.class_names):
                attempted_class = request.class_names[len(results)]
                results.append({
                    "success": False,
                    "name": attempted_class,
                    "attempted": True,
                    "error": "session_crashed_during_processing"
                })
            
            return {
                "success": False,
                "results": results,
                "errors": errors,
                "session_lost": True,
                "reattach_needed": True,
                "total": len(results),
                "error_count": len(errors)
            }
        
        success_count = len([r for r in results if r.get("success")])
        if session_number:
            aggregated_frida_logger.log_operation_complete(session_number, "scan_modifiers", success_count, len(results))
        
        return {
            "success": True,
            "results": results,
            "errors": errors,
            "session_lost": False,
            "total": len(results),
            "error_count": len(errors)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to scan modifiers on {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{device_id}/workshop/cancel-operation")
async def cancel_operation(device_id: str, request: CancelOperationRequest):
    try:
        validate_session_ownership(device_id, request.client_id)
        
        success = operation_manager.cancel(device_id, request.operation_type)
        
        return {
            "success": success,
            "message": f"Operation {request.operation_type} cancelled" if success else "No active operation"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel operation on {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{device_id}/workshop/operation/{operation_type}/progress")
async def get_operation_progress(device_id: str, operation_type: str):
    try:
        progress = operation_manager.get_device_operation(device_id, operation_type)
        
        if not progress:
            return {"active": False}
        
        return {
            "active": True,
            **progress
        }
        
    except Exception as e:
        logger.error(f"Failed to get operation progress for {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Temp State Management Endpoints (Phase 3)

@router.post("/{device_id}/workshop/sync-temp-state")
async def sync_temp_state(device_id: str, request: dict):
    """
    Frontend pushes class states at intervals to sync temp state.
    Used for auto-save functionality.
    """
    try:
        package_id = request.get("package_id")
        client_id = request.get("client_id")
        class_states = request.get("class_states", {})
        full_data = request.get("full_data")
        
        if not package_id or not client_id:
            raise HTTPException(status_code=400, detail="package_id and client_id required")
        
        validate_session_ownership(device_id, client_id)
        
        from device.workshop_tab.storage.temp_state_manager import temp_state_manager
        
        success = temp_state_manager.save_temp_state(
            device_id,
            package_id,
            class_states,
            full_data
        )
        
        if success:
            return {"success": True, "message": "Temp state synchronized"}
        else:
            raise HTTPException(status_code=500, detail="Failed to sync temp state")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to sync temp state for {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{device_id}/workshop/recovery-check/{package_id}")
async def check_recovery(device_id: str, package_id: str):
    """
    Check if recoverable temp state exists for this device+package.
    Called on WorkshopTab mount to offer crash recovery.
    """
    try:
        from device.workshop_tab.storage.temp_state_manager import temp_state_manager
        
        temp_state = temp_state_manager.load_temp_state(device_id, package_id)
        
        if temp_state:
            metadata = temp_state.get("metadata", {})
            state = temp_state.get("state", {})
            class_states = state.get("class_states", {})
            checkpoint_info = temp_state.get("checkpoint_info", {})
            
            # Calculate scanned/extracted counts
            scanned_count = sum(1 for s in class_states.values() if s.get("scanned"))
            extracted_count = sum(1 for s in class_states.values() if s.get("extracted"))
            
            return {
                "recoverable": True,
                "run_id": metadata.get("run_id"),
                "timestamp": metadata.get("timestamp"),
                "discovery_timestamp": metadata.get("discovery_timestamp"),
                "class_count": len(class_states),
                "scanned_count": scanned_count,
                "extracted_count": extracted_count,
                "last_saved_to": checkpoint_info.get("last_saved_folder"),
                "last_saved_timestamp": checkpoint_info.get("last_saved_timestamp")
            }
        
        return {"recoverable": False}
        
    except Exception as e:
        logger.error(f"Recovery check failed for {device_id}/{package_id}: {e}")
        return {"recoverable": False}


@router.post("/{device_id}/workshop/recover-temp-state")
async def recover_temp_state(device_id: str, request: dict):
    """
    Load and return full temp state for recovery.
    Frontend uses this to restore state after crash.
    """
    try:
        package_id = request.get("package_id")
        client_id = request.get("client_id")
        
        if not package_id or not client_id:
            raise HTTPException(status_code=400, detail="package_id and client_id required")
        
        validate_session_ownership(device_id, client_id)
        
        from device.workshop_tab.storage.temp_state_manager import temp_state_manager
        
        temp_state = temp_state_manager.load_temp_state(device_id, package_id)
        
        if not temp_state:
            raise HTTPException(status_code=404, detail="No temp state found")
        
        # Transform temp state to discovery result format
        result = {
            "metadata": temp_state.get("metadata", {}),
            "java_classes": temp_state.get("java_classes", {}),
            "native_modules": temp_state.get("native_modules", {}),
            "class_states": temp_state.get("state", {}).get("class_states", {}),
            "checkpoint_info": temp_state.get("checkpoint_info", {})
        }
        
        logger.info(f"Recovered temp state for {device_id}/{package_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Recovery failed for {device_id}/{package_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{device_id}/workshop/clear-temp-state")
async def clear_temp_state(device_id: str, request: dict):
    """
    Delete temp state directory.
    Used when user chooses to discard unsaved work.
    """
    try:
        package_id = request.get("package_id")
        client_id = request.get("client_id")
        
        if not package_id or not client_id:
            raise HTTPException(status_code=400, detail="package_id and client_id required")
        
        validate_session_ownership(device_id, client_id)
        
        from device.workshop_tab.storage.temp_state_manager import temp_state_manager
        
        success = temp_state_manager.clear_temp_state(device_id, package_id)
        
        if success:
            return {"success": True, "message": "Temp state cleared"}
        else:
            return {"success": False, "message": "No temp state to clear"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to clear temp state for {device_id}/{package_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Data Management Endpoints

@router.get("/workshop/folders")
async def list_discovery_folders(path: str = ""):
    try:
        from device.workshop_tab.storage.paths import WORKSHOP_DISCOVERIES_DIR
        
        base_dir = WORKSHOP_DISCOVERIES_DIR
        
        if path:
            safe_path = path.replace("\\", "/")
            parts = [p.strip() for p in safe_path.split("/") if p.strip()]
            current_dir = base_dir
            for part in parts:
                safe_part = part.replace("/", "_").replace("\\", "_")
                current_dir = current_dir / safe_part
        else:
            current_dir = base_dir
        
        if not current_dir.exists():
            current_dir.mkdir(parents=True, exist_ok=True)
        
        folders = []
        discoveries = []
        
        for item in sorted(current_dir.iterdir()):
            if item.is_dir():
                metadata_file = item / "metadata.json"
                if metadata_file.exists():
                    discoveries.append({
                        "folder": item.name,
                        "path": str(item)
                    })
                else:
                    folders.append(item.name)
        
        return {
            "path": path,
            "folders": folders,
            "discoveries": discoveries
        }
        
    except Exception as e:
        logger.error(f"Failed to list discovery folders: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{device_id}/workshop/discoveries/{package_id}")
async def list_discoveries(device_id: str, package_id: str):
    try:
        discoveries = list_package_discoveries(package_id)
        
        return {
            "package_id": package_id,
            "discoveries": discoveries,
            "count": len(discoveries)
        }
        
    except Exception as e:
        logger.error(f"Failed to list discoveries for {package_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workshop/discoveries")
async def list_all_discoveries():
    try:
        packages = list_all_packages_with_discoveries()
        
        return {
            "packages": packages,
            "total_packages": len(packages)
        }
        
    except Exception as e:
        logger.error(f"Failed to list all discoveries: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{device_id}/workshop/save")
async def save_discovery(device_id: str, request: SaveDiscoveryRequest):
    try:
        validate_session_ownership(device_id, request.client_id)
        
        discoverer = get_discoverer(device_id)
        result = discoverer.get_result()
        
        # PHASE 3: Merge temp state into result if available (PRIMARY PATH)
        if result:
            # Only merge if package_id matches to avoid cross-app contamination
            result_package_id = result.get("metadata", {}).get("package_id")
            
            if result_package_id == request.package_id:
                try:
                    from device.workshop_tab.storage.temp_state_manager import temp_state_manager
                    temp_state = temp_state_manager.load_temp_state(device_id, request.package_id)
                    
                    if temp_state and "state" in temp_state:
                        class_states = temp_state["state"].get("class_states", {})
                        
                        if class_states and "java_classes" in result and "classes" in result["java_classes"]:
                            # Merge temp states into java_classes
                            updated_count = 0
                            extracted_count = 0
                            scanned_count = 0
                            
                            for class_obj in result["java_classes"]["classes"]:
                                class_name = class_obj.get("name")
                                if class_name and class_name in class_states:
                                    state = class_states[class_name]
                                    
                                    # Safely merge each field with fallbacks
                                    if "scanned" in state:
                                        class_obj["scanned"] = state["scanned"]
                                        if state["scanned"]:
                                            scanned_count += 1
                                    
                                    if "extracted" in state:
                                        class_obj["extracted"] = state["extracted"]
                                        if state["extracted"]:
                                            extracted_count += 1
                                    
                                    if "is_from_apk" in state:
                                        class_obj["is_from_apk"] = state["is_from_apk"]
                                    
                                    if "loader_type" in state:
                                        class_obj["loader_type"] = state["loader_type"]
                                    
                                    # Most important: Update methods if extracted
                                    if state.get("extracted") and "methods" in state and state["methods"] is not None:
                                        class_obj["methods"] = state["methods"]
                                        class_obj["method_count"] = state.get("method_count", len(state["methods"]))
                                    
                                    updated_count += 1
                            
                            if updated_count > 0:
                                logger.info(f"[MANUAL SAVE] Merged {updated_count} class states from temp (scanned: {scanned_count}, extracted: {extracted_count})")
                                result["metadata"]["saved_from"] = "backend_with_temp_state"
                                result["metadata"]["temp_merge_stats"] = {
                                    "classes_updated": updated_count,
                                    "classes_scanned": scanned_count,
                                    "classes_extracted": extracted_count
                                }
                            else:
                                logger.info(f"[MANUAL SAVE] No class states to merge from temp")
                                result["metadata"]["saved_from"] = "backend_discovery_only"
                        else:
                            logger.info(f"[MANUAL SAVE] No temp class states available")
                            result["metadata"]["saved_from"] = "backend_discovery_only"
                    else:
                        logger.info(f"[MANUAL SAVE] No temp state found for {device_id}/{request.package_id}")
                        result["metadata"]["saved_from"] = "backend_discovery_only"
                
                except Exception as e:
                    logger.warning(f"[MANUAL SAVE] Failed to merge temp state: {e}")
                    result["metadata"]["saved_from"] = "backend_discovery_only"
                    result["metadata"]["temp_merge_error"] = str(e)
            else:
                # Package ID mismatch - user might have loaded old discovery or switched apps
                logger.warning(f"[MANUAL SAVE] Package ID mismatch: result={result_package_id}, request={request.package_id}")
                result["metadata"]["saved_from"] = "backend_discovery_only"
                result["metadata"]["package_mismatch"] = True
        
        # FRONTEND FALLBACK: If backend has nothing, use frontend data (SECONDARY PATH)
        if not result and request.discovery_data:
            if not request.is_fallback_save:
                raise HTTPException(
                    status_code=400, 
                    detail="Must set is_fallback_save=True when providing discovery_data"
                )
            
            logger.warning(f"[FALLBACK SAVE] Using frontend cache for {request.package_id} - backend data unavailable")
            result = request.discovery_data
            
            if "metadata" not in result or "java_classes" not in result or "native_modules" not in result:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid discovery_data format: missing required fields"
                )
            
            result["metadata"]["saved_from"] = "frontend_fallback"
            result["metadata"]["fallback_reason"] = "backend_data_unavailable"
        
        if not result:
            raise HTTPException(status_code=404, detail="No discovery result to save")
        
        folder_name = discovery_store.save_discovery(
            package_id=request.package_id,
            package_version=request.package_version,
            metadata=result["metadata"],
            java_classes=result["java_classes"],
            native_modules=result["native_modules"],
            custom_name=request.custom_name,
            save_path=request.save_path
        )
        
        if not folder_name:
            raise HTTPException(status_code=500, detail="Failed to save discovery")
        
        # Mark temp state as saved (keep temp alive for continued work)
        # Only mark for backend saves, not frontend fallback
        saved_from = result["metadata"].get("saved_from", "")
        if saved_from != "frontend_fallback":
            try:
                from device.workshop_tab.storage.temp_state_manager import temp_state_manager
                temp_state_manager.mark_as_saved(device_id, request.package_id, folder_name)
                logger.info(f"[MANUAL SAVE] Checkpoint updated - saved to: {folder_name}")
            except Exception as e:
                logger.warning(f"[MANUAL SAVE] Failed to mark temp as saved: {e}")
        
        return {
            "success": True,
            "message": "Discovery saved",
            "folder": folder_name,
            "used_fallback": request.is_fallback_save,
            "saved_from": saved_from
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save discovery for {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{device_id}/workshop/load/{package_id}/{discovery_folder}")
async def load_discovery(device_id: str, package_id: str, discovery_folder: str):
    try:
        data = discovery_store.load_discovery(package_id, discovery_folder)
        
        if not data:
            raise HTTPException(status_code=404, detail="Discovery not found")
        
        return data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to load discovery {package_id}/{discovery_folder}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{device_id}/workshop/discoveries/{package_id}/{discovery_folder}")
async def delete_discovery(device_id: str, package_id: str, discovery_folder: str):
    try:
        success = discovery_store.delete_discovery(package_id, discovery_folder)
        
        if not success:
            raise HTTPException(status_code=404, detail="Discovery not found")
        
        return {
            "success": True,
            "message": "Discovery deleted"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete discovery {package_id}/{discovery_folder}: {e}")
        raise HTTPException(status_code=500, detail=str(e))



