import asyncio
import threading
import subprocess
from collections import deque
from typing import Dict, List, Optional, Callable, Tuple
from datetime import datetime
from core.logger import get_logger

logger = get_logger(__name__, "backend")


class LogBuffer:
    def __init__(self, max_size: int = 1000):
        self.buffer = deque(maxlen=max_size)
        self.lock = threading.Lock()
        self._last_message: Optional[str] = None
    
    def add(self, log_entry: Dict):
        with self.lock:
            # Deduplicate consecutive identical messages
            msg = log_entry.get("message", "")
            if self._last_message is not None and self._last_message == msg:
                return
            self.buffer.append(log_entry)
            self._last_message = msg
    
    def get_all(self) -> List[Dict]:
        with self.lock:
            return list(self.buffer)
    
    def clear(self):
        with self.lock:
            self.buffer.clear()


class LogStreamer:
    def __init__(self):
        self.device_logs: Dict[str, Dict[str, LogBuffer]] = {}
        self.active_streams: Dict[str, Dict[str, bool]] = {}
        self.stream_tasks: Dict[str, Dict[str, asyncio.Task]] = {}
        self.stream_processes: Dict[str, Dict[str, subprocess.Popen]] = {}
        self.subscribers: Dict[str, Dict[str, List[Tuple[asyncio.AbstractEventLoop, Callable]]]] = {}
        logger.info("LogStreamer initialized")
    
    def get_or_create_buffer(self, device_id: str, log_type: str) -> LogBuffer:
        if device_id not in self.device_logs:
            self.device_logs[device_id] = {}
        
        if log_type not in self.device_logs[device_id]:
            # Tighter bounds to limit memory growth
            max_size = 500 if log_type == "logcat" else 300
            self.device_logs[device_id][log_type] = LogBuffer(max_size=max_size)
        
        return self.device_logs[device_id][log_type]
    
    def register_subscriber(self, device_id: str, log_type: str, loop: asyncio.AbstractEventLoop, callback: Callable):
        if device_id not in self.subscribers:
            self.subscribers[device_id] = {}
        if log_type not in self.subscribers[device_id]:
            self.subscribers[device_id][log_type] = []
        self.subscribers[device_id][log_type].append((loop, callback))
    
    def unregister_subscriber(self, device_id: str, log_type: str, callback: Optional[Callable] = None):
        try:
            subs = self.subscribers.get(device_id, {}).get(log_type, [])
            if callback is None:
                self.subscribers.get(device_id, {}).pop(log_type, None)
            else:
                self.subscribers[device_id][log_type] = [(lp, cb) for (lp, cb) in subs if cb != callback]
        except Exception:
            pass
    
    def _notify_subscribers(self, device_id: str, log_type: str, message: str, level: str, timestamp: str):
        subs = self.subscribers.get(device_id, {}).get(log_type, [])
        if not subs:
            return
        payload = {
            "type": log_type,
            "level": level,
            "message": message,
            "timestamp": timestamp
        }
        for loop, callback in list(subs):
            try:
                fut = asyncio.run_coroutine_threadsafe(
                    callback(payload),
                    loop
                )
                # Avoid blocking; do not call result() here
            except Exception:
                continue
    
    def add_log(self, device_id: str, log_type: str, message: str, level: str = "info"):
        buffer = self.get_or_create_buffer(device_id, log_type)
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message
        }
        buffer.add(log_entry)
        self._notify_subscribers(device_id, log_type, message, level, log_entry["timestamp"])
    
    def get_logs(self, device_id: str, log_type: str) -> List[Dict]:
        if device_id not in self.device_logs:
            return []
        
        if log_type not in self.device_logs[device_id]:
            return []
        
        return self.device_logs[device_id][log_type].get_all()
    
    def clear_logs(self, device_id: str, log_type: str):
        if device_id in self.device_logs and log_type in self.device_logs[device_id]:
            self.device_logs[device_id][log_type].clear()
    
    def is_streaming(self, device_id: str, log_type: str) -> bool:
        if device_id not in self.active_streams:
            return False
        return self.active_streams[device_id].get(log_type, False)
    
    def set_streaming(self, device_id: str, log_type: str, active: bool):
        if device_id not in self.active_streams:
            self.active_streams[device_id] = {}
        self.active_streams[device_id][log_type] = active
    
    def _parse_level_from_logcat(self, line: str) -> str:
        if " E " in line or " E/" in line:
            return "error"
        if " W " in line or " W/" in line:
            return "warning"
        if " D " in line or " D/" in line:
            return "debug"
        return "info"
    
    def _should_filter_logcat_line(self, line: str, level: str) -> bool:
        # Filter out debug logs from less important system components
        if level == "debug":
            # Common noisy tags to filter out
            noisy_tags = [
                "InputReader", "InputDispatcher", "WindowManager",
                "ActivityManager", "KeyguardUpdateMonitor", "PowerManagerService",
                "WifiService", "ConnectivityService", "ViewRootImpl"
            ]
            for tag in noisy_tags:
                if tag in line:
                    return True
        
        # Always keep errors and warnings
        if level in ["error", "warning"]:
            return False
        
        # Filter out very verbose system messages
        if "system_process" in line.lower() and level == "debug":
            return True
        
        return False
    
    def fetch_logcat_history(self, device_id: str, adb_manager, max_lines: int = 500):
        try:
            device = adb_manager.get_device(device_id)
            if not device:
                logger.error(f"Device {device_id} not found for logcat history")
                return
            
            # Try to get last N lines using -t, fallback to full dump
            # Use main buffer only for better performance, focus on application logs
            history = device.shell(f"logcat -d -v time -b main -t {max_lines}")
            if not history or "unknown option" in history.lower():
                history = device.shell("logcat -d -v time -b main")
                if history:
                    lines = history.splitlines()[-max_lines:]
                else:
                    lines = []
            else:
                lines = history.splitlines()
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                level = self._parse_level_from_logcat(line)
                # Apply smart filtering
                if self._should_filter_logcat_line(line, level):
                    continue
                self.add_log(device_id, "logcat", line, level)
        except Exception as e:
            logger.error(f"Failed to fetch logcat history for {device_id}: {str(e)}")
    
    async def stream_logcat(self, device_id: str, adb_manager, loop: asyncio.AbstractEventLoop):
        try:
            logger.info(f"Starting logcat stream for device {device_id}")
            self.set_streaming(device_id, "logcat", True)
            
            # Start logcat in a separate thread using adb subprocess for reliable streaming
            # Focus on main buffer and important logs only
            def read_logcat():
                process = None
                try:
                    # Use main buffer, filter by priority (V=Verbose, D=Debug, I=Info, W=Warning, E=Error, F=Fatal)
                    # *:I means show Info and above for all tags
                    cmd = ["adb", "-s", device_id, "logcat", "-v", "time", "-b", "main", "*:I"]
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        bufsize=1,
                        universal_newlines=True
                    )
                    if device_id not in self.stream_processes:
                        self.stream_processes[device_id] = {}
                    self.stream_processes[device_id]["logcat"] = process
                    
                    for line in iter(process.stdout.readline, ''):
                        # Check if streaming should stop
                        if not self.is_streaming(device_id, "logcat"):
                            logger.info(f"Logcat stream stopped for device {device_id}")
                            break
                        if not line:
                            continue
                        line = line.strip()
                        if not line:
                            continue
                        level = self._parse_level_from_logcat(line)
                        # Apply smart filtering
                        if self._should_filter_logcat_line(line, level):
                            continue
                        self.add_log(device_id, "logcat", line, level)
                except Exception as e:
                    logger.error(f"Error in logcat stream: {str(e)}")
                finally:
                    # Ensure process is terminated
                    if process and process.poll() is None:
                        try:
                            process.terminate()
                            process.wait(timeout=2)
                        except Exception:
                            try:
                                process.kill()
                            except Exception:
                                pass
            
            thread = threading.Thread(target=read_logcat, daemon=True)
            thread.start()
            
        except Exception as e:
            logger.error(f"Failed to start logcat stream: {str(e)}")
            self.set_streaming(device_id, "logcat", False)
    
    def stop_stream(self, device_id: str, log_type: str):
        logger.info(f"Stopping {log_type} stream for device {device_id}")
        self.set_streaming(device_id, log_type, False)
        
        if device_id in self.stream_tasks and log_type in self.stream_tasks[device_id]:
            task = self.stream_tasks[device_id][log_type]
            if not task.done():
                task.cancel()
        
        # Terminate the process more aggressively
        try:
            proc = self.stream_processes.get(device_id, {}).get(log_type)
            if proc and proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    # Force kill if terminate didn't work
                    proc.kill()
                    try:
                        proc.wait(timeout=1)
                    except Exception:
                        pass
        except Exception as e:
            logger.error(f"Error stopping {log_type} process: {str(e)}")


log_streamer = LogStreamer()

