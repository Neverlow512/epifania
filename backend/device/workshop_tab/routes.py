# Workshop tab API endpoints
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio
from core.device_manager import DeviceManager
from core.logger import get_logger
from device.workshop_tab.session.workshop_session import workshop_session
from device.workshop_tab.frida_session.session_manager import frida_session_manager
from device.workshop_tab.config.rules_manager import rules_manager
from device.workshop_tab.storage.discovery_store import discovery_store
from device.workshop_tab.storage.paths import (
    list_package_discoveries,
    list_all_packages_with_discoveries
)
from device.workshop_tab.discovery.discoverer import (
    get_discoverer,
    cancel_discovery,
    get_discovery_status
)

logger = get_logger(__name__, "device")

router = APIRouter()

device_manager = DeviceManager()


class SessionRequest(BaseModel):
    client_id: str


class AttachRequest(BaseModel):
    pid: int


class DiscoverRequest(BaseModel):
    package_id: str
    pid: int
    include_system_libs: bool = False
    package_info: Optional[Dict[str, Any]] = None


class SaveDiscoveryRequest(BaseModel):
    package_id: str
    package_version: str


class RulesUpdateRequest(BaseModel):
    rules: Dict[str, Any]


# Session Management Endpoints

@router.post("/{device_id}/workshop/session/acquire")
async def acquire_session(device_id: str, request: SessionRequest):
    try:
        if not device_manager.is_device_connected(device_id):
            raise HTTPException(status_code=404, detail="Device not found")
        
        success, message = workshop_session.acquire(device_id, request.client_id)
        
        return {
            "success": success,
            "message": message,
            "client_id": request.client_id
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
        
        result = frida_session_manager.attach(device_id, request.pid)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("message"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to attach to process on {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{device_id}/workshop/frida/detach")
async def detach_from_process(device_id: str):
    try:
        result = frida_session_manager.detach(device_id)
        return result
        
    except Exception as e:
        logger.error(f"Failed to detach from process on {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{device_id}/workshop/frida/status")
async def get_frida_status(device_id: str):
    try:
        status = frida_session_manager.get_status(device_id)
        return status
        
    except Exception as e:
        logger.error(f"Failed to get Frida status for {device_id}: {e}")
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


# Discovery Endpoints

@router.post("/{device_id}/workshop/discover")
async def start_discovery(device_id: str, request: DiscoverRequest):
    try:
        if not device_manager.is_device_connected(device_id):
            raise HTTPException(status_code=404, detail="Device not found")
        
        discoverer = get_discoverer(device_id)
        
        if discoverer.get_state() == "running":
            raise HTTPException(status_code=409, detail="Discovery already in progress")
        
        asyncio.create_task(
            discoverer.discover(
                package_id=request.package_id,
                pid=request.pid,
                include_system_libs=request.include_system_libs,
                package_info=request.package_info
            )
        )
        
        return {
            "success": True,
            "message": "Discovery started",
            "discovery_id": f"{request.package_id}_{discoverer._timestamp}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start discovery on {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{device_id}/workshop/discover/cancel")
async def cancel_discovery_endpoint(device_id: str):
    try:
        success = cancel_discovery(device_id)
        
        return {
            "success": success,
            "message": "Discovery cancelled" if success else "No active discovery"
        }
        
    except Exception as e:
        logger.error(f"Failed to cancel discovery on {device_id}: {e}")
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


# Data Management Endpoints

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
        discoverer = get_discoverer(device_id)
        result = discoverer.get_result()
        
        if not result:
            raise HTTPException(status_code=404, detail="No discovery result to save")
        
        folder_name = discovery_store.save_discovery(
            package_id=request.package_id,
            package_version=request.package_version,
            metadata=result["metadata"],
            java_classes=result["java_classes"],
            native_modules=result["native_modules"]
        )
        
        if not folder_name:
            raise HTTPException(status_code=500, detail="Failed to save discovery")
        
        return {
            "success": True,
            "message": "Discovery saved",
            "folder": folder_name
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


# WebSocket for real-time progress streaming

@router.websocket("/ws/{device_id}/workshop/discovery")
async def websocket_discovery_progress(websocket: WebSocket, device_id: str):
    await websocket.accept()
    logger.info(f"WebSocket connection established for workshop discovery on {device_id}")
    
    try:
        while True:
            status = get_discovery_status(device_id)
            
            if status:
                await websocket.send_json(status)
                
                if status.get("state") in ["complete", "error", "cancelled"]:
                    break
            
            await asyncio.sleep(0.5)
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for workshop discovery on {device_id}")
    except Exception as e:
        logger.error(f"WebSocket error for workshop discovery: {e}")

