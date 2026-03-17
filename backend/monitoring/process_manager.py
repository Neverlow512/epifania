import os
import signal
import psutil
import socket
from pathlib import Path
from typing import Optional
from core.logger import get_logger
from core.log_paths import LOGS_APPLICATION
import time
logger = get_logger(__name__, "backend")


class ProcessManager:
    def __init__(self, port: int = 8000, pid_file: Optional[str] = None):
        self.port = port
        self.pid_file = pid_file or str(LOGS_APPLICATION / "backend.pid")
        self.current_pid = os.getpid()
        
        logger.info(f"Process manager initialized for port {self.port}")
    
    def is_port_in_use(self) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('127.0.0.1', self.port)) == 0
    
    def find_process_using_port(self) -> Optional[psutil.Process]:
        try:
            for conn in psutil.net_connections(kind='inet'):
                if conn.laddr.port == self.port and conn.status == 'LISTEN':
                    try:
                        proc = psutil.Process(conn.pid)
                        return proc
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
        except Exception as e:
            logger.error(f"Error finding process on port {self.port}: {str(e)}")
        return None
    
    def kill_process_on_port(self) -> bool:
        try:
            proc = self.find_process_using_port()
            if proc:
                logger.warning(f"Found process {proc.pid} ({proc.name()}) using port {self.port}")
                
                # Check if it's our own process
                if proc.pid == self.current_pid:
                    logger.info("Process is current instance, skipping kill")
                    return False
                
                # Check if it's another uvicorn/python process
                cmdline = ' '.join(proc.cmdline())
                if 'uvicorn' in cmdline.lower() or 'main:app' in cmdline:
                    logger.warning(f"Killing stale backend process: {proc.pid}")
                    
                    # Kill children first (uvicorn --reload spawns worker children)
                    try:
                        children = proc.children(recursive=True)
                        for child in children:
                            logger.warning(f"Killing child process: {child.pid}")
                            child.terminate()
                        
                        # Wait for children
                        psutil.wait_procs(children, timeout=3)
                        
                        # Force kill remaining children
                        for child in children:
                            if child.is_running():
                                child.kill()
                    except Exception as e:
                        logger.debug(f"Error killing children: {e}")
                    
                    # Now kill the parent
                    proc.terminate()
                    
                    try:
                        proc.wait(timeout=5)
                        logger.info(f"Process {proc.pid} terminated gracefully")
                    except psutil.TimeoutExpired:
                        logger.warning(f"Process {proc.pid} did not terminate, forcing kill")
                        proc.kill()
                    
                    return True
                else:
                    logger.error(f"Port {self.port} is used by non-backend process: {cmdline}")
                    return False
            
            return False
            
        except Exception as e:
            logger.error(f"Error killing process on port {self.port}: {str(e)}")
            return False
    
    def cleanup_stale_processes(self):
        try:
            logger.info("Checking for stale backend processes...")
            
            # Check PID file
            if os.path.exists(self.pid_file):
                try:
                    with open(self.pid_file, 'r') as f:
                        old_pid = int(f.read().strip())
                    
                    if psutil.pid_exists(old_pid):
                        try:
                            proc = psutil.Process(old_pid)
                            cmdline = ' '.join(proc.cmdline())
                            
                            if 'uvicorn' in cmdline.lower() or 'main:app' in cmdline:
                                logger.warning(f"Found stale backend process from PID file: {old_pid}")
                                proc.terminate()
                                try:
                                    proc.wait(timeout=5)
                                except psutil.TimeoutExpired:
                                    proc.kill()
                                logger.info(f"Cleaned up stale process {old_pid}")
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                    
                    os.remove(self.pid_file)
                    logger.info("Removed stale PID file")
                    
                except Exception as e:
                    logger.error(f"Error cleaning up PID file: {str(e)}")
            
            # Check port with retry
            for attempt in range(3):
                if self.is_port_in_use():
                    logger.warning(f"Port {self.port} is in use, attempting cleanup (attempt {attempt + 1}/3)")
                    self.kill_process_on_port()
                    
                    # Wait for socket to be released
                    
                    time.sleep(1)
                else:
                    break
            
            if self.is_port_in_use():
                logger.error(f"Port {self.port} still in use after cleanup attempts")
            
        except Exception as e:
            logger.error(f"Error during stale process cleanup: {str(e)}")
    
    def write_pid_file(self):
        try:
            os.makedirs(os.path.dirname(self.pid_file), exist_ok=True)
            with open(self.pid_file, 'w') as f:
                f.write(str(self.current_pid))
            logger.info(f"Wrote PID {self.current_pid} to {self.pid_file}")
        except Exception as e:
            logger.error(f"Error writing PID file: {str(e)}")
    
    def cleanup_pid_file(self):
        try:
            if os.path.exists(self.pid_file):
                os.remove(self.pid_file)
                logger.info("Removed PID file")
        except Exception as e:
            logger.error(f"Error removing PID file: {str(e)}")
    
    def cleanup_on_shutdown(self):
        logger.info("Running shutdown cleanup...")
        self.cleanup_pid_file()


process_manager = ProcessManager()

