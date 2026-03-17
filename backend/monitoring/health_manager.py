import asyncio
import time
from typing import Optional, Callable
from datetime import datetime
from core.logger import get_logger

logger = get_logger(__name__, "backend")


class HealthManager:
    def __init__(self, check_interval: int = 10):
        self.check_interval = check_interval
        self.is_healthy = True
        self.last_check_time: Optional[datetime] = None
        self.health_checks: list[Callable] = []
        self.monitoring_task: Optional[asyncio.Task] = None
        self.running = False
        self.failure_count = 0
        self.max_failures = 3
        
        logger.info("Health manager initialized")
    
    def register_health_check(self, check_func: Callable, name: str = None):
        check_name = name or check_func.__name__
        self.health_checks.append((check_name, check_func))
        logger.info(f"Registered health check: {check_name}")
    
    async def run_health_checks(self) -> dict:
        results = {
            "overall_healthy": True,
            "checks": {},
            "timestamp": datetime.now().isoformat()
        }
        
        for check_name, check_func in self.health_checks:
            try:
                if asyncio.iscoroutinefunction(check_func):
                    result = await check_func()
                else:
                    result = check_func()
                
                results["checks"][check_name] = {
                    "status": "healthy" if result else "unhealthy",
                    "healthy": result
                }
                
                if not result:
                    results["overall_healthy"] = False
                    logger.warning(f"Health check failed: {check_name}")
                    
            except Exception as e:
                logger.error(f"Health check error for {check_name}: {str(e)}")
                results["checks"][check_name] = {
                    "status": "error",
                    "healthy": False,
                    "error": str(e)
                }
                results["overall_healthy"] = False
        
        self.is_healthy = results["overall_healthy"]
        self.last_check_time = datetime.now()
        
        if not self.is_healthy:
            self.failure_count += 1
            logger.warning(f"Health check failed ({self.failure_count}/{self.max_failures})")
        else:
            self.failure_count = 0
        
        return results
    
    async def monitoring_loop(self):
        logger.info("Health monitoring loop started")
        
        while self.running:
            try:
                await self.run_health_checks()
                
                if self.failure_count >= self.max_failures:
                    logger.error(f"Health check failed {self.max_failures} times consecutively")
                    logger.error("System may be unhealthy - manual intervention may be required")
                
                await asyncio.sleep(self.check_interval)
                
            except asyncio.CancelledError:
                logger.info("Health monitoring loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in health monitoring loop: {str(e)}")
                await asyncio.sleep(self.check_interval)
    
    async def start(self):
        if self.running:
            logger.warning("Health manager already running")
            return
        
        self.running = True
        self.monitoring_task = asyncio.create_task(self.monitoring_loop())
        logger.info("Health manager started")
    
    async def stop(self):
        if not self.running:
            return
        
        self.running = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Health manager stopped")
    
    def get_status(self) -> dict:
        return {
            "is_healthy": self.is_healthy,
            "last_check": self.last_check_time.isoformat() if self.last_check_time else None,
            "failure_count": self.failure_count,
            "max_failures": self.max_failures,
            "running": self.running
        }


health_manager = HealthManager()

