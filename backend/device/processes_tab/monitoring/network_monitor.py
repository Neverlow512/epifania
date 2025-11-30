# Network monitoring for Android devices via ADB

from typing import Dict, List, Optional
from collections import defaultdict, deque
import time
from core.logger import get_logger
from core.adb_manager import ADBManager
from device.processes_tab.monitoring.cache import device_metrics_cache

logger = get_logger(__name__, "device")


class NetworkMonitor:
    def __init__(self, adb_manager: ADBManager):
        self.adb_manager = adb_manager
        self._previous_bytes: Dict[str, Dict] = defaultdict(dict)
        self._previous_timestamps: Dict[str, float] = {}
        # Track recent endpoints with timestamps (max 100 entries per device)
        self._recent_endpoints: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        logger.info("NetworkMonitor initialized")
    
    def get_network_stats(self, device_serial: str, focused_pid: Optional[int] = None) -> Dict:
        # Use cache to prevent race conditions from concurrent requests
        cache_key = f"network:{device_serial}:{focused_pid or 'none'}"
        
        def compute():
            try:
                throughput = self._get_throughput(device_serial)
                endpoints = self._get_recent_endpoints(device_serial)
                
                result = {
                    "throughput": throughput,
                    "recent_endpoints": endpoints
                }
                
                if focused_pid:
                    focused = self._get_process_connections(device_serial, focused_pid)
                    if focused:
                        result["focused_process"] = focused
                
                return result
                
            except Exception as e:
                logger.error(f"Failed to get network stats for {device_serial}: {str(e)}")
                return {
                    "throughput": {
                        "bytes_sent_per_sec": 0,
                        "bytes_recv_per_sec": 0
                    },
                    "recent_endpoints": []
                }
        
        return device_metrics_cache.get_or_compute(cache_key, compute, ttl=1.5)
    
    def _get_throughput(self, device_serial: str) -> Dict:
        try:
            result = self.adb_manager.execute_shell(
                device_serial,
                "cat /proc/net/dev"
            )
            
            if not result:
                return {"bytes_sent_per_sec": 0, "bytes_recv_per_sec": 0}
            
            total_recv = 0
            total_sent = 0
            
            for line in result.strip().split('\n'):
                if ':' not in line:
                    continue
                
                parts = line.split(':')
                if len(parts) < 2:
                    continue
                
                interface = parts[0].strip()
                # Skip loopback
                if interface == "lo":
                    continue
                
                stats = parts[1].split()
                if len(stats) < 10:
                    continue
                
                try:
                    recv_bytes = int(stats[0])
                    sent_bytes = int(stats[8])
                    total_recv += recv_bytes
                    total_sent += sent_bytes
                except (ValueError, IndexError):
                    continue
            
            current_time = time.time()
            prev = self._previous_bytes.get(device_serial, {})
            prev_time = self._previous_timestamps.get(device_serial, 0)
            
            self._previous_bytes[device_serial] = {
                "recv": total_recv,
                "sent": total_sent
            }
            self._previous_timestamps[device_serial] = current_time
            
            if not prev or "recv" not in prev or prev_time == 0:
                return {"bytes_sent_per_sec": 0, "bytes_recv_per_sec": 0}
            
            time_diff = current_time - prev_time
            if time_diff <= 0:
                return {"bytes_sent_per_sec": 0, "bytes_recv_per_sec": 0}
            
            recv_diff = total_recv - prev["recv"]
            sent_diff = total_sent - prev["sent"]
            
            # Handle counter wrap-around
            if recv_diff < 0:
                recv_diff = total_recv
            if sent_diff < 0:
                sent_diff = total_sent
            
            return {
                "bytes_sent_per_sec": int(sent_diff / time_diff),
                "bytes_recv_per_sec": int(recv_diff / time_diff)
            }
            
        except Exception as e:
            logger.error(f"Failed to get throughput for {device_serial}: {str(e)}")
            return {"bytes_sent_per_sec": 0, "bytes_recv_per_sec": 0}
    
    def _get_process_connections(self, device_serial: str, pid: int) -> Optional[Dict]:
        try:
            connections = []
            
            # Get TCP connections for the process
            tcp_result = self.adb_manager.execute_shell(
                device_serial,
                f"cat /proc/{pid}/net/tcp /proc/{pid}/net/tcp6 2>/dev/null"
            )
            
            if tcp_result:
                connections = self._parse_tcp_connections(tcp_result)
            
            # Update recent endpoints
            current_time = time.time()
            for conn in connections:
                if conn.get("remote") and conn["remote"] != "0.0.0.0:0":
                    self._recent_endpoints[device_serial].append({
                        "endpoint": conn["remote"],
                        "timestamp": current_time,
                        "pid": pid
                    })
            
            return {
                "pid": pid,
                "tcp_connections": len(connections),
                "connections": connections[:20]  # Limit to 20 connections
            }
            
        except Exception as e:
            logger.error(f"Failed to get connections for PID {pid}: {str(e)}")
            return None
    
    def _parse_tcp_connections(self, tcp_output: str) -> List[Dict]:
        connections = []
        
        # TCP state mapping
        states = {
            "01": "ESTABLISHED",
            "02": "SYN_SENT",
            "03": "SYN_RECV",
            "04": "FIN_WAIT1",
            "05": "FIN_WAIT2",
            "06": "TIME_WAIT",
            "07": "CLOSE",
            "08": "CLOSE_WAIT",
            "09": "LAST_ACK",
            "0A": "LISTEN",
            "0B": "CLOSING"
        }
        
        for line in tcp_output.strip().split('\n'):
            line = line.strip()
            
            # Skip header lines
            if line.startswith("sl") or not line:
                continue
            
            parts = line.split()
            if len(parts) < 4:
                continue
            
            try:
                local_addr = self._decode_address(parts[1])
                remote_addr = self._decode_address(parts[2])
                state_hex = parts[3].upper()
                state = states.get(state_hex, "UNKNOWN")
                
                connections.append({
                    "local": local_addr,
                    "remote": remote_addr,
                    "state": state
                })
            except (ValueError, IndexError):
                continue
        
        return connections
    
    def _decode_address(self, addr_hex: str) -> str:
        # Decode hex address format: IP:PORT (e.g., "0100007F:0050" -> "127.0.0.1:80")
        try:
            ip_hex, port_hex = addr_hex.split(':')
            
            # Handle IPv4 (8 hex chars) and IPv6 (32 hex chars)
            if len(ip_hex) == 8:
                # IPv4 - little endian
                ip_int = int(ip_hex, 16)
                ip = ".".join([
                    str((ip_int >> 0) & 0xFF),
                    str((ip_int >> 8) & 0xFF),
                    str((ip_int >> 16) & 0xFF),
                    str((ip_int >> 24) & 0xFF)
                ])
            elif len(ip_hex) == 32:
                # IPv6 - simplified display
                ip = "::1" if ip_hex == "00000000000000000000000001000000" else f"ipv6:{ip_hex[:8]}..."
            else:
                ip = "unknown"
            
            port = int(port_hex, 16)
            return f"{ip}:{port}"
            
        except (ValueError, IndexError):
            return "unknown:0"
    
    def _get_recent_endpoints(self, device_serial: str, max_age: int = 300) -> List[Dict]:
        # Get endpoints from the last max_age seconds
        try:
            current_time = time.time()
            cutoff = current_time - max_age
            
            # Count endpoints
            endpoint_counts: Dict[str, int] = defaultdict(int)
            
            for entry in self._recent_endpoints[device_serial]:
                if entry["timestamp"] >= cutoff:
                    endpoint = entry["endpoint"]
                    # Extract just IP:port
                    endpoint_counts[endpoint] += 1
            
            # Sort by count and return top 10
            sorted_endpoints = sorted(
                endpoint_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            result = []
            for endpoint, count in sorted_endpoints:
                try:
                    ip, port = endpoint.rsplit(':', 1)
                    result.append({
                        "ip": ip,
                        "port": int(port),
                        "count": count
                    })
                except (ValueError, IndexError):
                    result.append({
                        "ip": endpoint,
                        "port": 0,
                        "count": count
                    })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get recent endpoints: {str(e)}")
            return []
    
    def get_all_connections(self, device_serial: str) -> List[Dict]:
        # Get all TCP connections on the device (requires root for full visibility)
        try:
            result = self.adb_manager.execute_shell(
                device_serial,
                "cat /proc/net/tcp /proc/net/tcp6 2>/dev/null"
            )
            
            if not result:
                return []
            
            connections = self._parse_tcp_connections(result)
            
            # Update recent endpoints
            current_time = time.time()
            for conn in connections:
                if conn.get("remote") and conn["remote"] != "0.0.0.0:0":
                    self._recent_endpoints[device_serial].append({
                        "endpoint": conn["remote"],
                        "timestamp": current_time,
                        "pid": 0
                    })
            
            return connections
            
        except Exception as e:
            logger.error(f"Failed to get all connections: {str(e)}")
            return []

