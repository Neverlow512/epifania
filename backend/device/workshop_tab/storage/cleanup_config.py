import json
import threading
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
from core.logger import get_logger

logger = get_logger(__name__, "backend")

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
CONFIG_DIR = PROJECT_ROOT / "local_storage" / "config" / "discovery_retention"

DEFAULT_RETENTION_LIMIT = 10


class CleanupConfigManager:
    def __init__(self):
        self._lock = threading.Lock()
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        logger.info("CleanupConfigManager initialized")
    
    def _get_config_file(self, package_id: str) -> Path:
        safe_package = package_id.replace(".", "_").replace("/", "_")
        return CONFIG_DIR / f"{safe_package}.json"
    
    def get_retention_limit(self, package_id: str) -> int:
        with self._lock:
            config_file = self._get_config_file(package_id)
            
            if not config_file.exists():
                return DEFAULT_RETENTION_LIMIT
            
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                return config.get("retention_limit", DEFAULT_RETENTION_LIMIT)
            except Exception as e:
                logger.error(f"Failed to read retention config for {package_id}: {e}")
                return DEFAULT_RETENTION_LIMIT
    
    def set_retention_limit(self, package_id: str, limit: int) -> bool:
        with self._lock:
            try:
                config_file = self._get_config_file(package_id)
                
                config = {
                    "package_id": package_id,
                    "retention_limit": limit,
                    "last_updated": datetime.now().isoformat()
                }
                
                with open(config_file, 'w') as f:
                    json.dump(config, f, indent=2)
                
                logger.info(f"Set retention limit for {package_id}: {limit}")
                return True
            except Exception as e:
                logger.error(f"Failed to set retention limit for {package_id}: {e}")
                return False
    
    def get_all_configs(self) -> Dict[str, int]:
        with self._lock:
            configs = {}
            
            if not CONFIG_DIR.exists():
                return configs
            
            for config_file in CONFIG_DIR.glob("*.json"):
                try:
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                    package_id = config.get("package_id")
                    retention_limit = config.get("retention_limit", DEFAULT_RETENTION_LIMIT)
                    if package_id:
                        configs[package_id] = retention_limit
                except Exception as e:
                    logger.warning(f"Failed to read config file {config_file.name}: {e}")
            
            return configs


cleanup_config_manager = CleanupConfigManager()
