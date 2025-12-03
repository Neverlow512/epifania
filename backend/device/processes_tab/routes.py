from fastapi import APIRouter, HTTPException
from typing import Optional
from pydantic import BaseModel
from core.device_manager import DeviceManager
from device.processes_tab.monitoring.dprocess_monitor import ProcessMonitor
from device.processes_tab.monitoring.cpu_monitor import CPUMonitor
from device.processes_tab.monitoring.memory_monitor import MemoryMonitor
from device.processes_tab.monitoring.storage_monitor import StorageMonitor
from device.processes_tab.monitoring.network_monitor import NetworkMonitor
from device.processes_tab.monitoring.cache import polling_session
from device.processes_tab.overview.process_inspector import ProcessInspector
from device.processes_tab.overview.cache import (
    overview_polling_session,
    process_overview_cache
)
from core.logger import get_logger

logger = get_logger(__name__, "device")

router = APIRouter()

device_manager = DeviceManager()
process_monitor = ProcessMonitor(adb_manager=device_manager.adb_manager)
cpu_monitor = CPUMonitor(adb_manager=device_manager.adb_manager)
memory_monitor = MemoryMonitor(adb_manager=device_manager.adb_manager)
storage_monitor = StorageMonitor(adb_manager=device_manager.adb_manager)
network_monitor = NetworkMonitor(adb_manager=device_manager.adb_manager)
process_inspector = ProcessInspector(adb_manager=device_manager.adb_manager)


class SessionRequest(BaseModel):
    client_id: str
    interval_ms: int = 2000


class OverviewSessionRequest(BaseModel):
    client_id: str
    interval_ms: int = 5000


