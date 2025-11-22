import os
import requests
import gzip
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from core.logger import get_logger

logger = get_logger(__name__, "backend")


class Installer:
    def __init__(self, adb_manager=None):
        self.frida_release_url = "https://api.github.com/repos/frida/frida/releases"
        self.cache_dir = Path(__file__).parent.parent / "frida_servers"
        self.cache_dir.mkdir(exist_ok=True)
        self.adb_manager = adb_manager
        logger.info(f"Installer initialized with cache directory: {self.cache_dir}")
    
    def get_architecture_mapping(self, android_abi: str) -> str:
        mapping = {
            "armeabi-v7a": "arm",
            "armeabi": "arm",
            "arm64-v8a": "arm64",
            "x86": "x86",
            "x86_64": "x86_64"
        }
        arch = mapping.get(android_abi, android_abi)
        logger.debug(f"Mapped Android ABI {android_abi} to Frida architecture {arch}")
        return arch
    
    def fetch_available_versions(self, limit: int = 10) -> List[Dict[str, str]]:
        try:
            logger.info("Fetching available Frida versions from GitHub")
            response = requests.get(self.frida_release_url, timeout=10)
            response.raise_for_status()
            
            releases = response.json()
            versions = []
            
            for release in releases[:limit]:
                version = release.get("tag_name", "").replace("v", "")
                if version:
                    versions.append({
                        "version": version,
                        "name": release.get("name", version),
                        "published_at": release.get("published_at", ""),
                        "prerelease": release.get("prerelease", False)
                    })
            
            logger.info(f"Found {len(versions)} Frida versions")
            return versions
        except Exception as e:
            logger.error(f"Failed to fetch Frida versions: {str(e)}")
            return []
    
    def get_cached_versions(self) -> Dict[str, List[str]]:
        try:
            cached = {}
            
            if not self.cache_dir.exists():
                return cached
            
            for version_dir in self.cache_dir.iterdir():
                if version_dir.is_dir():
                    version = version_dir.name
                    architectures = []
                    
                    for arch_dir in version_dir.iterdir():
                        if arch_dir.is_dir() and (arch_dir / "frida-server").exists():
                            architectures.append(arch_dir.name)
                    
                    if architectures:
                        cached[version] = architectures
            
            logger.info(f"Found {len(cached)} cached Frida versions")
            return cached
        except Exception as e:
            logger.error(f"Failed to list cached versions: {str(e)}")
            return {}
    
    def check_frida_server_version(self, device_serial: str) -> Optional[str]:
        try:
            if not self.adb_manager:
                logger.error("ADB manager not initialized")
                return None
            
            device = self.adb_manager.get_device(device_serial)
            if not device:
                logger.error(f"Device {device_serial} not found")
                return None
            
            result = device.shell("/data/local/tmp/frida-server --version")
            if result:
                version = result.strip()
                logger.info(f"Frida server version on {device_serial}: {version}")
                return version
            
            logger.info(f"Frida server not found on {device_serial}")
            return None
        except Exception as e:
            logger.debug(f"Failed to check Frida server version on {device_serial}: {str(e)}")
            return None
    
    def is_frida_server_running(self, device_serial: str) -> bool:
        try:
            if not self.adb_manager:
                return False
            
            device = self.adb_manager.get_device(device_serial)
            if not device:
                return False
            
            result = device.shell("ps | grep frida-server")
            running = result and "frida-server" in result and "grep" not in result
            
            if running:
                logger.info(f"Frida server is running on {device_serial}")
            else:
                logger.info(f"Frida server is not running on {device_serial}")
            
            return running
        except Exception as e:
            logger.debug(f"Failed to check if Frida server is running: {str(e)}")
            return False
    
    def download_frida_server(self, version: str, architecture: str) -> Optional[Path]:
        try:
            cache_path = self.cache_dir / version / architecture
            cache_path.mkdir(parents=True, exist_ok=True)
            
            frida_binary = cache_path / "frida-server"
            
            if frida_binary.exists():
                logger.info(f"Frida server {version} for {architecture} already cached")
                return frida_binary
            
            download_url = f"https://github.com/frida/frida/releases/download/{version}/frida-server-{version}-android-{architecture}.xz"
            
            logger.info(f"Downloading Frida server from {download_url}")
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            compressed_file = cache_path / f"frida-server-{version}-android-{architecture}.xz"
            
            with open(compressed_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Decompressing Frida server")
            
            import lzma
            with lzma.open(compressed_file, 'rb') as f_in:
                with open(frida_binary, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            compressed_file.unlink()
            
            frida_binary.chmod(0o755)
            
            logger.info(f"Successfully downloaded and cached Frida server {version} for {architecture}")
            return frida_binary
        except Exception as e:
            logger.error(f"Failed to download Frida server {version} for {architecture}: {str(e)}")
            return None
    
    def install_frida_server(self, device_serial: str, version: str, architecture: str) -> bool:
        try:
            if not self.adb_manager:
                logger.error("ADB manager not initialized")
                return False
            
            logger.info(f"Installing Frida server {version} on {device_serial}")
            
            frida_binary = self.download_frida_server(version, architecture)
            if not frida_binary:
                logger.error("Failed to download Frida server")
                return False
            
            device = self.adb_manager.get_device(device_serial)
            if not device:
                logger.error(f"Device {device_serial} not found")
                return False
            
            logger.info(f"Pushing Frida server to device")
            device.push(str(frida_binary), "/data/local/tmp/frida-server")
            
            logger.info(f"Setting executable permissions")
            device.shell("chmod 755 /data/local/tmp/frida-server")
            
            logger.info(f"Successfully installed Frida server {version} on {device_serial}")
            return True
        except Exception as e:
            logger.error(f"Failed to install Frida server on {device_serial}: {str(e)}")
            return False
    
    def push_cached_server(self, device_serial: str, version: str, architecture: str) -> bool:
        try:
            if not self.adb_manager:
                logger.error("ADB manager not initialized")
                return False
            
            cache_path = self.cache_dir / version / architecture / "frida-server"
            
            if not cache_path.exists():
                logger.error(f"Cached Frida server not found: {cache_path}")
                return False
            
            logger.info(f"Pushing cached Frida server {version} to {device_serial}")
            
            device = self.adb_manager.get_device(device_serial)
            if not device:
                logger.error(f"Device {device_serial} not found")
                return False
            
            device.push(str(cache_path), "/data/local/tmp/frida-server")
            device.shell("chmod 755 /data/local/tmp/frida-server")
            
            logger.info(f"Successfully pushed cached Frida server to {device_serial}")
            return True
        except Exception as e:
            logger.error(f"Failed to push cached Frida server: {str(e)}")
            return False
    
    def start_frida_server(self, device_serial: str) -> bool:
        try:
            if not self.adb_manager:
                logger.error("ADB manager not initialized")
                return False
            
            if self.is_frida_server_running(device_serial):
                logger.info(f"Frida server already running on {device_serial}")
                return True
            
            device = self.adb_manager.get_device(device_serial)
            if not device:
                logger.error(f"Device {device_serial} not found")
                return False
            
            logger.info(f"Starting Frida server on {device_serial}")
            device.shell("/data/local/tmp/frida-server &")
            
            import time
            time.sleep(2)
            
            if self.is_frida_server_running(device_serial):
                logger.info(f"Frida server started successfully on {device_serial}")
                return True
            else:
                logger.error(f"Frida server failed to start on {device_serial}")
                return False
        except Exception as e:
            logger.error(f"Failed to start Frida server on {device_serial}: {str(e)}")
            return False
    
    def stop_frida_server(self, device_serial: str) -> bool:
        try:
            if not self.adb_manager:
                logger.error("ADB manager not initialized")
                return False
            
            device = self.adb_manager.get_device(device_serial)
            if not device:
                logger.error(f"Device {device_serial} not found")
                return False
            
            logger.info(f"Stopping Frida server on {device_serial}")
            device.shell("killall frida-server")
            
            import time
            time.sleep(1)
            
            if not self.is_frida_server_running(device_serial):
                logger.info(f"Frida server stopped successfully on {device_serial}")
                return True
            else:
                logger.warning(f"Frida server may still be running on {device_serial}")
                return False
        except Exception as e:
            logger.error(f"Failed to stop Frida server on {device_serial}: {str(e)}")
            return False
    
    def restart_frida_server(self, device_serial: str) -> bool:
        try:
            logger.info(f"Restarting Frida server on {device_serial}")
            self.stop_frida_server(device_serial)
            
            import time
            time.sleep(1)
            
            return self.start_frida_server(device_serial)
        except Exception as e:
            logger.error(f"Failed to restart Frida server on {device_serial}: {str(e)}")
            return False
