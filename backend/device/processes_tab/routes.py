from fastapi import APIRouter, HTTPException
from typing import Optional
from core.device_manager import DeviceManager
from device.processes_tab.monitoring.dprocess_monitor import ProcessMonitor
from core.logger import get_logger

logger = get_logger(__name__, "device")

router = APIRouter()

device_manager = DeviceManager()
process_monitor = ProcessMonitor(adb_manager=device_manager.adb_manager)


@router.get("/{device_id}/processes")
async def list_processes(device_id: str):
    try:
        logger.info(f"Process list requested for device {device_id}")
        
        device = device_manager.get_device_details(device_id)
        if not device:
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


@router.get("/{device_id}/processes/{pid}")
async def get_process_details(device_id: str, pid: int):
    try:
        logger.info(f"Process details requested for PID {pid} on device {device_id}")
        
        device = device_manager.get_device_details(device_id)
        if not device:
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


@router.post("/{device_id}/processes/{pid}/kill")
async def kill_process(device_id: str, pid: int, signal: int = 9):
    try:
        logger.info(f"Kill request for PID {pid} on device {device_id}")
        
        device = device_manager.get_device_details(device_id)
        if not device:
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


@router.get("/{device_id}/processes/metrics")
async def get_process_metrics(device_id: str, pid: Optional[int] = None, duration: int = 60):
    try:
        logger.info(f"Process metrics requested for device {device_id}, pid={pid}, duration={duration}")
        
        device = device_manager.get_device_details(device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        metrics = process_monitor.get_process_metrics(device_id, pid, duration)
        
        return metrics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get metrics for {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

