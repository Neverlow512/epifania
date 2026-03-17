# App Focused filter configuration management
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from core.logger import get_logger
from device.workshop_tab.storage.paths import (
    get_app_focused_default_config,
    get_app_focused_templates_dir,
    ensure_workshop_directories
)

logger = get_logger(__name__, "backend")

FORMAT_VERSION = "1.0"


class AppFocusedManager:
    def __init__(self):
        ensure_workshop_directories()
    
    def get_default_patterns(self, package_id: str) -> List[str]:
        return [f"{package_id}.*"]
    
    def get_config(self, package_id: str) -> Dict[str, Any]:
        config_file = get_app_focused_default_config(package_id)
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                logger.debug(f"Loaded app focused config for {package_id}")
                return config
            except Exception as e:
                logger.error(f"Failed to load config for {package_id}, using defaults: {e}")
        
        return self._create_default_config(package_id)
    
    def save_config(self, package_id: str, patterns: List[str]) -> bool:
        try:
            config_file = get_app_focused_default_config(package_id)
            now = datetime.now().isoformat()
            
            existing = None
            if config_file.exists():
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        existing = json.load(f)
                except:
                    pass
            
            config = {
                "format_version": FORMAT_VERSION,
                "package_id": package_id,
                "patterns": patterns,
                "created": existing.get("created", now) if existing else now,
                "modified": now
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved app focused config for {package_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save config for {package_id}: {e}")
            return False
    
    def list_templates(self, package_id: str) -> List[Dict[str, Any]]:
        templates_dir = get_app_focused_templates_dir(package_id)
        templates = []
        
        if not templates_dir.exists():
            return templates
        
        for item in sorted(templates_dir.iterdir()):
            if item.is_file() and item.suffix == ".json":
                try:
                    with open(item, 'r', encoding='utf-8') as f:
                        template = json.load(f)
                    templates.append({
                        "name": item.stem,
                        "created": template.get("created"),
                        "pattern_count": len(template.get("patterns", []))
                    })
                except Exception as e:
                    logger.warning(f"Failed to read template {item.name}: {e}")
        
        return templates
    
    def get_template(self, package_id: str, name: str) -> Optional[Dict[str, Any]]:
        templates_dir = get_app_focused_templates_dir(package_id)
        template_file = templates_dir / f"{name}.json"
        
        if not template_file.exists():
            return None
        
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load template {name} for {package_id}: {e}")
            return None
    
    def save_template(self, package_id: str, name: str, patterns: List[str]) -> bool:
        try:
            templates_dir = get_app_focused_templates_dir(package_id)
            safe_name = name.replace("/", "_").replace("\\", "_").replace(" ", "_")
            template_file = templates_dir / f"{safe_name}.json"
            
            now = datetime.now().isoformat()
            
            template = {
                "format_version": FORMAT_VERSION,
                "name": name,
                "package_id": package_id,
                "patterns": patterns,
                "created": now
            }
            
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved template '{name}' for {package_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save template {name} for {package_id}: {e}")
            return False
    
    def delete_template(self, package_id: str, name: str) -> bool:
        try:
            templates_dir = get_app_focused_templates_dir(package_id)
            safe_name = name.replace("/", "_").replace("\\", "_").replace(" ", "_")
            template_file = templates_dir / f"{safe_name}.json"
            
            if not template_file.exists():
                logger.warning(f"Template {name} not found for {package_id}")
                return False
            
            template_file.unlink()
            logger.info(f"Deleted template '{name}' for {package_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete template {name} for {package_id}: {e}")
            return False
    
    def reset_to_default(self, package_id: str) -> Dict[str, Any]:
        config = self._create_default_config(package_id)
        config_file = get_app_focused_default_config(package_id)
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            logger.info(f"Reset app focused config to defaults for {package_id}")
        except Exception as e:
            logger.error(f"Failed to save reset config for {package_id}: {e}")
        
        return config
    
    def _create_default_config(self, package_id: str) -> Dict[str, Any]:
        now = datetime.now().isoformat()
        return {
            "format_version": FORMAT_VERSION,
            "package_id": package_id,
            "patterns": self.get_default_patterns(package_id),
            "created": now,
            "modified": now
        }


app_focused_manager = AppFocusedManager()

