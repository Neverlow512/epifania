import frida
from typing import List, Dict


class DeviceManager:
    def __init__(self):
        self.device_manager = frida.get_device_manager()
    
    def list_devices(self) -> List[Dict[str, str]]:
        try:
            devices = self.device_manager.enumerate_devices()
            return [
                {
                    "id": device.id,
                    "name": device.name,
                    "type": device.type
                }
                for device in devices
            ]
        except Exception as e:
            raise RuntimeError(f"Failed to enumerate devices: {str(e)}")

