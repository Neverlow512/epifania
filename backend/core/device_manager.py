import frida
from typing import List, Dict
from backend.core.logger import get_logger

logger = get_logger(__name__, "device")


class DeviceManager:
    def __init__(self):
        self.device_manager = frida.get_device_manager()
        logger.info("DeviceManager initialized")
    
    def list_devices(self) -> List[Dict[str, str]]:
        try:
            logger.info("Enumerating Frida devices")
            devices = self.device_manager.enumerate_devices()
            device_list = [
                {
                    "id": device.id,
                    "name": device.name,
                    "type": device.type
                }
                for device in devices
            ]
            logger.info(f"Enumerated {len(device_list)} devices: {[d['name'] for d in device_list]}")
            return device_list
        except Exception as e:
            logger.error(f"Failed to enumerate devices: {str(e)}")
            raise RuntimeError(f"Failed to enumerate devices: {str(e)}")

