import re
import os
from typing import List, Dict, Optional
from pathlib import Path
from core.logger import get_logger
from core.adb_manager import ADBManager

logger = get_logger(__name__, "device")

# Get project root directory (5 levels up from this file: management/ -> packages_tab/ -> device/ -> backend/ -> project_root/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent


class PackageManager:
    def __init__(self, adb_manager: ADBManager):
        self.adb_manager = adb_manager
    
    def _validate_package_id(self, package_id: str) -> bool:
        if not package_id:
            return False
        pattern = r'^[a-zA-Z][a-zA-Z0-9_]*(\.[a-zA-Z][a-zA-Z0-9_]*)+$'
        return bool(re.match(pattern, package_id))
    
    def list_available_apks(self) -> List[Dict]:
        """Scan for available APK files and split APK directories"""
        apks = []
        
        # Default APK storage locations
        search_paths = [
            PROJECT_ROOT / "tmp" / "extracted_apks",
            PROJECT_ROOT / "backend" / "tmp" / "extracted_apks"
        ]
        
        for base_path in search_paths:
            if not base_path.exists():
                continue
            
            try:
                for item in base_path.iterdir():
                    if item.is_file() and item.suffix == '.apk':
                        # Single APK file
                        try:
                            size_mb = item.stat().st_size / (1024 * 1024)
                            apks.append({
                                "path": str(item.relative_to(PROJECT_ROOT)),
                                "name": item.stem,
                                "type": "single",
                                "size_mb": round(size_mb, 2),
                                "file_count": 1,
                                "modified": item.stat().st_mtime
                            })
                        except Exception as e:
                            logger.warning(f"Failed to get info for {item}: {str(e)}")
                    
                    elif item.is_dir():
                        # Check if it's a split APK directory
                        apk_files = list(item.glob("*.apk"))
                        if apk_files:
                            try:
                                total_size_mb = sum(f.stat().st_size for f in apk_files) / (1024 * 1024)
                                has_base = any(f.name == "base.apk" for f in apk_files)
                                has_splits = any(f.name.startswith("split_") for f in apk_files)
                                
                                apk_type = "split" if (has_base or has_splits) else "multiple"
                                
                                apks.append({
                                    "path": str(item.relative_to(PROJECT_ROOT)),
                                    "name": item.name,
                                    "type": apk_type,
                                    "size_mb": round(total_size_mb, 2),
                                    "file_count": len(apk_files),
                                    "modified": max(f.stat().st_mtime for f in apk_files)
                                })
                            except Exception as e:
                                logger.warning(f"Failed to get info for {item}: {str(e)}")
            
            except Exception as e:
                logger.warning(f"Failed to scan {base_path}: {str(e)}")
        
        # Sort by modified time (newest first)
        apks.sort(key=lambda x: x["modified"], reverse=True)
        
        logger.info(f"Found {len(apks)} available APK(s)")
        return apks
    
    def _get_pid_for_package(self, device_serial: str, package_id: str) -> Optional[int]:
        try:
            result = self.adb_manager.execute_shell(device_serial, f"pidof {package_id}", timeout=5)
            if result and result.strip():
                pid_str = result.strip().split()[0]
                return int(pid_str)
        except Exception as e:
            logger.debug(f"Could not get PID for {package_id}: {str(e)}")
        return None
    
    def _get_running_packages(self, device_serial: str) -> Dict[str, int]:
        """Batch fetch all running app PIDs in a single command"""
        running = {}
        try:
            result = self.adb_manager.execute_shell(
                device_serial,
                "ps -A -o PID,NAME 2>/dev/null || ps -A",
                timeout=10
            )
            if result:
                for line in result.strip().split("\n"):
                    parts = line.split()
                    if len(parts) >= 2:
                        try:
                            pid = int(parts[0])
                            name = parts[-1]
                            if "." in name and not name.startswith("["):
                                running[name] = pid
                        except ValueError:
                            continue
        except Exception as e:
            logger.debug(f"Could not get running packages: {str(e)}")
        return running
    
    def _parse_package_info(self, package_line: str, is_system: bool, running_packages: Dict[str, int]) -> Optional[Dict]:
        if not package_line.startswith("package:"):
            return None
        
        package_id = package_line.replace("package:", "").strip()
        
        if not self._validate_package_id(package_id):
            logger.warning(f"Invalid package ID format: {package_id}")
            return None
        
        pid = running_packages.get(package_id)
        
        package_info = {
            "package_id": package_id,
            "name": package_id.split(".")[-1].title(),
            "is_system": is_system,
            "pid": pid,
            "is_running": pid is not None,
            "version": None,
            "version_code": None,
            "install_date": None,
            "size_mb": None
        }
        
        return package_info
    
    def list_packages(self, device_serial: str, filter_type: str = "all") -> List[Dict]:
        logger.info(f"Listing packages for {device_serial}, filter={filter_type}")
        
        packages = []
        
        try:
            running_packages = self._get_running_packages(device_serial)
            
            if filter_type == "user":
                result = self.adb_manager.execute_shell(device_serial, "pm list packages -3", timeout=15)
                if result:
                    for line in result.strip().split("\n"):
                        if line.strip():
                            pkg_info = self._parse_package_info(line, False, running_packages)
                            if pkg_info:
                                packages.append(pkg_info)
            
            elif filter_type == "system":
                result = self.adb_manager.execute_shell(device_serial, "pm list packages -s", timeout=15)
                if result:
                    for line in result.strip().split("\n"):
                        if line.strip():
                            pkg_info = self._parse_package_info(line, True, running_packages)
                            if pkg_info:
                                packages.append(pkg_info)
            
            else:
                user_result = self.adb_manager.execute_shell(device_serial, "pm list packages -3", timeout=15)
                if user_result:
                    for line in user_result.strip().split("\n"):
                        if line.strip():
                            pkg_info = self._parse_package_info(line, False, running_packages)
                            if pkg_info:
                                packages.append(pkg_info)
                
                system_result = self.adb_manager.execute_shell(device_serial, "pm list packages -s", timeout=15)
                if system_result:
                    for line in system_result.strip().split("\n"):
                        if line.strip():
                            pkg_info = self._parse_package_info(line, True, running_packages)
                            if pkg_info:
                                packages.append(pkg_info)
            
            packages.sort(key=lambda x: x["name"].lower())
            logger.info(f"Found {len(packages)} packages for {device_serial}")
            
        except Exception as e:
            logger.error(f"Failed to list packages for {device_serial}: {str(e)}")
            raise
        
        return packages
    
    def get_package_details(self, device_serial: str, package_id: str) -> Optional[Dict]:
        logger.info(f"Getting package details for {package_id} on {device_serial}")
        
        if not self._validate_package_id(package_id):
            logger.error(f"Invalid package ID format: {package_id}")
            return None
        
        try:
            details = {
                "package_id": package_id,
                "name": package_id.split(".")[-1].title(),
            }
            
            # Check if system app
            system_check = self.adb_manager.execute_shell(
                device_serial,
                f"pm list packages -s | grep -q 'package:{package_id}$' && echo 'system' || echo 'user'",
                timeout=5
            )
            details["is_system"] = system_check and "system" in system_check
            
            # Get package metadata using targeted grep (much faster than parsing entire dump)
            metadata = self.adb_manager.execute_shell(
                device_serial,
                f"pm dump {package_id} | grep -E 'versionName=|versionCode=|targetSdk=|minSdk=|installerPackageName=|dataDir=' | head -10",
                timeout=10
            )
            
            if not metadata:
                # Fallback: check if package exists
                pkg_check = self.adb_manager.execute_shell(
                    device_serial,
                    f"pm list packages | grep -q 'package:{package_id}$' && echo 'exists'",
                    timeout=5
                )
                if not pkg_check or "exists" not in pkg_check:
                    logger.warning(f"Package {package_id} not found on {device_serial}")
                    return None
            
            version_match = re.search(r'versionName=([^\s]+)', metadata) if metadata else None
            details["version"] = version_match.group(1) if version_match else "unknown"
            
            version_code_match = re.search(r'versionCode=(\d+)', metadata) if metadata else None
            details["version_code"] = int(version_code_match.group(1)) if version_code_match else 0
            
            install_source_match = re.search(r'installerPackageName=([^\s]+)', metadata) if metadata else None
            details["install_source"] = install_source_match.group(1) if install_source_match else "unknown"
            
            target_sdk_match = re.search(r'targetSdk=(\d+)', metadata) if metadata else None
            details["target_sdk"] = int(target_sdk_match.group(1)) if target_sdk_match else 0
            
            min_sdk_match = re.search(r'minSdk=(\d+)', metadata) if metadata else None
            details["min_sdk"] = int(min_sdk_match.group(1)) if min_sdk_match else 0
            
            data_dir_match = re.search(r'dataDir=([^\s]+)', metadata) if metadata else None
            data_dir = data_dir_match.group(1) if data_dir_match else f"/data/data/{package_id}"
            
            # Get APK path
            apk_path_result = self.adb_manager.execute_shell(
                device_serial,
                f"pm path {package_id}",
                timeout=5
            )
            if apk_path_result and apk_path_result.startswith("package:"):
                details["apk_path"] = apk_path_result.replace("package:", "").strip()
            else:
                details["apk_path"] = "unknown"
            
            # Get sizes in a single command for efficiency
            size_cmd = f"du -sm {details['apk_path']} {data_dir} {data_dir}/cache 2>/dev/null || echo '0 0 0'"
            size_output = self.adb_manager.execute_shell(device_serial, size_cmd, timeout=10)
            
            details["size_mb"] = 0.0
            details["data_size_mb"] = 0.0
            details["cache_size_mb"] = 0.0
            
            if size_output:
                lines = size_output.strip().split("\n")
                for i, line in enumerate(lines):
                    parts = line.split()
                    if parts and parts[0].isdigit():
                        size = float(parts[0])
                        if i == 0:
                            details["size_mb"] = size
                        elif i == 1:
                            details["data_size_mb"] = size
                        elif i == 2:
                            details["cache_size_mb"] = size
            
            # Get all unique permissions
            perm_output = self.adb_manager.execute_shell(
                device_serial,
                f"pm dump {package_id} | grep -oE 'android\\.permission\\.[A-Z_]+' | sort -u",
                timeout=15
            )
            permissions = []
            if perm_output:
                permissions = [p.strip() for p in perm_output.strip().split("\n") if p.strip()]
            
            details["permissions"] = permissions
            details["permissions_count"] = len(permissions)
            
            # Signing cert - extract signature hash from pm dump
            sig_output = self.adb_manager.execute_shell(
                device_serial,
                f"pm dump {package_id} | grep -m1 'signatures=' | head -1",
                timeout=5
            )
            if sig_output:
                sig_match = re.search(r'signatures:\[([a-fA-F0-9]+)\]', sig_output)
                if sig_match:
                    details["signing_cert"] = sig_match.group(1)
                else:
                    details["signing_cert"] = "unknown"
            else:
                details["signing_cert"] = "unknown"
            
            # Get main activity using resolve-activity (fast)
            resolve_result = self.adb_manager.execute_shell(
                device_serial,
                f"cmd package resolve-activity --brief -c android.intent.category.LAUNCHER {package_id}",
                timeout=5
            )
            details["main_activity"] = None
            if resolve_result:
                lines = [l.strip() for l in resolve_result.strip().split("\n") if l.strip()]
                for line in lines:
                    if "/" in line and not line.startswith("priority"):
                        activity = line.split("/")[-1] if "/" in line else line
                        details["main_activity"] = activity
                        break
            
            pid = self._get_pid_for_package(device_serial, package_id)
            details["pid"] = pid
            details["is_running"] = pid is not None
            
            logger.info(f"Successfully retrieved details for {package_id}")
            return details
            
        except Exception as e:
            logger.error(f"Failed to get package details for {package_id}: {str(e)}")
            raise
    
    def install_package(self, device_serial: str, apk_source: str, is_local_file: bool = True, device_temp_path: str = "/data/local/tmp/temp_install.apk") -> bool:
        logger.info(f"Installing package on {device_serial} from {apk_source}, local={is_local_file}")
        
        try:
            if is_local_file:
                # Resolve relative paths from project root, not backend directory
                if not os.path.isabs(apk_source):
                    apk_source = str(PROJECT_ROOT / apk_source)
                
                if not os.path.exists(apk_source):
                    logger.error(f"APK file/directory not found: {apk_source}")
                    return False
                
                # Handle split APK (directory with multiple APK files)
                if os.path.isdir(apk_source):
                    return self._install_split_apk(device_serial, apk_source)
                
                # Handle single APK file
                if not apk_source.endswith('.apk'):
                    logger.error(f"File is not an APK: {apk_source}")
                    return False
                
                if not device_temp_path.startswith('/'):
                    logger.error(f"Device temp path must be absolute: {device_temp_path}")
                    return False
                
                logger.info(f"Pushing {apk_source} to {device_temp_path}")
                push_result = self.adb_manager._run_adb_command(
                    ['adb', '-s', device_serial, 'push', apk_source, device_temp_path],
                    timeout=120
                )
                
                if push_result.returncode != 0:
                    logger.error(f"Failed to push APK: {push_result.stderr}")
                    return False
                
                install_result = self.adb_manager.execute_shell(
                    device_serial,
                    f"pm install -r {device_temp_path}",
                    timeout=120
                )
                
                self.adb_manager.execute_shell(device_serial, f"rm {device_temp_path}", timeout=10)
                
                if install_result and "Success" in install_result:
                    logger.info(f"Successfully installed package from {apk_source}")
                    return True
                else:
                    logger.error(f"Installation failed: {install_result}")
                    return False
            
            else:
                if not apk_source.startswith('/'):
                    logger.error(f"Device path must be absolute: {apk_source}")
                    return False
                
                install_result = self.adb_manager.execute_shell(
                    device_serial,
                    f"pm install -r {apk_source}",
                    timeout=120
                )
                
                if install_result and "Success" in install_result:
                    logger.info(f"Successfully installed package from device path {apk_source}")
                    return True
                else:
                    logger.error(f"Installation failed: {install_result}")
                    return False
        
        except Exception as e:
            logger.error(f"Failed to install package: {str(e)}")
            raise
    
    def _install_split_apk(self, device_serial: str, split_apk_dir: str) -> bool:
        logger.info(f"Installing split APK from directory {split_apk_dir}")
        
        try:
            # Find all APK files in the directory
            apk_files = []
            for file in os.listdir(split_apk_dir):
                if file.endswith('.apk'):
                    full_path = os.path.join(split_apk_dir, file)
                    apk_files.append(full_path)
            
            if not apk_files:
                logger.error(f"No APK files found in directory: {split_apk_dir}")
                return False
            
            # Sort to ensure base.apk is first if it exists
            apk_files.sort(key=lambda x: (not os.path.basename(x).startswith('base'), x))
            
            logger.info(f"Found {len(apk_files)} APK files to install")
            
            # Use adb install-multiple for split APKs
            cmd = ['adb', '-s', device_serial, 'install-multiple', '-r'] + apk_files
            
            install_result = self.adb_manager._run_adb_command(cmd, timeout=180)
            
            if install_result.returncode == 0:
                logger.info(f"Successfully installed split APK from {split_apk_dir}")
                return True
            else:
                logger.error(f"Failed to install split APK: {install_result.stderr}")
                return False
        
        except Exception as e:
            logger.error(f"Failed to install split APK: {str(e)}")
            raise
    
    def uninstall_package(self, device_serial: str, package_id: str, keep_data: bool = False) -> bool:
        logger.info(f"Uninstalling {package_id} on {device_serial}, keep_data={keep_data}")
        
        if not self._validate_package_id(package_id):
            logger.error(f"Invalid package ID format: {package_id}")
            return False
        
        try:
            keep_flag = "-k" if keep_data else ""
            command = f"pm uninstall {keep_flag} {package_id}".strip()
            
            result = self.adb_manager.execute_shell(device_serial, command, timeout=60)
            
            if result and "Success" in result:
                logger.info(f"Successfully uninstalled {package_id}")
                return True
            else:
                logger.error(f"Uninstallation failed: {result}")
                return False
        
        except Exception as e:
            logger.error(f"Failed to uninstall package {package_id}: {str(e)}")
            raise
    
    def pull_package(self, device_serial: str, package_id: str, destination_path: str) -> Optional[str]:
        logger.info(f"Pulling {package_id} from {device_serial} to {destination_path}")
        
        if not self._validate_package_id(package_id):
            logger.error(f"Invalid package ID format: {package_id}")
            return None
        
        try:
            apk_path_result = self.adb_manager.execute_shell(
                device_serial,
                f"pm path {package_id}",
                timeout=10
            )
            
            if not apk_path_result or not apk_path_result.startswith("package:"):
                logger.error(f"Could not find APK path for {package_id}")
                return None
            
            # Parse all APK paths (handles split APKs / App Bundles)
            apk_paths = []
            for line in apk_path_result.strip().split("\n"):
                if line.startswith("package:"):
                    apk_paths.append(line.replace("package:", "").strip())
            
            if not apk_paths:
                logger.error(f"No valid APK paths found for {package_id}")
                return None
            
            # Resolve destination directory
            if destination_path.endswith('.apk'):
                dest_dir = os.path.dirname(destination_path)
                base_name = os.path.basename(destination_path).replace('.apk', '')
            else:
                dest_dir = destination_path
                base_name = package_id
            
            if not os.path.isabs(dest_dir):
                dest_dir = str(PROJECT_ROOT / dest_dir)
            else:
                dest_dir = os.path.abspath(dest_dir)
            
            if dest_dir:
                os.makedirs(dest_dir, exist_ok=True)
            
            # Single APK - simple pull
            if len(apk_paths) == 1:
                final_path = os.path.join(dest_dir, f"{base_name}.apk")
                pull_result = self.adb_manager._run_adb_command(
                    ['adb', '-s', device_serial, 'pull', apk_paths[0], final_path],
                    timeout=120
                )
                
                if pull_result.returncode == 0:
                    logger.info(f"Successfully pulled {package_id} to {final_path}")
                    return final_path
                else:
                    logger.error(f"Failed to pull package: {pull_result.stderr}")
                    return None
            
            # Split APK (App Bundle) - pull all parts to a subdirectory
            split_dir = os.path.join(dest_dir, base_name)
            os.makedirs(split_dir, exist_ok=True)
            
            pulled_files = []
            for apk_path in apk_paths:
                apk_name = os.path.basename(apk_path)
                local_path = os.path.join(split_dir, apk_name)
                
                pull_result = self.adb_manager._run_adb_command(
                    ['adb', '-s', device_serial, 'pull', apk_path, local_path],
                    timeout=120
                )
                
                if pull_result.returncode == 0:
                    pulled_files.append(local_path)
                    logger.debug(f"Pulled split APK: {apk_name}")
                else:
                    logger.warning(f"Failed to pull split APK {apk_name}: {pull_result.stderr}")
            
            if pulled_files:
                logger.info(f"Successfully pulled {package_id} ({len(pulled_files)} split APKs) to {split_dir}")
                return split_dir
            else:
                logger.error(f"Failed to pull any APK files for {package_id}")
                return None
        
        except Exception as e:
            logger.error(f"Failed to pull package {package_id}: {str(e)}")
            raise
    
    def launch_package(self, device_serial: str, package_id: str) -> bool:
        logger.info(f"Launching {package_id} on {device_serial}")
        
        if not self._validate_package_id(package_id):
            logger.error(f"Invalid package ID format: {package_id}")
            return False
        
        try:
            # Use monkey command - fastest and most reliable way to launch an app
            launch_result = self.adb_manager.execute_shell(
                device_serial,
                f"monkey -p {package_id} -c android.intent.category.LAUNCHER 1",
                timeout=10
            )
            
            if launch_result and "Events injected" in launch_result:
                logger.info(f"Launched {package_id} using monkey")
                return True
            
            # Fallback: try cmd package resolve-activity (fast, no huge output)
            resolve_result = self.adb_manager.execute_shell(
                device_serial,
                f"cmd package resolve-activity --brief -c android.intent.category.LAUNCHER {package_id}",
                timeout=5
            )
            
            if resolve_result:
                lines = [l.strip() for l in resolve_result.strip().split("\n") if l.strip()]
                for line in lines:
                    if "/" in line and not line.startswith("priority"):
                        activity_name = line.strip()
                        launch_result = self.adb_manager.execute_shell(
                            device_serial,
                            f"am start -n {activity_name}",
                            timeout=10
                        )
                        if launch_result and ("Starting" in launch_result or "Warning" in launch_result):
                            logger.info(f"Successfully launched {package_id}")
                            return True
            
            # Final fallback: use am start with package intent
            launch_result = self.adb_manager.execute_shell(
                device_serial,
                f"am start -a android.intent.action.MAIN -c android.intent.category.LAUNCHER {package_id}",
                timeout=10
            )
            
            if launch_result and ("Starting" in launch_result or "Warning" in launch_result):
                logger.info(f"Successfully launched {package_id} via intent")
                return True
            
            logger.error(f"Could not launch {package_id}: no launchable activity found")
            return False
        
        except Exception as e:
            logger.error(f"Failed to launch package {package_id}: {str(e)}")
            raise
    
    def force_stop(self, device_serial: str, package_id: str) -> bool:
        logger.info(f"Force stopping {package_id} on {device_serial}")
        
        if not self._validate_package_id(package_id):
            logger.error(f"Invalid package ID format: {package_id}")
            return False
        
        try:
            self.adb_manager.execute_shell(
                device_serial,
                f"am force-stop {package_id}",
                timeout=10
            )
            
            pid = self._get_pid_for_package(device_serial, package_id)
            if pid is None:
                logger.info(f"Successfully force stopped {package_id}")
                return True
            else:
                logger.warning(f"Force stop command executed but process still running: PID {pid}")
                return True
        
        except Exception as e:
            logger.error(f"Failed to force stop {package_id}: {str(e)}")
            raise
    
    def clear_cache(self, device_serial: str, package_id: str) -> bool:
        logger.info(f"Clearing cache for {package_id} on {device_serial}")
        
        if not self._validate_package_id(package_id):
            logger.error(f"Invalid package ID format: {package_id}")
            return False
        
        try:
            # Get the cache directory path
            cache_dir = f"/data/data/{package_id}/cache"
            
            # Try to clear cache using run-as (works for debuggable apps)
            result = self.adb_manager.execute_shell(
                device_serial,
                f"run-as {package_id} rm -rf {cache_dir}/* 2>/dev/null; "
                f"rm -rf {cache_dir}/* 2>/dev/null; "
                f"rm -rf /data/user/0/{package_id}/cache/* 2>/dev/null; "
                "echo done",
                timeout=15
            )
            
            logger.info(f"Cache cleared for {package_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to clear cache for {package_id}: {str(e)}")
            raise
    
    def clear_data(self, device_serial: str, package_id: str) -> bool:
        logger.info(f"Clearing data for {package_id} on {device_serial}")
        
        if not self._validate_package_id(package_id):
            logger.error(f"Invalid package ID format: {package_id}")
            return False
        
        try:
            result = self.adb_manager.execute_shell(
                device_serial,
                f"pm clear {package_id}",
                timeout=30
            )
            
            if result and "Success" in result:
                logger.info(f"Successfully cleared data for {package_id}")
                return True
            else:
                logger.error(f"Failed to clear data: {result}")
                return False
        
        except Exception as e:
            logger.error(f"Failed to clear data for {package_id}: {str(e)}")
            raise

