# Operation manager - tracks active operations for cancellation and progress
import time
import threading
from typing import Dict, Any, Optional
from core.logger import get_logger

logger = get_logger(__name__, "device")


class ActiveOperation:
    def __init__(self, device_id: str, operation_type: str, total: int = 0):
        self.device_id = device_id
        self.operation_type = operation_type
        self.start_time = time.time()
        self.end_time = None
        self.current = 0
        self.total = total
        self.current_item = ""
        self.cancelled = False
        self.completed = False
        self.success_count = 0
        self.error_count = 0
    
    def finalize(self, success_count: int, error_count: int):
        self.end_time = time.time()
        self.success_count = success_count
        self.error_count = error_count
        self.completed = True
    
    def get_metrics(self) -> Dict[str, Any]:
        duration = (self.end_time or time.time()) - self.start_time
        throughput = self.total / duration if duration > 0 and self.total > 0 else 0
        
        return {
            "operation_type": self.operation_type,
            "total": self.total,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "duration": duration,
            "throughput": throughput,
            "cancelled": self.cancelled
        }


class OperationManager:
    def __init__(self):
        self._operations: Dict[str, ActiveOperation] = {}
        self._lock = threading.Lock()
    
    def register(self, device_id: str, operation_type: str, total: int = 0) -> str:
        operation_id = f"{device_id}_{operation_type}_{int(time.time() * 1000)}"
        with self._lock:
            self._operations[operation_id] = ActiveOperation(device_id, operation_type, total)
        logger.info(f"Registered operation: {operation_id}")
        return operation_id
    
    def update_progress(self, operation_id: str, current: int, total: int, item: str):
        with self._lock:
            if operation_id in self._operations:
                op = self._operations[operation_id]
                op.current = current
                op.total = total
                op.current_item = item
    
    def mark_completed(self, operation_id: str):
        with self._lock:
            if operation_id in self._operations:
                self._operations[operation_id].completed = True
    
    def finalize_operation(self, operation_id: str, success_count: int, error_count: int) -> Optional[Dict[str, Any]]:
        with self._lock:
            if operation_id in self._operations:
                op = self._operations[operation_id]
                op.finalize(success_count, error_count)
                return op.get_metrics()
        return None
    
    def cancel(self, device_id: str, operation_type: str = None) -> bool:
        cancelled_any = False
        with self._lock:
            for op_id, op in self._operations.items():
                if op.device_id == device_id:
                    if operation_type is None or op.operation_type == operation_type:
                        op.cancelled = True
                        cancelled_any = True
                        logger.info(f"Cancelled operation: {op_id}")
        return cancelled_any
    
    def is_cancelled(self, operation_id: str) -> bool:
        with self._lock:
            if operation_id in self._operations:
                return self._operations[operation_id].cancelled
        return False
    
    def get_progress(self, operation_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            if operation_id in self._operations:
                op = self._operations[operation_id]
                return {
                    "operation_id": operation_id,
                    "operation_type": op.operation_type,
                    "current": op.current,
                    "total": op.total,
                    "current_item": op.current_item,
                    "cancelled": op.cancelled,
                    "completed": op.completed,
                    "elapsed": time.time() - op.start_time
                }
        return None
    
    def get_device_operation(self, device_id: str, operation_type: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            for op_id, op in self._operations.items():
                if op.device_id == device_id and op.operation_type == operation_type:
                    if not op.completed:
                        return {
                            "operation_id": op_id,
                            "operation_type": op.operation_type,
                            "current": op.current,
                            "total": op.total,
                            "current_item": op.current_item,
                            "cancelled": op.cancelled,
                            "completed": op.completed,
                            "elapsed": time.time() - op.start_time
                        }
        return None
    
    def unregister(self, operation_id: str):
        with self._lock:
            if operation_id in self._operations:
                del self._operations[operation_id]
                logger.info(f"Unregistered operation: {operation_id}")
    
    def cleanup_completed(self, max_age_seconds: float = 60.0):
        current_time = time.time()
        with self._lock:
            to_remove = [
                op_id for op_id, op in self._operations.items()
                if op.completed and (current_time - op.start_time) > max_age_seconds
            ]
            for op_id in to_remove:
                del self._operations[op_id]
            if to_remove:
                logger.info(f"Cleaned up {len(to_remove)} completed operations")


operation_manager = OperationManager()
