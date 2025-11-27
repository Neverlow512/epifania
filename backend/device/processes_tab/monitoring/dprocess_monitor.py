import re
from typing import List, Dict, Optional
from collections import defaultdict, deque
from datetime import datetime
from core.logger import get_logger
from core.adb_manager import ADBManager

logger = get_logger(__name__, "device")


class ProcessMonitor:
    def __init__(self, adb_manager: ADBManager):
        self.adb_manager = adb_manager
        self.metrics_storage = defaultdict(lambda: defaultdict(lambda: deque(maxlen=120)))
        self.previous_snapshots = defaultdict(dict)
        logger.info("ProcessMonitor initialized")
    
    def list_processes(self, device_serial: str) -> List[Dict]:
        try:
            logger.info(f"Listing processes for device {device_serial}")
            
            result = self.adb_manager.execute_shell(
                device_serial,
                "ps -A -o PID,USER,STAT,VSZ,RSS,PPID,WCHAN,NAME,ARGS 2>/dev/null || ps -eo pid,user,s,vsz,rss,ppid,wchan,comm,args"
            )
            
            if not result or result.strip() == "":
                logger.warning(f"No process data returned for {device_serial}")
                return []
            
            processes = self._parse_process_list(result)
            logger.info(f"Found {len(processes)} processes on {device_serial}")
            
            current_snapshot = {p['pid']: p for p in processes}
            self.previous_snapshots[device_serial] = current_snapshot
            
            return processes
            
        except Exception as e:
            logger.error(f"Failed to list processes for {device_serial}: {str(e)}")
            return []
    
    def _parse_process_list(self, ps_output: str) -> List[Dict]:
        processes = []
        lines = ps_output.strip().split('\n')
        
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            
            try:
                parts = line.split(None, 8)
                
                if len(parts) < 8:
                    continue
                
                pid = int(parts[0])
                user = parts[1]
                state = parts[2]
                vsz_kb = int(parts[3]) if parts[3].isdigit() else 0
                rss_kb = int(parts[4]) if parts[4].isdigit() else 0
                ppid = int(parts[5]) if parts[5].isdigit() else 0
                name = parts[7]
                command = parts[8] if len(parts) > 8 else name
                
                state_char = state[0] if state else 'S'
                state_map = {
                    'R': 'running',
                    'S': 'sleeping',
                    'D': 'disk_sleep',
                    'Z': 'zombie',
                    'T': 'traced',
                    'W': 'paging'
                }
                state_name = state_map.get(state_char, 'unknown')
                
                memory_mb = round(rss_kb / 1024, 2)
                cpu_percent = 0.0
                
                process = {
                    'pid': pid,
                    'name': name,
                    'user': user,
                    'cpu_percent': cpu_percent,
                    'memory_kb': rss_kb,
                    'memory_mb': memory_mb,
                    'vsz_kb': vsz_kb,
                    'state': state_name,
                    'ppid': ppid,
                    'command': command
                }
                
                processes.append(process)
                
            except (ValueError, IndexError) as e:
                logger.debug(f"Failed to parse process line: {line} - {str(e)}")
                continue
        
        return processes
    
    def get_process_details(self, device_serial: str, pid: int) -> Optional[Dict]:
        try:
            logger.info(f"Getting details for process {pid} on {device_serial}")
            
            details = {
                'pid': pid,
                'cmdline': self._get_process_cmdline(device_serial, pid),
                'status': self._get_process_status(device_serial, pid),
                'threads': self._get_process_threads(device_serial, pid),
                'open_files': self._get_process_files(device_serial, pid),
                'network_connections': self._get_process_network(device_serial, pid),
                'memory_maps': self._get_process_maps(device_serial, pid)
            }
            
            return details
            
        except Exception as e:
            logger.error(f"Failed to get process details for {pid} on {device_serial}: {str(e)}")
            return None
    
    def _get_process_cmdline(self, device_serial: str, pid: int) -> str:
        result = self.adb_manager.execute_shell(
            device_serial,
            f"cat /proc/{pid}/cmdline 2>/dev/null | tr '\\0' ' '"
        )
        return result.strip() if result else ""
    
    def _get_process_status(self, device_serial: str, pid: int) -> Dict:
        result = self.adb_manager.execute_shell(
            device_serial,
            f"cat /proc/{pid}/status 2>/dev/null"
        )
        
        status_info = {}
        if result:
            for line in result.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    status_info[key.strip()] = value.strip()
        
        return status_info
    
    def _get_process_threads(self, device_serial: str, pid: int) -> List[Dict]:
        result = self.adb_manager.execute_shell(
            device_serial,
            f"ls /proc/{pid}/task 2>/dev/null"
        )
        
        threads = []
        if result:
            thread_ids = result.strip().split()
            for tid in thread_ids:
                if tid.isdigit():
                    threads.append({'tid': int(tid)})
        
        return threads
    
    def _get_process_files(self, device_serial: str, pid: int) -> List[Dict]:
        result = self.adb_manager.execute_shell(
            device_serial,
            f"ls -l /proc/{pid}/fd 2>/dev/null"
        )
        
        files = []
        if result:
            for line in result.split('\n'):
                if '->' in line:
                    parts = line.split('->')
                    if len(parts) == 2:
                        fd_info = parts[0].strip().split()
                        if fd_info:
                            fd_num = fd_info[-1]
                            file_path = parts[1].strip()
                            files.append({
                                'fd': fd_num,
                                'path': file_path
                            })
        
        return files
    
    def _get_process_network(self, device_serial: str, pid: int) -> List[Dict]:
        return []
    
    def _get_process_maps(self, device_serial: str, pid: int) -> List[Dict]:
        result = self.adb_manager.execute_shell(
            device_serial,
            f"cat /proc/{pid}/maps 2>/dev/null | head -50"
        )
        
        maps = []
        if result:
            for line in result.split('\n'):
                if line.strip():
                    parts = line.split(None, 5)
                    if len(parts) >= 5:
                        maps.append({
                            'address': parts[0],
                            'perms': parts[1],
                            'offset': parts[2],
                            'dev': parts[3],
                            'inode': parts[4],
                            'pathname': parts[5] if len(parts) > 5 else ''
                        })
        
        return maps
    
    def kill_process(self, device_serial: str, pid: int, signal: int = 9) -> bool:
        try:
            logger.info(f"Killing process {pid} on {device_serial} with signal {signal}")
            
            result = self.adb_manager.execute_shell(
                device_serial,
                f"su -c 'kill -{signal} {pid}' 2>/dev/null || kill -{signal} {pid}"
            )
            
            verify = self.adb_manager.execute_shell(
                device_serial,
                f"ps -p {pid} 2>/dev/null"
            )
            
            is_killed = not verify or len(verify.strip().split('\n')) <= 1
            
            if is_killed:
                logger.info(f"Successfully killed process {pid}")
                return True
            else:
                logger.warning(f"Process {pid} may still be running")
                return False
                
        except Exception as e:
            logger.error(f"Failed to kill process {pid} on {device_serial}: {str(e)}")
            return False
    
    def get_process_metrics(self, device_serial: str, pid: Optional[int] = None, duration: int = 60) -> Dict:
        try:
            device_metrics = self.metrics_storage.get(device_serial, {})
            
            if pid:
                process_metrics = list(device_metrics.get(pid, []))
                return {
                    'device': device_serial,
                    'pid': pid,
                    'metrics': process_metrics[-duration:] if process_metrics else []
                }
            else:
                all_metrics = {}
                for proc_pid, metrics in device_metrics.items():
                    all_metrics[proc_pid] = list(metrics)[-duration:]
                
                return {
                    'device': device_serial,
                    'metrics': all_metrics
                }
                
        except Exception as e:
            logger.error(f"Failed to get metrics for {device_serial}: {str(e)}")
            return {'device': device_serial, 'metrics': {}}
    
    def store_metrics(self, device_serial: str, processes: List[Dict]):
        timestamp = datetime.now().isoformat()
        
        for process in processes:
            pid = process.get('pid')
            if pid:
                metric_point = {
                    'timestamp': timestamp,
                    'cpu_percent': process.get('cpu_percent', 0.0),
                    'memory_mb': process.get('memory_mb', 0.0)
                }
                self.metrics_storage[device_serial][pid].append(metric_point)
    
    def detect_changes(self, device_serial: str, current_processes: List[Dict]) -> Dict:
        previous = self.previous_snapshots.get(device_serial, {})
        current = {p['pid']: p for p in current_processes}
        
        previous_pids = set(previous.keys())
        current_pids = set(current.keys())
        
        spawned_pids = current_pids - previous_pids
        killed_pids = previous_pids - current_pids
        
        spawned = [current[pid] for pid in spawned_pids]
        killed = [previous[pid] for pid in killed_pids]
        
        changed = []
        for pid in previous_pids & current_pids:
            prev = previous[pid]
            curr = current[pid]
            
            cpu_diff = curr.get('cpu_percent', 0) - prev.get('cpu_percent', 0)
            mem_diff = curr.get('memory_mb', 0) - prev.get('memory_mb', 0)
            
            if cpu_diff > 50 or mem_diff > 100:
                changed.append({
                    'process': curr,
                    'cpu_increase': cpu_diff,
                    'memory_increase_mb': mem_diff
                })
        
        return {
            'spawned': spawned,
            'killed': killed,
            'changed': changed
        }
    
    def cleanup_metrics(self, device_serial: str, current_pids: List[int]):
        if device_serial in self.metrics_storage:
            stored_pids = list(self.metrics_storage[device_serial].keys())
            for pid in stored_pids:
                if pid not in current_pids:
                    del self.metrics_storage[device_serial][pid]
                    logger.debug(f"Cleaned up metrics for dead process {pid}")

