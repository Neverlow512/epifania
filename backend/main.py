from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
from core.device_manager import DeviceManager
from core.installer import Installer
from frida_mgmt.manage.server import FridaServerManager
from frida_mgmt.manage.discovery import FridaDiscovery
from frida_mgmt.manage.permissions import FridaPermissions
from core.diagnostics import DeviceDiagnostics
from core.logger import get_logger
from core.log_streamer import log_streamer
from monitoring import health_manager, process_manager
import asyncio
from datetime import datetime
import frida

logger = get_logger(__name__, "backend")

# Cleanup stale processes before starting
logger.info("Performing pre-startup cleanup...")
process_manager.cleanup_stale_processes()

app = FastAPI(title="Epifania API", version="1.0.0")


class FridaInstallRequest(BaseModel):
    version: str
    architecture: Optional[str] = None


class FridaPushRequest(BaseModel):
    version: str
    architecture: str


class FridaCleanRequest(BaseModel):
    paths: List[str]

@app.on_event("startup")
async def startup_event():
    logger.info("Epifania backend starting up")
    
    # Write PID file for process tracking
    process_manager.write_pid_file()
    
    # Register health checks
    def check_adb_connection():
        try:
            return device_manager.adb_manager.is_adb_available()
        except Exception as e:
            logger.error(f"ADB health check failed: {str(e)}")
            return False
    
    health_manager.register_health_check(check_adb_connection, "adb_connection")
    
    # Start health monitoring
    await health_manager.start()
    logger.info("Health monitoring started")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Epifania backend shutting down")
    
    # Stop health monitoring
    await health_manager.stop()
    logger.info("Health monitoring stopped")
    
    # Cleanup process manager
    process_manager.cleanup_on_shutdown()
    logger.info("Process cleanup complete")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

device_manager = DeviceManager()
installer = Installer(adb_manager=device_manager.adb_manager)
server_manager = FridaServerManager(adb_manager=device_manager.adb_manager)
discovery_manager = FridaDiscovery(adb_manager=device_manager.adb_manager)
permissions_manager = FridaPermissions(adb_manager=device_manager.adb_manager)
diagnostics = DeviceDiagnostics(adb_manager=device_manager.adb_manager)


@app.get("/health")
async def health_check():
    logger.debug("Health check requested")
    adb_available = device_manager.adb_manager.is_adb_available()
    
    # Get device count for additional status info
    device_count = 0
    if adb_available:
        try:
            devices = device_manager.adb_manager.list_devices()
            device_count = len(devices)
        except:
            pass
    
    # Get health manager status
    health_status = health_manager.get_status()
    
    return {
        "status": "healthy" if health_status["is_healthy"] else "degraded",
        "adb_connected": adb_available,
        "device_count": device_count,
        "timestamp": datetime.now().isoformat(),
        "health_manager": health_status
    }


@app.get("/api/system/health")
async def get_system_health():
    try:
        logger.info("System health check requested")
        health_results = await health_manager.run_health_checks()
        return health_results
    except Exception as e:
        logger.error(f"Failed to get system health: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/adb/restart")
async def restart_adb():
    try:
        logger.info("ADB restart requested")
        result = device_manager.adb_manager.restart_adb_server()
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=500, detail=result["message"])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to restart ADB: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/devices")
async def get_devices():
    try:
        logger.info("Device enumeration requested")
        devices = device_manager.list_devices()
        logger.info(f"Found {len(devices)} device(s)")
        return {"devices": devices}
    except Exception as e:
        logger.error(f"Failed to enumerate devices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/devices/{device_id}")
async def get_device_details(device_id: str):
    try:
        logger.info(f"Device details requested for {device_id}")
        device = device_manager.get_device_details(device_id)
        
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        frida_version = server_manager.check_frida_server_version(device_id)
        frida_running = server_manager.is_frida_server_running(device_id)
        
        device["frida_server_version"] = frida_version
        device["frida_server_running"] = frida_running
        
        return device
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get device details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/devices/{device_id}/connect")
async def connect_device(device_id: str):
    try:
        logger.info(f"Connection verification requested for {device_id}")
        # Log the intent for visibility in ADB Operations
        log_streamer.add_log(device_id, "adb_operations", "verify: echo 'test'", "debug")
        result = device_manager.verify_device_connection(device_id)
        return result
    except Exception as e:
        logger.error(f"Failed to verify device connection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/frida/versions")
async def get_frida_versions():
    try:
        logger.info("Frida versions requested")
        versions = installer.fetch_available_versions(limit=15)
        return {"versions": versions}
    except Exception as e:
        logger.error(f"Failed to fetch Frida versions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/frida/cached")
async def get_cached_frida_versions():
    try:
        logger.info("Cached Frida versions requested")
        cached = installer.get_cached_versions()
        return {"cached": cached}
    except Exception as e:
        logger.error(f"Failed to get cached Frida versions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/devices/{device_id}/frida/recommended")