@router.post("/{device_id}/session/register")
async def register_session(device_id: str, request: SessionRequest):
    # Register a polling session for a device
    # First client becomes primary and controls the interval
    try:
        if not device_manager.is_device_connected(device_id):
            raise HTTPException(status_code=404, detail="Device not found")
        
        is_primary, message, active_interval = polling_session.register(
            device_id, request.client_id, request.interval_ms
        )
        
        return {
            "is_primary": is_primary,
            "message": message,
            "active_interval_ms": active_interval,
            "client_id": request.client_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to register session for {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{device_id}/session/unregister")
async def unregister_session(device_id: str, request: SessionRequest):
    # Unregister a polling session when tab closes
    try:
        polling_session.unregister(device_id, request.client_id)
        return {"success": True}
    except Exception as e:
        logger.error(f"Failed to unregister session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{device_id}/session/info")
async def get_session_info(device_id: str):
    # Get current session info for a device
    try:
        info = polling_session.get_session_info(device_id)
        if not info:
            return {"active": False}
        return {"active": True, **info}
    except Exception as e:
        logger.error(f"Failed to get session info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{device_id}/processes")
async def list_processes(device_id: str):
    try:
        logger.info(f"Process list requested for device {device_id}")
        
        if not device_manager.is_device_connected(device_id):
            raise HTTPException(status_code=404, detail="Device not found")
        
        processes = process_monitor.list_processes(device_id)
        process_monitor.store_metrics(device_id, processes)
        changes = process_monitor.detect_changes(device_id, processes)
        
        current_pids = [p['pid'] for p in processes]
        process_monitor.cleanup_metrics(device_id, current_pids)
        user_processes = [p for p in processes if not p['user'].startswith('system') and p['user'] != 'root']
        system_processes = [p for p in processes if p['user'].startswith('system') or p['user'] == 'root']
        
        total_memory_mb = sum(p['memory_mb'] for p in processes)
        
        return {
            "processes": processes,
            "count": len(processes),
            "stats": {
                "total": len(processes),
                "user": len(user_processes),
                "system": len(system_processes),
                "total_memory_mb": round(total_memory_mb, 2)
            },
            "changes": changes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list processes for {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{device_id}/processes/metrics")
async def get_process_metrics(device_id: str, pid: Optional[int] = None, duration: int = 60):
    try:
        logger.info(f"Process metrics requested for device {device_id}, pid={pid}, duration={duration}")
        
        if not device_manager.is_device_connected(device_id):
            raise HTTPException(status_code=404, detail="Device not found")
        
        metrics = process_monitor.get_process_metrics(device_id, pid, duration)
        
        return metrics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get metrics for {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{device_id}/processes/churn")
async def get_process_churn(device_id: str, window: int = 60):
    try:
        logger.info(f"Process churn requested for device {device_id}, window={window}s")
        
        if not device_manager.is_device_connected(device_id):
            raise HTTPException(status_code=404, detail="Device not found")
        
        churn_stats = process_monitor.get_churn_stats(device_id, window)
        return churn_stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get churn stats for {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{device_id}/processes/churn/history")
async def get_process_churn_history(device_id: str, limit: int = 500):
    try:
        logger.info(f"Process churn history requested for device {device_id}, limit={limit}")
        
        if not device_manager.is_device_connected(device_id):
            raise HTTPException(status_code=404, detail="Device not found")
        
        history = process_monitor.get_churn_history(device_id, limit)
        return history
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get churn history for {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{device_id}/processes/{pid}")
async def get_process_details(device_id: str, pid: int):
    try:
        logger.info(f"Process details requested for PID {pid} on device {device_id}")
        
        if not device_manager.is_device_connected(device_id):
            raise HTTPException(status_code=404, detail="Device not found")
        
        details = process_monitor.get_process_details(device_id, pid)
        
        if not details:
            raise HTTPException(status_code=404, detail=f"Process {pid} not found or inaccessible")
        
        return details
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get process details for {pid} on {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{device_id}/processes/{pid}/overview")
async def get_process_overview(device_id: str, pid: int, force_refresh: bool = False):
    try:
        logger.info(f"Process overview requested for PID {pid} on device {device_id}")
        
        if not device_manager.is_device_connected(device_id):
            raise HTTPException(status_code=404, detail="Device not found")
        
        def compute_overview():
            has_root = device_manager.adb_manager.check_root_access(device_id)
            return process_inspector.inspect(device_id, pid, has_root)
        
        if force_refresh:
            process_overview_cache.invalidate(device_id, pid)
        
        overview, is_cached, age = process_overview_cache.get_or_compute(
            device_id, pid, compute_overview
        )
        
        if not overview:
            raise HTTPException(
                status_code=404, 
                detail=f"Process {pid} not found or inaccessible"
            )
        
        overview["_cache"] = {
            "is_cached": is_cached,
            "age_seconds": round(age, 2)
        }
        
        return overview
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get process overview for {pid} on {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{device_id}/overview/session/register")
async def register_overview_session(device_id: str, request: OverviewSessionRequest):
    try:
        if not device_manager.is_device_connected(device_id):
            raise HTTPException(status_code=404, detail="Device not found")
        
        is_primary, message, active_interval = overview_polling_session.register(
            device_id, request.client_id, request.interval_ms
        )
        
        return {
            "is_primary": is_primary,
            "message": message,
            "active_interval_ms": active_interval,
            "client_id": request.client_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to register overview session for {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{device_id}/overview/session/unregister")
async def unregister_overview_session(device_id: str, request: OverviewSessionRequest):
    try:
        overview_polling_session.unregister(device_id, request.client_id)
        return {"success": True}
    except Exception as e:
        logger.error(f"Failed to unregister overview session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{device_id}/overview/session/info")
async def get_overview_session_info(device_id: str):
    try:
        info = overview_polling_session.get_session_info(device_id)
        if not info:
            return {"active": False}
        return {"active": True, **info}
    except Exception as e:
        logger.error(f"Failed to get overview session info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{device_id}/processes/{pid}/kill")
async def kill_process(device_id: str, pid: int, signal: int = 9):
    try:
        logger.info(f"Kill request for PID {pid} on device {device_id}")
        
        if not device_manager.is_device_connected(device_id):
            raise HTTPException(status_code=404, detail="Device not found")
        
        success = process_monitor.kill_process(device_id, pid, signal)
        
        if success:
            return {
                "success": True,
                "message": f"Process {pid} terminated successfully"
            }
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to terminate process {pid}. It may require root access or may not exist."
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to kill process {pid} on {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{device_id}/system/cpu")
async def get_cpu_stats(device_id: str, top_n: int = 5):
    try:
        logger.info(f"CPU stats requested for device {device_id}")
        
        if not device_manager.is_device_connected(device_id):
            raise HTTPException(status_code=404, detail="Device not found")
        
        stats = cpu_monitor.get_cpu_stats(device_id, top_n)
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get CPU stats for {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{device_id}/system/memory")
async def get_memory_stats(device_id: str, pid: Optional[int] = None):
    try:
        logger.info(f"Memory stats requested for device {device_id}, focused_pid={pid}")
        
        if not device_manager.is_device_connected(device_id):
            raise HTTPException(status_code=404, detail="Device not found")
        
        stats = memory_monitor.get_memory_stats(device_id, pid)
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get memory stats for {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{device_id}/system/storage")
async def get_storage_stats(device_id: str, partition: str = "/data"):
    try:
        logger.info(f"Storage stats requested for device {device_id}, partition={partition}")
        
        if not device_manager.is_device_connected(device_id):
            raise HTTPException(status_code=404, detail="Device not found")
        
        stats = storage_monitor.get_storage_stats(device_id, partition)
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get storage stats for {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{device_id}/system/storage/all")
async def get_all_partitions(device_id: str):
    try:
        logger.info(f"All partitions requested for device {device_id}")
        
        if not device_manager.is_device_connected(device_id):
            raise HTTPException(status_code=404, detail="Device not found")
        
        partitions = storage_monitor.get_all_partitions(device_id)
        return {"partitions": partitions}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get partitions for {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{device_id}/system/network")
async def get_network_stats(device_id: str, pid: Optional[int] = None):
    try:
        logger.info(f"Network stats requested for device {device_id}, focused_pid={pid}")
        
        if not device_manager.is_device_connected(device_id):
            raise HTTPException(status_code=404, detail="Device not found")
        
        stats = network_monitor.get_network_stats(device_id, pid)
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get network stats for {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{device_id}/system/network/connections")
async def get_all_connections(device_id: str):
    try:
        logger.info(f"All connections requested for device {device_id}")
        
        if not device_manager.is_device_connected(device_id):
            raise HTTPException(status_code=404, detail="Device not found")
        
        connections = network_monitor.get_all_connections(device_id)
        return {"connections": connections, "count": len(connections)}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get connections for {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
