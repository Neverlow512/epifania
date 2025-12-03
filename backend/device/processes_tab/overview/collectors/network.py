# Process network collector - TCP/UDP/Unix connections owned by specific PID

from typing import Dict, List, Optional, Set
from core.logger import get_logger
from core.adb_manager import ADBManager
import re

logger = get_logger(__name__, "device")

TCP_STATES = {
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
    "0B": "CLOSING",
}

UNIX_SOCKET_TYPES = {
    "0001": "STREAM",
    "0002": "DGRAM",
    "0005": "SEQPACKET",
}

UNIX_SOCKET_STATES = {
    "01": "LISTENING",
    "02": "CONNECTING",
    "03": "CONNECTED",
    "04": "DISCONNECTING",
}


class NetworkCollector:
    def __init__(self, adb_manager: ADBManager):
        self.adb_manager = adb_manager

    def collect(self, device_serial: str, pid: int) -> Optional[Dict]:
        try:
            # Get socket inodes owned by this process
            socket_inodes = self._get_process_socket_inodes(device_serial, pid)

            tcp_connections = self._get_tcp_connections(device_serial, socket_inodes)
            tcp6_connections = self._get_tcp6_connections(device_serial, socket_inodes)
            udp_connections = self._get_udp_connections(device_serial, socket_inodes)
            udp6_connections = self._get_udp6_connections(device_serial, socket_inodes)
            unix_sockets = self._get_unix_sockets(device_serial, socket_inodes)

            all_tcp = tcp_connections + tcp6_connections
            all_udp = udp_connections + udp6_connections

            state_summary = {}
            for conn in all_tcp:
                state = conn.get("state", "UNKNOWN")
                state_summary[state] = state_summary.get(state, 0) + 1

            return {
                "tcp_count": len(all_tcp),
                "udp_count": len(all_udp),
                "unix_count": len(unix_sockets),
                "total_count": len(all_tcp) + len(all_udp) + len(unix_sockets),
                "tcp_connections": all_tcp[:50],
                "udp_connections": all_udp[:50],
                "unix_sockets": unix_sockets[:50],
                "state_summary": state_summary,
                "truncated": len(all_tcp) > 50 or len(all_udp) > 50 or len(unix_sockets) > 50,
            }

        except Exception as e:
            logger.error(f"Failed to collect network for PID {pid}: {str(e)}")
            return None

    def _get_process_socket_inodes(self, device_serial: str, pid: int) -> Set[str]:
        # Get all file descriptors and extract socket inodes
        result = self.adb_manager.execute_shell(
            device_serial,
            f"ls -la /proc/{pid}/fd 2>/dev/null | grep socket"
        )
        if not result:
            return set()

        inodes = set()
        socket_pattern = re.compile(r'socket:\[(\d+)\]')
        for line in result.strip().split("\n"):
            match = socket_pattern.search(line)
            if match:
                inodes.add(match.group(1))

        return inodes

    def _get_tcp_connections(self, device_serial: str, socket_inodes: Set[str]) -> List[Dict]:
        result = self.adb_manager.execute_shell(
            device_serial,
            "cat /proc/net/tcp 2>/dev/null"
        )
        return self._parse_tcp_output(result, socket_inodes, is_ipv6=False) if result else []

    def _get_tcp6_connections(self, device_serial: str, socket_inodes: Set[str]) -> List[Dict]:
        result = self.adb_manager.execute_shell(
            device_serial,
            "cat /proc/net/tcp6 2>/dev/null"
        )
        return self._parse_tcp_output(result, socket_inodes, is_ipv6=True) if result else []

    def _get_udp_connections(self, device_serial: str, socket_inodes: Set[str]) -> List[Dict]:
        result = self.adb_manager.execute_shell(
            device_serial,
            "cat /proc/net/udp 2>/dev/null"
        )
        return self._parse_udp_output(result, socket_inodes, is_ipv6=False) if result else []

    def _get_udp6_connections(self, device_serial: str, socket_inodes: Set[str]) -> List[Dict]:
        result = self.adb_manager.execute_shell(
            device_serial,
            "cat /proc/net/udp6 2>/dev/null"
        )
        return self._parse_udp_output(result, socket_inodes, is_ipv6=True) if result else []

    def _get_unix_sockets(self, device_serial: str, socket_inodes: Set[str]) -> List[Dict]:
        result = self.adb_manager.execute_shell(
            device_serial,
            "cat /proc/net/unix 2>/dev/null"
        )
        return self._parse_unix_output(result, socket_inodes) if result else []

    def _parse_unix_output(self, output: str, socket_inodes: Set[str]) -> List[Dict]:
        sockets = []

        for line in output.strip().split("\n"):
            line = line.strip()
            if line.startswith("Num") or not line:
                continue

            parts = line.split()
            # Format: Num RefCount Protocol Flags Type St Inode Path
            if len(parts) < 7:
                continue

            try:
                inode = parts[6]
                if inode not in socket_inodes:
                    continue

                socket_type = UNIX_SOCKET_TYPES.get(parts[4], "UNKNOWN")
                state = UNIX_SOCKET_STATES.get(parts[5], "UNKNOWN")
                path = parts[7] if len(parts) > 7 else ""

                # Clean up abstract socket paths (start with @)
                if path.startswith("@"):
                    path = path  # Keep as-is, @ indicates abstract namespace

                sockets.append({
                    "protocol": "unix",
                    "type": socket_type,
                    "state": state,
                    "inode": inode,
                    "path": path,
                })
            except (ValueError, IndexError):
                continue

        return sockets

    def _parse_tcp_output(self, output: str, socket_inodes: Set[str], is_ipv6: bool) -> List[Dict]:
        connections = []

        for line in output.strip().split("\n"):
            line = line.strip()
            if line.startswith("sl") or not line:
                continue

            parts = line.split()
            # Format: sl local_addr rem_addr st tx_queue rx_queue tr tm->when retrnsmt uid timeout inode
            if len(parts) < 10:
                continue

            try:
                inode = parts[9]
                # Filter: only include connections owned by this process
                if inode not in socket_inodes:
                    continue

                local_addr = self._decode_address(parts[1], is_ipv6)
                remote_addr = self._decode_address(parts[2], is_ipv6)
                state_hex = parts[3].upper()
                state = TCP_STATES.get(state_hex, "UNKNOWN")

                connections.append({
                    "protocol": "tcp6" if is_ipv6 else "tcp",
                    "local_address": local_addr["ip"],
                    "local_port": local_addr["port"],
                    "remote_address": remote_addr["ip"],
                    "remote_port": remote_addr["port"],
                    "state": state,
                    "inode": inode,
                })
            except (ValueError, IndexError):
                continue

        return connections

    def _parse_udp_output(self, output: str, socket_inodes: Set[str], is_ipv6: bool) -> List[Dict]:
        connections = []

        for line in output.strip().split("\n"):
            line = line.strip()
            if line.startswith("sl") or not line:
                continue

            parts = line.split()
            # Format: sl local_addr rem_addr st tx_queue rx_queue tr tm->when retrnsmt uid timeout inode
            if len(parts) < 10:
                continue

            try:
                inode = parts[9]
                # Filter: only include connections owned by this process
                if inode not in socket_inodes:
                    continue

                local_addr = self._decode_address(parts[1], is_ipv6)
                remote_addr = self._decode_address(parts[2], is_ipv6)

                connections.append({
                    "protocol": "udp6" if is_ipv6 else "udp",
                    "local_address": local_addr["ip"],
                    "local_port": local_addr["port"],
                    "remote_address": remote_addr["ip"],
                    "remote_port": remote_addr["port"],
                    "state": "UNCONN",
                    "inode": inode,
                })
            except (ValueError, IndexError):
                continue

        return connections

    def _decode_address(self, addr_hex: str, is_ipv6: bool) -> Dict:
        try:
            ip_hex, port_hex = addr_hex.split(":")
            port = int(port_hex, 16)

            if is_ipv6:
                ip = self._decode_ipv6(ip_hex)
            else:
                ip = self._decode_ipv4(ip_hex)

            return {"ip": ip, "port": port}
        except (ValueError, IndexError):
            return {"ip": "unknown", "port": 0}

    def _decode_ipv4(self, ip_hex: str) -> str:
        try:
            ip_int = int(ip_hex, 16)
            return ".".join([
                str((ip_int >> 0) & 0xFF),
                str((ip_int >> 8) & 0xFF),
                str((ip_int >> 16) & 0xFF),
                str((ip_int >> 24) & 0xFF),
            ])
        except ValueError:
            return "unknown"

    def _decode_ipv6(self, ip_hex: str) -> str:
        if len(ip_hex) != 32:
            return f"ipv6:{ip_hex[:16]}..."

        # Check for common patterns
        if ip_hex == "00000000000000000000000000000000":
            return "::"
        if ip_hex == "00000000000000000000000001000000":
            return "::1"

        try:
            # Split into 4-char groups and reverse byte order within each 32-bit word
            groups = []
            for i in range(0, 32, 8):
                word = ip_hex[i:i + 8]
                # Reverse byte order within word (little-endian to big-endian)
                reversed_word = word[6:8] + word[4:6] + word[2:4] + word[0:2]
                groups.append(reversed_word[0:4])
                groups.append(reversed_word[4:8])

            # Check for IPv4-mapped IPv6 address (::ffff:x.x.x.x)
            # Format: first 5 groups are 0, 6th group is ffff, last 2 groups are IPv4
            if (groups[0] == "0000" and groups[1] == "0000" and
                groups[2] == "0000" and groups[3] == "0000" and
                groups[4] == "0000" and groups[5].lower() == "ffff"):
                # Extract IPv4 from last two groups
                ipv4_high = int(groups[6], 16)
                ipv4_low = int(groups[7], 16)
                ipv4 = f"{(ipv4_high >> 8) & 0xFF}.{ipv4_high & 0xFF}.{(ipv4_low >> 8) & 0xFF}.{ipv4_low & 0xFF}"
                return ipv4

            # Format as standard IPv6, removing leading zeros
            formatted = ":".join(g.lstrip("0") or "0" for g in groups)
            
            # Compress consecutive zero groups (simple compression)
            formatted = formatted.replace(":0:0:0:0:0:0:0:", "::")
            formatted = formatted.replace(":0:0:0:0:0:0:", "::")
            formatted = formatted.replace(":0:0:0:0:0:", "::")
            formatted = formatted.replace(":0:0:0:0:", "::")
            formatted = formatted.replace(":0:0:0:", "::")
            formatted = formatted.replace(":0:0:", "::")
            
            return formatted
        except (ValueError, IndexError):
            return f"ipv6:{ip_hex[:16]}..."

