# Categorization rules management - load, save, and reset rules
import json
from pathlib import Path
from typing import Dict, Any, Optional
from core.logger import get_logger
from device.workshop_tab.storage.paths import (
    CATEGORIZATION_RULES_FILE,
    ensure_workshop_directories
)

logger = get_logger(__name__, "backend")


DEFAULT_RULES = {
    "format_version": "1.0",
    "categories": {
        "Network": {
            "keywords": ["http", "url", "okhttp", "retrofit", "websocket", "socket", "request", "response", "connection", "net"],
            "packages": ["okhttp3", "retrofit2", "com.squareup.okhttp", "java.net", "javax.net"],
            "confidence": "high",
            "enabled": True
        },
        "Crypto": {
            "keywords": ["cipher", "encrypt", "decrypt", "crypto", "aes", "rsa", "ssl", "tls", "keystore", "hash", "sign", "verify"],
            "packages": ["javax.crypto", "java.security", "org.bouncycastle"],
            "confidence": "high",
            "enabled": True
        },
        "Storage": {
            "keywords": ["sqlite", "database", "preference", "sharedpref", "file", "contentprovider", "storage", "cache", "persist"],
            "packages": ["android.database", "android.content"],
            "confidence": "high",
            "enabled": True
        },
        "Security": {
            "keywords": ["auth", "authentication", "biometric", "fingerprint", "keyguard", "token", "credential", "password", "login", "session"],
            "packages": ["android.hardware.biometrics", "android.security"],
            "confidence": "high",
            "enabled": True
        },
        "UI": {
            "keywords": ["activity", "fragment", "view", "layout", "widget", "dialog", "adapter", "recycler"],
            "packages": ["android.app", "android.view", "android.widget", "androidx.fragment"],
            "confidence": "medium",
            "enabled": True
        },
        "Reflection": {
            "keywords": ["reflect", "invoke", "method", "field", "class", "proxy", "dynamic"],
            "packages": ["java.lang.reflect"],
            "confidence": "high",
            "enabled": True
        },
        "Native": {
            "keywords": ["jni", "native", "ndk"],
            "packages": [],
            "confidence": "high",
            "enabled": True
        }
    },
    "system_packages": [
        "android.",
        "java.",
        "javax.",
        "dalvik.",
        "com.android.",
        "sun.",
        "libcore.",
        "org.apache.",
        "org.json.",
        "org.xml.",
        "org.w3c."
    ],
    "system_paths": [
        "/system/",
        "/apex/",
        "/vendor/"
    ],
    "obfuscation_detection": {
        "min_package_parts_single_char": 2,
        "max_class_name_length": 2,
        "random_pattern_threshold": 0.7
    },
    "confidence_thresholds": {
        "high": 0.8,
        "medium": 0.5,
        "low": 0.2
    }
}


class RulesManager:
    def __init__(self):
        ensure_workshop_directories()
        self._rules_cache: Optional[Dict[str, Any]] = None
    
    def get_rules(self, force_reload: bool = False) -> Dict[str, Any]:
        if self._rules_cache is not None and not force_reload:
            return self._rules_cache
        
        if CATEGORIZATION_RULES_FILE.exists():
            try:
                with open(CATEGORIZATION_RULES_FILE, 'r', encoding='utf-8') as f:
                    self._rules_cache = json.load(f)
                logger.debug("Loaded categorization rules from file")
                return self._rules_cache
            except Exception as e:
                logger.error(f"Failed to load rules file, using defaults: {e}")
        
        self._rules_cache = DEFAULT_RULES.copy()
        self._save_rules(self._rules_cache)
        logger.info("Created default categorization rules file")
        return self._rules_cache
    
    def update_rules(self, rules: Dict[str, Any]) -> bool:
        try:
            if "format_version" not in rules:
                rules["format_version"] = DEFAULT_RULES["format_version"]
            
            required_keys = ["categories", "system_packages", "system_paths", "obfuscation_detection"]
            for key in required_keys:
                if key not in rules:
                    logger.error(f"Missing required key in rules: {key}")
                    return False
            
            self._save_rules(rules)
            self._rules_cache = rules
            logger.info("Updated categorization rules")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update rules: {e}")
            return False
    
    def reset_to_defaults(self) -> Dict[str, Any]:
        self._rules_cache = DEFAULT_RULES.copy()
        self._save_rules(self._rules_cache)
        logger.info("Reset categorization rules to defaults")
        return self._rules_cache
    
    def add_category(self, name: str, config: Dict[str, Any]) -> bool:
        rules = self.get_rules()
        
        if name in rules["categories"]:
            logger.warning(f"Category {name} already exists, updating")
        
        required = ["keywords", "packages", "confidence", "enabled"]
        for key in required:
            if key not in config:
                logger.error(f"Missing required key in category config: {key}")
                return False
        
        rules["categories"][name] = config
        return self.update_rules(rules)
    
    def remove_category(self, name: str) -> bool:
        rules = self.get_rules()
        
        if name not in rules["categories"]:
            logger.warning(f"Category {name} does not exist")
            return False
        
        del rules["categories"][name]
        return self.update_rules(rules)
    
    def toggle_category(self, name: str, enabled: bool) -> bool:
        rules = self.get_rules()
        
        if name not in rules["categories"]:
            logger.warning(f"Category {name} does not exist")
            return False
        
        rules["categories"][name]["enabled"] = enabled
        return self.update_rules(rules)
    
    def get_enabled_categories(self) -> Dict[str, Any]:
        rules = self.get_rules()
        return {
            name: config
            for name, config in rules["categories"].items()
            if config.get("enabled", True)
        }
    
    def _save_rules(self, rules: Dict[str, Any]):
        with open(CATEGORIZATION_RULES_FILE, 'w', encoding='utf-8') as f:
            json.dump(rules, f, indent=2, ensure_ascii=False)


rules_manager = RulesManager()

