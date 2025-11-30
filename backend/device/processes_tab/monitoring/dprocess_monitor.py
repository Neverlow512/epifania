import re
import time
from typing import List, Dict, Optional
from collections import defaultdict, deque
from datetime import datetime
from core.logger import get_logger
from core.adb_manager import ADBManager

logger = get_logger(__name__, "device")

# Android ActivityManager process state constants mapped to user-friendly labels
PROC_STATE_MAP = {
    0: 'persistent',    # PROCESS_STATE_PERSISTENT
    1: 'persistent',    # PROCESS_STATE_PERSISTENT_UI
    2: 'foreground',    # PROCESS_STATE_TOP
    3: 'foreground',    # PROCESS_STATE_FOREGROUND_SERVICE_LOCATION (API 29+)
    4: 'visible',       # PROCESS_STATE_BOUND_FOREGROUND_SERVICE
    5: 'service',       # PROCESS_STATE_FOREGROUND_SERVICE
    6: 'bound',         # PROCESS_STATE_BOUND_TOP
    7: 'visible',       # PROCESS_STATE_IMPORTANT_FOREGROUND
    8: 'background',    # PROCESS_STATE_IMPORTANT_BACKGROUND
    9: 'background',    # PROCESS_STATE_TRANSIENT_BACKGROUND
    10: 'background',   # PROCESS_STATE_BACKUP
    11: 'service',      # PROCESS_STATE_SERVICE
    12: 'receiver',     # PROCESS_STATE_RECEIVER
    13: 'cached',       # PROCESS_STATE_TOP_SLEEPING (API 23+)
    14: 'background',   # PROCESS_STATE_HEAVY_WEIGHT
    15: 'cached',       # PROCESS_STATE_HOME
    16: 'cached',       # PROCESS_STATE_LAST_ACTIVITY
    17: 'cached',       # PROCESS_STATE_CACHED_ACTIVITY
    18: 'cached',       # PROCESS_STATE_CACHED_ACTIVITY_CLIENT
    19: 'cached',       # PROCESS_STATE_CACHED_RECENT
    20: 'cached',       # PROCESS_STATE_CACHED_EMPTY
}


class ChurnTracker:
    # Tracks process spawn/kill events with timestamps for time-windowed counts
    # Maintains full history for research purposes (up to max_events per device)
    
    def __init__(self, max_events: int = 1000):
        self._spawn_events: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_events))
        self._kill_events: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_events))
    
    def record_spawn(self, device_serial: str, process: Dict):
        timestamp = time.time()
        self._spawn_events[device_serial].append({
            "timestamp": timestamp,
            "pid": process.get("pid"),
            "name": process.get("name", "unknown"),
            "user": process.get("user", "unknown")
        })
    
    def record_kill(self, device_serial: str, process: Dict):
        timestamp = time.time()
        self._kill_events[device_serial].append({
            "timestamp": timestamp,
            "pid": process.get("pid"),
            "name": process.get("name", "unknown"),
            "user": process.get("user", "unknown")
        })
    
    def get_churn_stats(self, device_serial: str, window_seconds: int = 60) -> Dict:
        current_time = time.time()
        cutoff = current_time - window_seconds
        
        spawned_count = 0
        spawned_recent = []
        for event in self._spawn_events[device_serial]:
            if event["timestamp"] >= cutoff:
                spawned_count += 1
                spawned_recent.append({
                    "pid": event["pid"],
                    "name": event["name"],
                    "user": event.get("user", "unknown"),
                    "seconds_ago": int(current_time - event["timestamp"])
                })
        
        killed_count = 0
        killed_recent = []
        for event in self._kill_events[device_serial]:
            if event["timestamp"] >= cutoff:
                killed_count += 1
                killed_recent.append({
                    "pid": event["pid"],
                    "name": event["name"],
                    "user": event.get("user", "unknown"),
                    "seconds_ago": int(current_time - event["timestamp"])
                })
        
        # Sort by most recent first, limit to 10
        spawned_recent.sort(key=lambda x: x["seconds_ago"])
        killed_recent.sort(key=lambda x: x["seconds_ago"])
        
        return {
            "window_seconds": window_seconds,
            "spawned_count": spawned_count,
            "killed_count": killed_count,
            "net_change": spawned_count - killed_count,
            "recent_spawned": spawned_recent[:10],
            "recent_killed": killed_recent[:10]
        }
    
    def get_full_history(self, device_serial: str, limit: int = 500) -> Dict:
        # Returns full chronological history of all spawn/kill events for research
        current_time = time.time()
        
        all_events = []
        
        for event in self._spawn_events[device_serial]:
            all_events.append({
                "type": "spawn",
                "timestamp": event["timestamp"],
                "time_iso": datetime.fromtimestamp(event["timestamp"]).isoformat(),
                "pid": event["pid"],
                "name": event["name"],
                "user": event.get("user", "unknown"),
                "seconds_ago": int(current_time - event["timestamp"])
            })
        
        for event in self._kill_events[device_serial]:
            all_events.append({
                "type": "kill",
                "timestamp": event["timestamp"],
                "time_iso": datetime.fromtimestamp(event["timestamp"]).isoformat(),
                "pid": event["pid"],
                "name": event["name"],
                "user": event.get("user", "unknown"),
                "seconds_ago": int(current_time - event["timestamp"])
            })
        
        # Sort by timestamp descending (most recent first)
        all_events.sort(key=lambda x: x["timestamp"], reverse=True)
        
        total_spawned = len(self._spawn_events[device_serial])
        total_killed = len(self._kill_events[device_serial])
        
        return {
            "events": all_events[:limit],
            "total_events": len(all_events),
            "total_spawned": total_spawned,
            "total_killed": total_killed,
            "limited": len(all_events) > limit
        }