async def get_recommended_frida_version(device_id: str):
    try:
        logger.info(f"Recommended Frida version requested for {device_id}")
        
        # Get device details first
        device_info = device_manager.get_device_details(device_id)
        if not device_info:
            raise HTTPException(status_code=404, detail="Device not found")
        
        recommended = installer.get_recommended_version(device_info)
        
        if recommended:
            return recommended
        else:
            raise HTTPException(status_code=404, detail="Could not determine recommended version")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get recommended Frida version: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/devices/{device_id}/frida/install")
async def install_frida(device_id: str, request: FridaInstallRequest):
    try:
        logger.info(f"Frida installation requested for {device_id}, version {request.version}")
        
        device = device_manager.get_device_details(device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        architecture = request.architecture or device.get("architecture", "")
        frida_arch = installer.get_architecture_mapping(architecture)
        
        success = installer.install_frida_server(device_id, request.version, frida_arch)
        
        if success:
            # Pass the necessary functions to start_frida_server
            start_success = server_manager.start_frida_server(
                device_id,
                check_permissions_func=permissions_manager.check_permissions,
                set_permissions_func=permissions_manager.set_permissions,
                discover_servers_func=discovery_manager.discover_frida_servers
            )
            return {
                "success": True,
                "message": "Frida server installed successfully",
                "started": start_success
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to install Frida server")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to install Frida server: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/devices/{device_id}/frida/push")
async def push_frida(device_id: str, request: FridaPushRequest):
    try:
        logger.info(f"Frida push requested for {device_id}, version {request.version}")
        
        success = installer.push_cached_server(device_id, request.version, request.architecture)
        
        if success:
            return {"success": True, "message": "Frida server pushed successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to push Frida server")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to push Frida server: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/devices/{device_id}/frida/start")
async def start_frida(device_id: str):
    try:
        logger.info(f"Frida start requested for {device_id}")
        success = server_manager.start_frida_server(
            device_id,
            check_permissions_func=permissions_manager.check_permissions,
            set_permissions_func=permissions_manager.set_permissions,
            discover_servers_func=discovery_manager.discover_frida_servers
        )
        
        if success:
            return {"success": True, "message": "Frida server started successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to start Frida server")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start Frida server: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/devices/{device_id}/frida/stop")
async def stop_frida(device_id: str):
    try:
        logger.info(f"Frida stop requested for {device_id}")
        success = server_manager.stop_frida_server(device_id)
        
        if success:
            return {"success": True, "message": "Frida server stopped successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to stop Frida server")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to stop Frida server: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/devices/{device_id}/frida/restart")
async def restart_frida(device_id: str):
    try:
        logger.info(f"Frida restart requested for {device_id}")
        success = server_manager.restart_frida_server(
            device_id,
            check_permissions_func=permissions_manager.check_permissions,
            set_permissions_func=permissions_manager.set_permissions,
            discover_servers_func=discovery_manager.discover_frida_servers
        )
        
        if success:
            return {"success": True, "message": "Frida server restarted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to restart Frida server")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to restart Frida server: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/devices/{device_id}/logs/{log_type}")
async def get_device_logs(device_id: str, log_type: str):
    try:
        logger.info(f"Logs requested for device {device_id}, type {log_type}")
        logs = log_streamer.get_logs(device_id, log_type)
        return {"logs": logs}
    except Exception as e:
        logger.error(f"Failed to get logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/devices/{device_id}/frida/discover")
async def discover_frida_servers(device_id: str):
    try:
        logger.info(f"Frida server discovery requested for {device_id}")
        servers = discovery_manager.discover_frida_servers(device_id)
        return {"servers": servers}
    except Exception as e:
        logger.error(f"Failed to discover Frida servers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/devices/{device_id}/frida/clean")
async def clean_frida_servers(device_id: str, request: FridaCleanRequest):
    try:
        logger.info(f"Frida server cleanup requested for {device_id}")
        result = discovery_manager.remove_frida_servers(
            device_id,
            request.paths,
            is_running_func=server_manager.is_frida_server_running,
            stop_server_func=server_manager.stop_frida_server
        )
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=500, detail=result["message"])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to clean Frida servers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/devices/{device_id}/frida/permissions")
async def get_frida_permissions(device_id: str, path: str = "/data/local/tmp/frida-server"):
    try:
        logger.info(f"Frida permissions check requested for {device_id}")
        result = permissions_manager.check_permissions(device_id, path)
        return result
    except Exception as e:
        logger.error(f"Failed to check Frida permissions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/devices/{device_id}/frida/permissions")
