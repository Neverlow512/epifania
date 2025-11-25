# Comprehensive ADB diagnostics module for device testing

from typing import Dict, List, Optional
from core.logger import get_logger

logger = get_logger(__name__, "device")

try:
    from core.log_streamer import log_streamer
    LOG_STREAMER_AVAILABLE = True
except ImportError:
    LOG_STREAMER_AVAILABLE = False


class DeviceDiagnostics:
    def __init__(self, adb_manager):
        self.adb_manager = adb_manager
        logger.info("DeviceDiagnostics initialized")
    
    def run_full_diagnostics(self, device_serial: str) -> Dict:
        logger.info(f"Running full diagnostics for device {device_serial}")
        
        if LOG_STREAMER_AVAILABLE:
            log_streamer.add_log(device_serial, "device_logs", "Starting comprehensive ADB diagnostics", "info")
        
        results = {
            "device_id": device_serial,
            "timestamp": "",
            "tests": []
        }
        
        from datetime import datetime
        results["timestamp"] = datetime.now().isoformat()
        
        # Run all diagnostic tests
        results["tests"].append(self.test_shell_connectivity(device_serial))
        results["tests"].append(self.test_root_access(device_serial))
        results["tests"].append(self.test_write_permissions(device_serial))
        results["tests"].append(self.test_selinux_status(device_serial))
        results["tests"].append(self.test_storage_space(device_serial))
        results["tests"].append(self.test_adb_version(device_serial))
        
        # Calculate overall status
        passed = sum(1 for test in results["tests"] if test["status"] == "pass")
        total = len(results["tests"])
        results["summary"] = {
            "passed": passed,
            "failed": total - passed,
            "total": total,
            "overall_status": "pass" if passed == total else "warning" if passed > 0 else "fail"
        }
        
        if LOG_STREAMER_AVAILABLE:
            log_streamer.add_log(
                device_serial, 
                "device_logs", 
                f"Diagnostics complete: {passed}/{total} tests passed", 
                "info" if passed == total else "warning"
            )
        
        logger.info(f"Diagnostics complete for {device_serial}: {passed}/{total} tests passed")
        return results
    
    def test_shell_connectivity(self, device_serial: str) -> Dict:
        test_result = {
            "name": "Shell Connectivity",
            "description": "Tests basic ADB shell command execution",
            "status": "fail",
            "message": "",
            "details": {}
        }
        
        try:
            result = self.adb_manager.execute_shell(device_serial, "echo 'connectivity_test'")
            if result and "connectivity_test" in result:
                test_result["status"] = "pass"
                test_result["message"] = "Shell commands execute successfully"
                test_result["details"]["response"] = result.strip()
            else:
                test_result["message"] = "Shell command did not return expected output"
                test_result["details"]["response"] = result
                
            if LOG_STREAMER_AVAILABLE:
                log_streamer.add_log(device_serial, "adb_operations", "shell: echo 'connectivity_test'", "debug")
                
        except Exception as e:
            test_result["message"] = f"Shell connectivity failed: {str(e)}"
            test_result["details"]["error"] = str(e)
            logger.error(f"Shell connectivity test failed for {device_serial}: {str(e)}")
        
        return test_result
    
    def test_root_access(self, device_serial: str) -> Dict:
        test_result = {
            "name": "Root Access",
            "description": "Checks if device has root access available",
            "status": "fail",
            "message": "",
            "details": {}
        }
        
        try:
            result = self.adb_manager.execute_shell(device_serial, "su -c 'id'")
            if result and "uid=0" in result:
                test_result["status"] = "pass"
                test_result["message"] = "Root access is available"
                test_result["details"]["uid"] = "0 (root)"
            else:
                test_result["status"] = "warning"
                test_result["message"] = "Root access not available (may limit Frida functionality)"
                test_result["details"]["note"] = "Some Frida operations may require root"
                
            if LOG_STREAMER_AVAILABLE:
                log_streamer.add_log(device_serial, "adb_operations", "shell: su -c 'id'", "debug")
                
        except Exception as e:
            test_result["status"] = "warning"
            test_result["message"] = "Root access not available"
            test_result["details"]["error"] = str(e)
            logger.debug(f"Root access test failed for {device_serial}: {str(e)}")
        
        return test_result
    
    def test_write_permissions(self, device_serial: str) -> Dict:
        test_result = {
            "name": "Write Permissions",
            "description": "Tests write access to /data/local/tmp directory",
            "status": "fail",
            "message": "",
            "details": {}
        }
        
        try:
            test_file = "/data/local/tmp/.epifania_write_test"
            
            # Try to write a test file
            result = self.adb_manager.execute_shell(device_serial, f"echo 'test' > {test_file} && cat {test_file} && rm {test_file}")
            
            if result and "test" in result:
                test_result["status"] = "pass"
                test_result["message"] = "Write permissions to /data/local/tmp are available"
                test_result["details"]["path"] = "/data/local/tmp"
            else:
                test_result["message"] = "Cannot write to /data/local/tmp"
                test_result["details"]["error"] = "Write test failed"
                
            if LOG_STREAMER_AVAILABLE:
                log_streamer.add_log(device_serial, "adb_operations", f"shell: write test to {test_file}", "debug")
                
        except Exception as e:
            test_result["message"] = f"Write permission test failed: {str(e)}"
            test_result["details"]["error"] = str(e)
            logger.error(f"Write permission test failed for {device_serial}: {str(e)}")
        
        return test_result
    
    def test_selinux_status(self, device_serial: str) -> Dict:
        test_result = {
            "name": "SELinux Status",
            "description": "Checks SELinux enforcement mode",
            "status": "pass",
            "message": "",
            "details": {}
        }
        
        try:
            result = self.adb_manager.execute_shell(device_serial, "getenforce")
            if result:
                mode = result.strip()
                test_result["details"]["mode"] = mode
                
                if mode.lower() == "enforcing":
                    test_result["status"] = "warning"
                    test_result["message"] = "SELinux is enforcing (may require additional permissions)"
                    test_result["details"]["note"] = "Consider setting to permissive for Frida: setenforce 0"
                elif mode.lower() == "permissive":
                    test_result["status"] = "pass"
                    test_result["message"] = "SELinux is permissive (optimal for Frida)"
                else:
                    test_result["status"] = "pass"
                    test_result["message"] = f"SELinux mode: {mode}"
            else:
                test_result["status"] = "pass"
                test_result["message"] = "SELinux status unknown or not available"
                
            if LOG_STREAMER_AVAILABLE:
                log_streamer.add_log(device_serial, "adb_operations", "shell: getenforce", "debug")
                
        except Exception as e:
            test_result["status"] = "pass"
            test_result["message"] = "SELinux check not available"
            test_result["details"]["note"] = "This is normal for some devices"
            logger.debug(f"SELinux test failed for {device_serial}: {str(e)}")
        
        return test_result
    
    def test_storage_space(self, device_serial: str) -> Dict:
        test_result = {
            "name": "Storage Space",
            "description": "Checks available storage in /data partition",
            "status": "fail",
            "message": "",
            "details": {}
        }
        
        try:
            result = self.adb_manager.execute_shell(device_serial, "df /data | tail -1")
            if result:
                parts = result.split()
                if len(parts) >= 4:
                    available = parts[3]
                    usage_percent = parts[4] if len(parts) > 4 else "N/A"
                    
                    test_result["details"]["available"] = available
                    test_result["details"]["usage"] = usage_percent
                    
                    # Try to extract numeric value (handle K, M, G suffixes)
                    try:
                        avail_str = available.rstrip('KMG')
                        avail_num = float(avail_str)
                        suffix = available[-1] if available[-1] in 'KMG' else 'K'
                        
                        # Convert to MB
                        if suffix == 'K':
                            avail_mb = avail_num / 1024
                        elif suffix == 'M':
                            avail_mb = avail_num
                        else:  # G
                            avail_mb = avail_num * 1024
                        
                        if avail_mb < 50:
                            test_result["status"] = "warning"
                            test_result["message"] = f"Low storage space: {available} available"
                            test_result["details"]["note"] = "Consider freeing up space"
                        else:
                            test_result["status"] = "pass"
                            test_result["message"] = f"Sufficient storage: {available} available"
                    except:
                        test_result["status"] = "pass"
                        test_result["message"] = f"Storage available: {available}"
                else:
                    test_result["status"] = "pass"
                    test_result["message"] = "Storage information available"
            else:
                test_result["status"] = "warning"
                test_result["message"] = "Could not determine storage space"
                
            if LOG_STREAMER_AVAILABLE:
                log_streamer.add_log(device_serial, "adb_operations", "shell: df /data", "debug")
                
        except Exception as e:
            test_result["status"] = "warning"
            test_result["message"] = "Storage check failed"
            test_result["details"]["error"] = str(e)
            logger.debug(f"Storage test failed for {device_serial}: {str(e)}")
        
        return test_result
    
    def test_adb_version(self, device_serial: str) -> Dict:
        test_result = {
            "name": "ADB Version",
            "description": "Checks ADB daemon version on device",
            "status": "pass",
            "message": "",
            "details": {}
        }
        
        try:
            # Use subprocess to get adb version
            import subprocess
            result = subprocess.run(
                ['adb', 'version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version_info = result.stdout.strip().split('\n')[0]
                test_result["details"]["version"] = version_info
                test_result["message"] = f"ADB version: {version_info}"
                test_result["status"] = "pass"
            else:
                test_result["status"] = "warning"
                test_result["message"] = "Could not determine ADB version"
                
        except Exception as e:
            test_result["status"] = "warning"
            test_result["message"] = "Could not determine ADB version"
            test_result["details"]["error"] = str(e)
            logger.debug(f"ADB version test failed: {str(e)}")
        
        return test_result

