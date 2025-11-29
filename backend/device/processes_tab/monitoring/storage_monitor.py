# Storage monitoring for Android devices via ADB

from typing import Dict, List
from core.logger import get_logger
from core.adb_manager import ADBManager

logger = get_logger(__name__, "device")


class StorageMonitor:
    def __init__(self, adb_manager: ADBManager):
        self.adb_manager = adb_manager
        logger.info("StorageMonitor initialized")
    
    def get_storage_stats(self, device_serial: str, partition: str = "/data") -> Dict:
        try:
            result = self._get_partition_info(device_serial, partition)
            return result
        except Exception as e:
            logger.error(f"Failed to get storage stats for {device_serial}: {str(e)}")
            return {
                "partition": partition,
                "total_gb": 0.0,
                "used_gb": 0.0,
                "free_gb": 0.0,
                "percent_used": 0.0
            }
    
    def get_all_partitions(self, device_serial: str) -> List[Dict]:
        try:
            result = self.adb_manager.execute_shell(
                device_serial,
                "df -h 2>/dev/null"
            )
            
            if not result:
                return []
            
            partitions = []
            lines = result.strip().split('\n')
            
            for line in lines[1:]:
                parts = line.split()
                if len(parts) < 6:
                    continue
                
                mount_point = parts[-1]
                
                # Filter to relevant partitions
                if not any(p in mount_point for p in ["/data", "/system", "/storage", "/sdcard"]):
                    continue
                
                try:
                    total = self._parse_size(parts[1])
                    used = self._parse_size(parts[2])
                    free = self._parse_size(parts[3])
                    percent_str = parts[4].replace('%', '')
                    percent = float(percent_str) if percent_str.isdigit() else 0.0
                    
                    partitions.append({
                        "partition": mount_point,
                        "filesystem": parts[0],
                        "total_gb": total,
                        "used_gb": used,
                        "free_gb": free,
                        "percent_used": percent
                    })
                except (ValueError, IndexError):
                    continue
            
            return partitions
            
        except Exception as e:
            logger.error(f"Failed to get all partitions for {device_serial}: {str(e)}")
            return []
    
    def _get_partition_info(self, device_serial: str, partition: str) -> Dict:
        try:
            result = self.adb_manager.execute_shell(
                device_serial,
                f"df {partition} 2>/dev/null"
            )
            
            if not result:
                return self._fallback_partition_info(device_serial, partition)
            
            lines = result.strip().split('\n')
            if len(lines) < 2:
                return self._fallback_partition_info(device_serial, partition)
            
            # Parse df output (may be in 1K blocks or human-readable)
            data_line = lines[1]
            parts = data_line.split()
            
            if len(parts) < 4:
                return self._fallback_partition_info(device_serial, partition)
            
            # Try to detect if output is in 1K blocks or human-readable
            try:
                # Check if second field looks like a number (1K blocks) or has suffix (human-readable)
                if parts[1][-1].isalpha():
                    # Human-readable format
                    total = self._parse_size(parts[1])
                    used = self._parse_size(parts[2])
                    free = self._parse_size(parts[3])
                else:
                    # 1K blocks format
                    total = int(parts[1]) / (1024 * 1024)
                    used = int(parts[2]) / (1024 * 1024)
                    free = int(parts[3]) / (1024 * 1024)
                
                percent_used = (used / total * 100) if total > 0 else 0.0
                
                return {
                    "partition": partition,
                    "total_gb": round(total, 2),
                    "used_gb": round(used, 2),
                    "free_gb": round(free, 2),
                    "percent_used": round(percent_used, 1)
                }
                
            except (ValueError, IndexError, ZeroDivisionError):
                return self._fallback_partition_info(device_serial, partition)
            
        except Exception as e:
            logger.error(f"Failed to get partition info for {partition}: {str(e)}")
            return {
                "partition": partition,
                "total_gb": 0.0,
                "used_gb": 0.0,
                "free_gb": 0.0,
                "percent_used": 0.0
            }
    
    def _fallback_partition_info(self, device_serial: str, partition: str) -> Dict:
        # Try with -k flag for 1K blocks
        try:
            result = self.adb_manager.execute_shell(
                device_serial,
                f"df -k {partition} 2>/dev/null"
            )
            
            if not result:
                return {
                    "partition": partition,
                    "total_gb": 0.0,
                    "used_gb": 0.0,
                    "free_gb": 0.0,
                    "percent_used": 0.0
                }
            
            lines = result.strip().split('\n')
            if len(lines) < 2:
                return {
                    "partition": partition,
                    "total_gb": 0.0,
                    "used_gb": 0.0,
                    "free_gb": 0.0,
                    "percent_used": 0.0
                }
            
            parts = lines[1].split()
            if len(parts) < 4:
                return {
                    "partition": partition,
                    "total_gb": 0.0,
                    "used_gb": 0.0,
                    "free_gb": 0.0,
                    "percent_used": 0.0
                }
            
            # Values in 1K blocks
            total_kb = int(parts[1])
            used_kb = int(parts[2])
            free_kb = int(parts[3])
            
            total_gb = total_kb / (1024 * 1024)
            used_gb = used_kb / (1024 * 1024)
            free_gb = free_kb / (1024 * 1024)
            percent_used = (used_gb / total_gb * 100) if total_gb > 0 else 0.0
            
            return {
                "partition": partition,
                "total_gb": round(total_gb, 2),
                "used_gb": round(used_gb, 2),
                "free_gb": round(free_gb, 2),
                "percent_used": round(percent_used, 1)
            }
            
        except Exception as e:
            logger.debug(f"Fallback partition info failed: {str(e)}")
            return {
                "partition": partition,
                "total_gb": 0.0,
                "used_gb": 0.0,
                "free_gb": 0.0,
                "percent_used": 0.0
            }
    
    def _parse_size(self, size_str: str) -> float:
        # Parse human-readable sizes like "64G", "500M", "1.2T"
        try:
            size_str = size_str.strip().upper()
            
            if not size_str:
                return 0.0
            
            multipliers = {
                'K': 1 / (1024 * 1024),
                'M': 1 / 1024,
                'G': 1,
                'T': 1024
            }
            
            suffix = size_str[-1]
            if suffix in multipliers:
                value = float(size_str[:-1])
                return value * multipliers[suffix]
            else:
                # Assume bytes if no suffix
                return float(size_str) / (1024 * 1024 * 1024)
                
        except (ValueError, IndexError):
            return 0.0

