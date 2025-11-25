import os
import requests
import gzip
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from core.logger import get_logger

logger = get_logger(__name__, "backend")

try:
    from core.log_streamer import log_streamer
    LOG_STREAMER_AVAILABLE = True
except ImportError:
    LOG_STREAMER_AVAILABLE = False
    logger.warning("Log streamer not available")


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
    
    def get_recommended_version(self, device_info: Dict[str, any]) -> Optional[Dict[str, str]]:
        try:
            if not device_info:
                logger.error("Device info not provided")
                return None
            
            sdk = int(device_info.get("sdk_version", 0))
            android_ver = device_info.get("android_version", "Unknown")
            arch = device_info.get("architecture", "unknown")
            frida_arch = self.get_architecture_mapping(arch)
            device_serial = device_info.get("serial", "unknown")
            
            logger.info(f"Device {device_serial}: SDK {sdk}, Android {android_ver}, Arch {frida_arch}")
            
            # Check if we already have a cached version for this architecture
            cached = self.get_cached_versions()
            if cached:
                for version in sorted(cached.keys(), reverse=True):
                    if frida_arch in cached[version]:
                        logger.info(f"Found cached Frida version {version} for {frida_arch}")
                        return {
                            "version": version,
                            "name": version,
                            "architecture": frida_arch,
                            "sdk_version": sdk,
                            "android_version": android_ver,
                            "reason": "Latest cached version for device architecture",
                            "cached": True
                        }
            
            # Fetch available versions from GitHub
            versions = self.fetch_available_versions(limit=20)
            if not versions:
                logger.error("No Frida versions available")
                return None
            
            # Filter out prereleases for stability
            stable_versions = [v for v in versions if not v.get("prerelease", False)]
            if not stable_versions:
                stable_versions = versions
            
            # Get the latest stable version
            recommended = stable_versions[0] if stable_versions else None
            
            if recommended:
                logger.info(f"Recommended Frida version for {device_serial}: {recommended['version']}")
                return {
                    "version": recommended["version"],
                    "name": recommended.get("name", recommended["version"]),
                    "architecture": frida_arch,
                    "sdk_version": sdk,
                    "android_version": android_ver,
                    "reason": "Latest stable version compatible with device",
                    "cached": False
                }
            
            return None
        except Exception as e:
            logger.error(f"Failed to determine recommended version: {str(e)}")
            return None
    
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
                if LOG_STREAMER_AVAILABLE:
                    log_streamer.add_log(device_serial, "frida_install", "ADB manager not initialized", "error")
                return False
            
            logger.info(f"Installing Frida server {version} on {device_serial}")
            if LOG_STREAMER_AVAILABLE:
                log_streamer.add_log(device_serial, "frida_install", f"Starting installation of Frida {version} for {architecture}", "info")
            
            frida_binary = self.download_frida_server(version, architecture)
            if not frida_binary:
                logger.error("Failed to download Frida server")
                if LOG_STREAMER_AVAILABLE:
                    log_streamer.add_log(device_serial, "frida_install", "Failed to download Frida server", "error")
                return False
            
            if LOG_STREAMER_AVAILABLE:
                log_streamer.add_log(device_serial, "frida_install", f"Downloaded Frida server to {frida_binary}", "info")
            
            # Verify device is available (adb_manager will validate)
            # No need to get device object anymore
            
            logger.info(f"Pushing Frida server to device")
            if LOG_STREAMER_AVAILABLE:
                log_streamer.add_log(device_serial, "frida_install", "Pushing Frida server to /data/local/tmp/frida-server", "info")
                log_streamer.add_log(device_serial, "adb_operations", f"push {frida_binary} /data/local/tmp/frida-server", "info")
            
            # Use adb_manager's push method instead of device.push
            push_success = self.adb_manager.push_file(device_serial, str(frida_binary), "/data/local/tmp/frida-server")
            if not push_success:
                logger.error("Failed to push Frida server to device")
                if LOG_STREAMER_AVAILABLE:
                    log_streamer.add_log(device_serial, "frida_install", "Failed to push Frida server", "error")
                return False
            
            logger.info(f"Setting executable permissions")
            if LOG_STREAMER_AVAILABLE:
                log_streamer.add_log(device_serial, "frida_install", "Setting executable permissions", "info")
                log_streamer.add_log(device_serial, "adb_operations", "shell: chmod 755 /data/local/tmp/frida-server", "info")
            
            # Use adb_manager's execute_shell instead of device.shell
            chmod_result = self.adb_manager.execute_shell(device_serial, "chmod 755 /data/local/tmp/frida-server")
            if chmod_result is None:
                logger.warning("chmod command may have failed, but continuing")
            
            logger.info(f"Successfully installed Frida server {version} on {device_serial}")
            if LOG_STREAMER_AVAILABLE:
                log_streamer.add_log(device_serial, "frida_install", f"Successfully installed Frida server {version}", "info")
            return True
        except Exception as e:
            logger.error(f"Failed to install Frida server on {device_serial}: {str(e)}")
            if LOG_STREAMER_AVAILABLE:
                log_streamer.add_log(device_serial, "frida_install", f"Installation failed: {str(e)}", "error")
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
            
            # Use adb_manager's push method directly
            push_success = self.adb_manager.push_file(device_serial, str(cache_path), "/data/local/tmp/frida-server")
            if not push_success:
                logger.error("Failed to push cached Frida server to device")
                return False
            
            # Use adb_manager's execute_shell for chmod
            chmod_result = self.adb_manager.execute_shell(device_serial, "chmod 755 /data/local/tmp/frida-server")
            if chmod_result is None:
                logger.warning("chmod command may have failed, but continuing")
            
            logger.info(f"Successfully pushed cached Frida server to {device_serial}")
            return True
        except Exception as e:
            logger.error(f"Failed to push cached Frida server: {str(e)}")
            return False
    