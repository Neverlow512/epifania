import asyncio
import threading
from collections import deque
from typing import Dict, List, Optional, Callable
from datetime import datetime
from core.logger import get_logger

logger = get_logger(__name__, "backend")


class LogBuffer:
    def __init__(self, max_size: int = 1000):
        self.buffer = deque(maxlen=max_size)
        self.lock = threading.Lock()
    
    def add(self, log_entry: Dict):
        with self.lock:
            self.buffer.append(log_entry)
    
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
        logger.info("LogStreamer initialized")
    
    def get_or_create_buffer(self, device_id: str, log_type: str) -> LogBuffer:
        if device_id not in self.device_logs:
            self.device_logs[device_id] = {}
        
        if log_type not in self.device_logs[device_id]:
            self.device_logs[device_id][log_type] = LogBuffer()
        
        return self.device_logs[device_id][log_type]
    
    def add_log(self, device_id: str, log_type: str, message: str, level: str = "info"):
        buffer = self.get_or_create_buffer(device_id, log_type)
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message
        }
        buffer.add(log_entry)
    
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
    
    async def stream_logcat(self, device_id: str, adb_manager, callback: Callable):
        try:
            logger.info(f"Starting logcat stream for device {device_id}")
            self.set_streaming(device_id, "logcat", True)
            
            device = adb_manager.get_device(device_id)
            if not device:
                logger.error(f"Device {device_id} not found for logcat streaming")
                return
            
            # Start logcat in a separate thread to avoid blocking
            def read_logcat():
                try:
                    # Clear old logs first
                    device.shell("logcat -c")
                    
                    # Stream logcat
                    process = device.shell("logcat", timeout=None)
                    for line in process.split('\n'):
                        if not self.is_streaming(device_id, "logcat"):
                            break
                        
                        if line.strip():
                            # Parse log level
                            level = "info"
                            if " E " in line or " E/" in line:
                                level = "error"
                            elif " W " in line or " W/" in line:
                                level = "warning"
                            elif " D " in line or " D/" in line:
                                level = "debug"
                            
                            self.add_log(device_id, "logcat", line.strip(), level)
                            asyncio.run(callback(device_id, "logcat", line.strip(), level))
                except Exception as e:
                    logger.error(f"Error in logcat stream: {str(e)}")
            
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


log_streamer = LogStreamer()

