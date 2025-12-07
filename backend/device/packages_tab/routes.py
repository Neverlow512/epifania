from fastapi import APIRouter, HTTPException
from typing import Optional
from pydantic import BaseModel
from core.device_manager import DeviceManager
from device.packages_tab.management.package_manager import PackageManager
from device.packages_tab.management.cache import packages_polling_session
from core.logger import get_logger

logger = get_logger(__name__, "device")

router = APIRouter()

device_manager = DeviceManager()
package_manager = PackageManager(adb_manager=device_manager.adb_manager)


class SessionRequest(BaseModel):
    client_id: str
    interval_ms: int = 5000


class InstallRequest(BaseModel):
    apk_source: str
    is_local_file: bool = True
    device_temp_path: str = "/data/local/tmp/temp_install.apk"


class PullRequest(BaseModel):
    destination_path: str


@router.post("/{device_id}/packages/session/register")
async def register_session(device_id: str, request: SessionRequest):
    try:
        if not device_manager.is_device_connected(device_id):
            raise HTTPException(status_code=404, detail="Device not found")
        
        is_primary, message, active_interval = packages_polling_session.register(
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
        logger.error(f"Failed to register packages session for {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{device_id}/packages/session/unregister")
async def unregister_session(device_id: str, request: SessionRequest):
    try:
        packages_polling_session.unregister(device_id, request.client_id)
        return {"success": True}
    except Exception as e:
        logger.error(f"Failed to unregister packages session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{device_id}/packages/session/info")
async def get_session_info(device_id: str):
    try:
        info = packages_polling_session.get_session_info(device_id)
        if not info:
            return {"active": False}
        return {"active": True, **info}
    except Exception as e:
        logger.error(f"Failed to get packages session info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{device_id}/packages")
async def list_packages(device_id: str, filter: str = "all"):
    try:
        logger.info(f"Package list requested for device {device_id}, filter={filter}")
        
        if not device_manager.is_device_connected(device_id):
            raise HTTPException(status_code=404, detail="Device not found")
        
        if filter not in ["all", "user", "system"]:
            raise HTTPException(status_code=400, detail="Invalid filter type. Use 'all', 'user', or 'system'")
        
        packages = package_manager.list_packages(device_id, filter_type=filter)
        
        user_count = sum(1 for p in packages if not p["is_system"])
        system_count = sum(1 for p in packages if p["is_system"])
        running_count = sum(1 for p in packages if p["is_running"])
        
        return {
            "packages": packages,
            "count": len(packages),
            "stats": {
                "user": user_count,
                "system": system_count,
                "running": running_count
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list packages for {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{device_id}/packages/available-apks")
async def list_available_apks(device_id: str):
    try:
        logger.info(f"Available APKs list requested for device {device_id}")
        
        if not device_manager.is_device_connected(device_id):
            raise HTTPException(status_code=404, detail="Device not found")
        
        apks = package_manager.list_available_apks()
        
        return {
            "apks": apks,
            "count": len(apks)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list available APKs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{device_id}/packages/{package_id:path}")
async def get_package_details(device_id: str, package_id: str):
    try:
        logger.info(f"Package details requested for {package_id} on device {device_id}")
        
        if not device_manager.is_device_connected(device_id):
            raise HTTPException(status_code=404, detail="Device not found")
        
        details = package_manager.get_package_details(device_id, package_id)
        
        if not details:
            raise HTTPException(status_code=404, detail=f"Package {package_id} not found")
        
        return details
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get package details for {package_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{device_id}/packages/install")
async def install_package(device_id: str, request: InstallRequest):
    try:
        logger.info(f"Package installation requested for device {device_id}")
        
        if not device_manager.is_device_connected(device_id):
            raise HTTPException(status_code=404, detail="Device not found")
        
        success = package_manager.install_package(
            device_id, 
            request.apk_source, 
            request.is_local_file,
            request.device_temp_path
        )
        
        if success:
            return {
                "success": True,
                "message": f"Package installed successfully from {request.apk_source}"
            }
        else:
            raise HTTPException(
                status_code=500, 
                detail="Failed to install package. Check logs for details."
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to install package on {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{device_id}/packages/{package_id:path}")
async def uninstall_package(device_id: str, package_id: str, keep_data: bool = False):
    try:
        logger.info(f"Package uninstall requested for {package_id} on device {device_id}")
        
        if not device_manager.is_device_connected(device_id):
            raise HTTPException(status_code=404, detail="Device not found")
        
        success = package_manager.uninstall_package(device_id, package_id, keep_data)
        
        if success:
            return {
                "success": True,
                "message": f"Package {package_id} uninstalled successfully"
            }
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to uninstall {package_id}. It may be a system app or protected."
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to uninstall {package_id} on {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{device_id}/packages/{package_id:path}/pull")
async def pull_package(device_id: str, package_id: str, request: PullRequest):
    try:
        logger.info(f"Package pull requested for {package_id} on device {device_id}")
        
        if not device_manager.is_device_connected(device_id):
            raise HTTPException(status_code=404, detail="Device not found")
        
        local_path = package_manager.pull_package(
            device_id, 
            package_id, 
            request.destination_path
        )
        
        if local_path:
            return {
                "success": True,
                "message": f"Package {package_id} pulled successfully",
                "local_path": local_path
            }
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to pull {package_id}. Check if package exists and destination is writable."
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to pull {package_id} from {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{device_id}/packages/{package_id:path}/launch")
async def launch_package(device_id: str, package_id: str):
    try:
        logger.info(f"Package launch requested for {package_id} on device {device_id}")
        
        if not device_manager.is_device_connected(device_id):
            raise HTTPException(status_code=404, detail="Device not found")
        
        success = package_manager.launch_package(device_id, package_id)
        
        if success:
            return {
                "success": True,
                "message": f"Package {package_id} launched successfully"
            }
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to launch {package_id}. It may not have a launchable activity."
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to launch {package_id} on {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{device_id}/packages/{package_id:path}/stop")
async def force_stop_package(device_id: str, package_id: str):
    try:
        logger.info(f"Force stop requested for {package_id} on device {device_id}")
        
        if not device_manager.is_device_connected(device_id):
            raise HTTPException(status_code=404, detail="Device not found")
        
        success = package_manager.force_stop(device_id, package_id)
        
        if success:
            return {
                "success": True,
                "message": f"Package {package_id} force stopped successfully"
            }
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to force stop {package_id}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to force stop {package_id} on {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{device_id}/packages/{package_id:path}/clear-cache")
async def clear_cache(device_id: str, package_id: str):
    try:
        logger.info(f"Clear cache requested for {package_id} on device {device_id}")
        
        if not device_manager.is_device_connected(device_id):
            raise HTTPException(status_code=404, detail="Device not found")
        
        success = package_manager.clear_cache(device_id, package_id)
        
        if success:
            return {
                "success": True,
                "message": f"Cache cleared for {package_id}"
            }
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to clear cache for {package_id}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to clear cache for {package_id} on {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{device_id}/packages/{package_id:path}/clear-data")
async def clear_data(device_id: str, package_id: str):
    try:
        logger.info(f"Clear data requested for {package_id} on device {device_id}")
        
        if not device_manager.is_device_connected(device_id):
            raise HTTPException(status_code=404, detail="Device not found")
        
        success = package_manager.clear_data(device_id, package_id)
        
        if success:
            return {
                "success": True,
                "message": f"Data cleared for {package_id}"
            }
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to clear data for {package_id}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to clear data for {package_id} on {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