async def set_frida_permissions(device_id: str, path: Optional[str] = None):
    try:
        if path is None:
            path = "/data/local/tmp/frida-server"
        logger.info(f"Frida permissions update requested for {device_id} at {path}")
        result = permissions_manager.set_permissions(device_id, path)
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=500, detail=result["message"])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to set Frida permissions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/devices/{device_id}/diagnostics/adb")
async def run_adb_diagnostics(device_id: str):
    try:
        logger.info(f"ADB diagnostics requested for {device_id}")
        results = diagnostics.run_full_diagnostics(device_id)
        return results
    except Exception as e:
        logger.error(f"Failed to run ADB diagnostics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/devices/{device_id}/frida/test-connection")
async def test_frida_connection(device_id: str):
    try:
        logger.info(f"Frida connection test requested for {device_id}")
        
        result = {
            "connected": False,
            "message": "",
            "details": {}
        }
        
        # Check if server is running first
        if not server_manager.is_frida_server_running(device_id):
            result["message"] = "Frida server is not running"
            result["details"]["error"] = "No frida-server process found"
            return result
        
        # Try to connect via Frida
        try:
            device = frida.get_device(device_id)
            result["details"]["device_name"] = device.name
            result["details"]["device_type"] = device.type
            
            # Try to enumerate processes to verify connection works
            processes = device.enumerate_processes()
            result["details"]["process_count"] = len(processes)
            
            result["connected"] = True
            result["message"] = "Frida connection successful"
            logger.info(f"Frida connection test passed for {device_id}")
            
        except frida.ServerNotRunningError:
            result["message"] = "Frida server not responding"
            result["details"]["error"] = "Server process exists but not responding"
        except frida.TimedOutError:
            result["message"] = "Frida connection timed out"
            result["details"]["error"] = "Connection attempt timed out"
        except Exception as frida_error:
            result["message"] = f"Frida connection failed: {str(frida_error)}"
            result["details"]["error"] = str(frida_error)
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to test Frida connection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/devices/{device_id}/logs")
async def websocket_logs(websocket: WebSocket, device_id: str):
    await websocket.accept()
    logger.info(f"WebSocket connection established for device {device_id}")
    
    active_streams: Dict[str, bool] = {}
    loop = asyncio.get_event_loop()
    
    async def send_payload(payload: Dict):
        try:
            log_type = payload.get("type")
            if active_streams.get(log_type, False):
                await websocket.send_json(payload)
        except Exception as e:
            logger.error(f"Error sending log via WebSocket: {str(e)}")
    
    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")
            log_type = data.get("log_type")
            
            logger.info(f"WebSocket received action='{action}' log_type='{log_type}' for device {device_id}")
            
            if action == "start" and log_type:
                logger.info(f"Starting {log_type} stream for device {device_id}")
                active_streams[log_type] = True
                # Register real-time updates for the requested log type
                log_streamer.register_subscriber(device_id, log_type, loop, send_payload)
                
                # Send historical logs first (for all log types)
                if log_type == "logcat":
                    # Populate history buffer from device
                    log_streamer.fetch_logcat_history(device_id, device_manager.adb_manager, max_lines=500)
                
                historical_logs = log_streamer.get_logs(device_id, log_type)
                for log_entry in historical_logs:
                    await websocket.send_json({
                        "type": log_type,
                        "level": log_entry.get("level", "info"),
                        "message": log_entry.get("message", ""),
                        "timestamp": log_entry.get("timestamp", "")
                    })
                
                # Start active streaming only for log types that need it
                # adb_operations and frida_install are event-driven (populated via add_log calls)
                if log_type == "logcat" and not log_streamer.is_streaming(device_id, log_type):
                    asyncio.create_task(log_streamer.stream_logcat(
                        device_id, 
                        device_manager.adb_manager,
                        loop
                    ))
                elif log_type == "frida_server" and not log_streamer.is_streaming(device_id, log_type):
                    asyncio.create_task(log_streamer.stream_frida_server(device_id, device_manager.adb_manager))
                
                # For event-driven logs, just acknowledge they're "active" (receiving updates)
                if log_type in ["adb_operations", "frida_install"]:
                    logger.info(f"{log_type} is now active and will receive real-time updates")
                    # Mark as streaming even though there's no background process
                    log_streamer.set_streaming(device_id, log_type, True)
                
            elif action == "stop" and log_type:
                logger.info(f"Stopping {log_type} stream for device {device_id}")
                active_streams[log_type] = False
                log_streamer.stop_stream(device_id, log_type)
                log_streamer.unregister_subscriber(device_id, log_type, send_payload)
                
            elif action == "clear" and log_type:
                logger.info(f"Clearing {log_type} logs for device {device_id}")
                log_streamer.clear_logs(device_id, log_type)
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for device {device_id}")
        for log_type in active_streams:
            log_streamer.stop_stream(device_id, log_type)
            log_streamer.unregister_subscriber(device_id, log_type, send_payload)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        for log_type in active_streams:
            log_streamer.stop_stream(device_id, log_type)
            log_streamer.unregister_subscriber(device_id, log_type, send_payload)

