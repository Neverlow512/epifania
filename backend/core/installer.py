import requests
from typing import Optional


class Installer:
    def __init__(self):
        self.frida_release_url = "https://github.com/frida/frida/releases"
    
    def check_frida_server_version(self, device_id: str) -> Optional[str]:
        pass
    
    def download_frida_server(self, version: str, architecture: str) -> bytes:
        pass
    
    def install_frida_server(self, device_id: str, binary_path: str) -> bool:
        pass

