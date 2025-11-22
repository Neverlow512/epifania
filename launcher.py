#!/usr/bin/env python3
import subprocess
import sys
import os
import signal
import time
from pathlib import Path


class Launcher:
    def __init__(self):
        self.processes = []
        self.project_root = Path(__file__).parent.resolve()
        
    def start_backend(self):
        print("[Launcher] Starting FastAPI backend on http://127.0.0.1:8000")
        backend_process = subprocess.Popen(
            [
                sys.executable, "-m", "uvicorn",
                "backend.main:app",
                "--reload",
                "--host", "127.0.0.1",
                "--port", "8000"
            ],
            cwd=self.project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        self.processes.append(backend_process)
        return backend_process
    
    def start_frontend(self):
        print("[Launcher] Starting Vite dev server on http://127.0.0.1:5173")
        frontend_dir = self.project_root / "frontend"
        frontend_process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        self.processes.append(frontend_process)
        return frontend_process
    
    def shutdown(self, signum=None, frame=None):
        print("\n[Launcher] Shutting down services...")
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        print("[Launcher] All services stopped")
        sys.exit(0)
    
    def run(self):
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
        
        try:
            backend = self.start_backend()
            time.sleep(2)
            frontend = self.start_frontend()
            
            print("\n" + "="*60)
            print("Epifania is running")
            print("="*60)
            print("Backend:  http://127.0.0.1:8000")
            print("Frontend: http://127.0.0.1:5173")
            print("="*60)
            print("\nPress Ctrl+C to stop all services\n")
            
            while True:
                time.sleep(1)
                if backend.poll() is not None:
                    print("[Launcher] Backend process exited unexpectedly")
                    self.shutdown()
                if frontend.poll() is not None:
                    print("[Launcher] Frontend process exited unexpectedly")
                    self.shutdown()
                    
        except Exception as e:
            print(f"[Launcher] Error: {e}")
            self.shutdown()


if __name__ == "__main__":
    launcher = Launcher()
    launcher.run()

