# Install markers for app identification across devices
import re
from typing import Dict, Any, Optional
from core.adb_manager import ADBManager
from core.logger import get_logger

logger = get_logger(__name__, "workshop")


class InstallMarkersCollector:
    def __init__(self, adb_manager: ADBManager):
        self.adb_manager = adb_manager
    
    def get_install_markers(self, device_serial: str, package_id: str) -> Optional[Dict[str, Any]]:
        try:
            pkg_check = self.adb_manager.execute_shell(
                device_serial,
                f"pm list packages | grep -q 'package:{package_id}$' && echo 'exists'",
                timeout=5
            )
            if not pkg_check or "exists" not in pkg_check:
                logger.debug(f"Package {package_id} not installed on {device_serial}")
                return None
            
            markers = {"package_id": package_id}
            
            metadata = self.adb_manager.execute_shell(
                device_serial,
                f"pm dump {package_id} | grep -E 'versionName=|versionCode=|firstInstallTime=|lastUpdateTime=|signatures=' | head -10",
                timeout=10
            )
            
            if metadata:
                version_match = re.search(r'versionName=([^\s]+)', metadata)
                markers["version"] = version_match.group(1) if version_match else "unknown"
                
                version_code_match = re.search(r'versionCode=(\d+)', metadata)
                markers["version_code"] = int(version_code_match.group(1)) if version_code_match else 0
                
                first_install_match = re.search(r'firstInstallTime=(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})', metadata)
                markers["first_install_time"] = first_install_match.group(1) if first_install_match else None
                
                last_update_match = re.search(r'lastUpdateTime=(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})', metadata)
                markers["last_update_time"] = last_update_match.group(1) if last_update_match else None
                
                sig_match = re.search(r'signatures:\[([a-fA-F0-9]+)\]', metadata)
                markers["signing_cert_short"] = sig_match.group(1) if sig_match else None
            else:
                markers["version"] = "unknown"
                markers["version_code"] = 0
                markers["first_install_time"] = None
                markers["last_update_time"] = None
                markers["signing_cert_short"] = None
            
            logger.debug(f"Collected install markers for {package_id}: version={markers['version']}, first_install={markers['first_install_time']}")
            return markers
            
        except Exception as e:
            logger.error(f"Failed to get install markers for {package_id}: {e}")
            return None