class ProcessMonitor:
    def __init__(self, adb_manager: ADBManager):
        self.adb_manager = adb_manager
        self.metrics_storage = defaultdict(lambda: defaultdict(lambda: deque(maxlen=120)))
        self.previous_snapshots = defaultdict(dict)
        self.snapshot_timestamps = defaultdict(float)
        self.churn_tracker = ChurnTracker()
        self._initialized_devices = set()
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
            
            android_states = self._get_android_process_states(device_serial)
            self._apply_android_states(processes, android_states)
            
            previous = self.previous_snapshots.get(device_serial, {})
            for process in processes:
                pid = process['pid']
                prev_data = previous.get(pid, {})
                # Only use previous memory if same process (name + user match to handle PID reuse)
                if prev_data.get('name') == process['name'] and prev_data.get('user') == process['user']:
                    prev_mem = prev_data.get('memory_mb', process['memory_mb'])
                else:
                    prev_mem = process['memory_mb']
                process['memory_delta_mb'] = round(process['memory_mb'] - prev_mem, 2)
            
            return processes
            
        except Exception as e:
            logger.error(f"Failed to list processes for {device_serial}: {str(e)}")
            return []
    
    def _get_android_process_states(self, device_serial: str) -> Dict[int, Dict]:
        # Fetches Android process states via dumpsys activity processes
        try:
            result = self.adb_manager.execute_shell(
                device_serial,
                "dumpsys activity processes 2>/dev/null | grep -E '(ProcessRecord|pid=|curProcState=|cached=)'"
            )
            
            if not result:
                return {}
            
            states = {}
            current_pid = None
            current_info = None
            
            for line in result.split('\n'):
                line = line.strip()
                
                if 'ProcessRecord' in line:
                    if current_pid and current_info:
                        states[current_pid] = current_info
                    current_pid = None
                    current_info = {}
                    
                    # Extract process type (*PERS*, *APP*, etc.)
                    if '*PERS*' in line:
                        current_info['type'] = 'persistent'
                    elif '*APP*' in line:
                        current_info['type'] = 'app'
                    
                elif 'pid=' in line and current_info is not None:
                    match = re.search(r'pid=(\d+)', line)
                    if match:
                        current_pid = int(match.group(1))
                
                elif 'curProcState=' in line and current_info is not None:
                    match = re.search(r'curProcState=(\d+)', line)
                    if match:
                        proc_state = int(match.group(1))
                        current_info['proc_state'] = proc_state
                        current_info['state_label'] = PROC_STATE_MAP.get(proc_state, 'background')
                
                elif 'cached=' in line and current_info is not None:
                    current_info['cached'] = 'cached=true' in line
            
            if current_pid and current_info:
                states[current_pid] = current_info
            
            logger.debug(f"Got Android states for {len(states)} processes")
            return states
            
        except Exception as e:
            logger.warning(f"Failed to get Android process states: {str(e)}")
            return {}
    
    def _apply_android_states(self, processes: List[Dict], android_states: Dict[int, Dict]):
        # Merges Android state info into process list, with fallback to kernel state
        for process in processes:
            pid = process['pid']
            android_info = android_states.get(pid)
            
            if android_info:
                process['state'] = android_info.get('state_label', 'background')
                process['android_managed'] = True
            else:
                # Fallback for non-Android processes
                if process.get('is_kernel_thread'):
                    process['state'] = 'kernel'
                elif process.get('user') == 'root' and process['pid'] < 1000:
                    process['state'] = 'native'
                elif process.get('kernel_state') == 'zombie':
                    process['state'] = 'zombie'
                else:
                    process['state'] = 'native'
                process['android_managed'] = False
    
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
                kernel_state_map = {
                    'R': 'running',
                    'S': 'sleeping',
                    'D': 'disk_sleep',
                    'Z': 'zombie',
                    'T': 'traced',
                    'W': 'paging'
                }
                kernel_state = kernel_state_map.get(state_char, 'unknown')
                
                memory_mb = round(rss_kb / 1024, 2)
                cpu_percent = 0.0
                
                is_kernel_thread = name.startswith('[') and name.endswith(']')
                
                process = {
                    'pid': pid,
                    'name': name,
                    'user': user,
                    'cpu_percent': cpu_percent,
                    'memory_kb': rss_kb,
                    'memory_mb': memory_mb,
                    'memory_delta_mb': 0.0,
                    'vsz_kb': vsz_kb,
                    'state': kernel_state,
                    'kernel_state': kernel_state,
                    'ppid': ppid,
                    'command': command,
                    'is_kernel_thread': is_kernel_thread
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
        current_time = time.time()
        previous = self.previous_snapshots.get(device_serial, {})
        current = {p['pid']: p for p in current_processes}
        last_snapshot_time = self.snapshot_timestamps.get(device_serial, 0)
        
        # Debounce: skip churn recording if snapshot was updated less than 500ms ago
        # This prevents double-counting when multiple tabs poll simultaneously
        should_record_churn = (current_time - last_snapshot_time) >= 0.5
        
        # Check if this is the first snapshot for this device (initialization)
        is_first_snapshot = device_serial not in self._initialized_devices
        if is_first_snapshot:
            self._initialized_devices.add(device_serial)
        
        # Update snapshot and timestamp
        self.previous_snapshots[device_serial] = current
        self.snapshot_timestamps[device_serial] = current_time
        
        previous_pids = set(previous.keys())
        current_pids = set(current.keys())
        
        spawned = []
        killed = []
        changed = []
        
        # Detect killed processes and PID reuse
        for pid in previous_pids:
            prev = previous[pid]
            if pid not in current_pids:
                killed.append(prev)
            else:
                curr = current[pid]
                # PID reuse: different name or user means old process died, new one spawned
                if prev.get('name') != curr.get('name') or prev.get('user') != curr.get('user'):
                    killed.append(prev)
                    spawned.append(curr)
        
        # Detect newly spawned processes (PIDs not in previous snapshot)
        for pid in current_pids - previous_pids:
            spawned.append(current[pid])
        
        # Record churn events only if:
        # 1. We have a previous snapshot (not first poll ever)
        # 2. This is not the initialization snapshot (don't count existing processes as spawned)
        # 3. Enough time has passed since last snapshot (debounce for concurrent requests)
        if previous and not is_first_snapshot and should_record_churn:
            for proc in spawned:
                self.churn_tracker.record_spawn(device_serial, proc)
            for proc in killed:
                self.churn_tracker.record_kill(device_serial, proc)
        
        # Check for significant resource changes (only for same process identity)
        for pid in previous_pids & current_pids:
            prev = previous[pid]
            curr = current[pid]
            
            # Skip if PID was reused by different process
            if prev.get('name') != curr.get('name') or prev.get('user') != curr.get('user'):
                continue
            
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
    
    def get_churn_stats(self, device_serial: str, window_seconds: int = 60) -> Dict:
        return self.churn_tracker.get_churn_stats(device_serial, window_seconds)
    
    def get_churn_history(self, device_serial: str, limit: int = 500) -> Dict:
        return self.churn_tracker.get_full_history(device_serial, limit)
    
    def cleanup_metrics(self, device_serial: str, current_pids: List[int]):
        if device_serial in self.metrics_storage:
            stored_pids = list(self.metrics_storage[device_serial].keys())
            for pid in stored_pids:
                if pid not in current_pids:
                    del self.metrics_storage[device_serial][pid]
                    logger.debug(f"Cleaned up metrics for dead process {pid}")

