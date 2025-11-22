from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict
from core.device_manager import DeviceManager
from core.installer import Installer
from core.logger import get_logger
from core.log_streamer import log_streamer
import asyncio

logger = get_logger(__name__, "backend")

app = FastAPI(title="Epifania API", version="1.0.0")


class FridaInstallRequest(BaseModel):
    version: str
    architecture: Optional[str] = None


class FridaPushRequest(BaseModel):
    version: str
    architecture: str

@app.on_event("startup")
async def startup_event():
    logger.info("Epifania backend starting up")

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


@app.get("/health")
async def health_check():
    logger.debug("Health check requested")
    adb_available = device_manager.adb_manager.is_adb_available()
    return {
        "status": "healthy",
        "adb_connected": adb_available
    }


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
        
        frida_version = installer.check_frida_server_version(device_id)
        frida_running = installer.is_frida_server_running(device_id)
        
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
            start_success = installer.start_frida_server(device_id)
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
        success = installer.start_frida_server(device_id)
        
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
        success = installer.stop_frida_server(device_id)
        
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
        success = installer.restart_frida_server(device_id)
        
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


@app.websocket("/ws/devices/{device_id}/logs")
async def websocket_logs(websocket: WebSocket, device_id: str):
    await websocket.accept()
    logger.info(f"WebSocket connection established for device {device_id}")
    
    active_streams: Dict[str, bool] = {}
    
    async def send_log(dev_id: str, log_type: str, message: str, level: str):
        try:
            if dev_id == device_id and active_streams.get(log_type, False):
                await websocket.send_json({
                    "type": log_type,
                    "level": level,
                    "message": message,
                    "timestamp": asyncio.get_event_loop().time()
                })
        except Exception as e:
            logger.error(f"Error sending log via WebSocket: {str(e)}")
    
    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")
            log_type = data.get("log_type")
            
            if action == "start" and log_type:
                logger.info(f"Starting {log_type} stream for device {device_id}")
                active_streams[log_type] = True
                
                # Send historical logs first
                historical_logs = log_streamer.get_logs(device_id, log_type)
                for log_entry in historical_logs:
                    await websocket.send_json({
                        "type": log_type,
                        "level": log_entry.get("level", "info"),
                        "message": log_entry.get("message", ""),
                        "timestamp": log_entry.get("timestamp", "")
                    })
                
                # Start streaming based on log type
                if log_type == "logcat":
                    asyncio.create_task(log_streamer.stream_logcat(
                        device_id, 
                        device_manager.adb_manager,
                        send_log
                    ))
                
            elif action == "stop" and log_type:
                logger.info(f"Stopping {log_type} stream for device {device_id}")
                active_streams[log_type] = False
                log_streamer.stop_stream(device_id, log_type)
                
            elif action == "clear" and log_type:
                logger.info(f"Clearing {log_type} logs for device {device_id}")
                log_streamer.clear_logs(device_id, log_type)
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for device {device_id}")
        for log_type in active_streams:
            log_streamer.stop_stream(device_id, log_type)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        for log_type in active_streams:
            log_streamer.stop_stream(device_id, log_type)

