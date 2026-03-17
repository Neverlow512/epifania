# Inclusion/exclusion filter for classes and modules with three-tier filtering
import re
from enum import Enum
from typing import Dict, Any, List, Tuple
from device.workshop_tab.config.rules_manager import rules_manager


class FilterMode(str, Enum):
    FOCUSED = "focused"
    PACKAGE = "package"
    ALL = "all"


class SourceType(str, Enum):
    APP = "app"
    BUNDLED = "bundled"
    SYSTEM = "system"


class DiscoveryFilter:
    def __init__(
        self, 
        package_id: str, 
        filter_mode: FilterMode = FilterMode.FOCUSED,
        app_focused_patterns: List[str] = None
    ):
        self.package_id = package_id
        self.filter_mode = filter_mode
        self._rules = rules_manager.get_rules()
        
        # App Focused custom patterns for focused mode
        # If provided, these patterns are used instead of just package_id matching
        self._app_focused_patterns = app_focused_patterns or []
        self._compiled_patterns = self._compile_patterns(self._app_focused_patterns)
        
        self._system_packages = self._rules.get("system_packages", [
            "android.", "java.", "javax.", "dalvik.", "com.android.",
            "sun.", "libcore.", "org.apache.", "org.json.", "org.xml.", "org.w3c."
        ])
        self._system_paths = self._rules.get("system_paths", [
            "/system/", "/apex/", "/vendor/"
        ])
        
        self.included_classes: List[Dict[str, Any]] = []
        self.skipped_classes: List[Dict[str, str]] = []
        self.included_modules: List[Dict[str, Any]] = []
        self.skipped_modules: List[Dict[str, str]] = []
        
        self._source_stats = {
            "classes": {"app": 0, "bundled": 0, "system": 0},
            "modules": {"app": 0, "bundled": 0, "system": 0}
        }
        
        self._total_classes_seen = 0
        self._total_modules_seen = 0
    
    def _compile_patterns(self, patterns: List[str]) -> List[re.Pattern]:
        compiled = []
        for pattern in patterns:
            if not pattern:
                continue
            # Convert glob-like patterns to regex
            # pattern.* becomes pattern\..* (match pattern. followed by anything)
            # pattern becomes exact match or prefix
            if pattern.endswith(".*"):
                regex_pattern = "^" + re.escape(pattern[:-2]) + r"\."
            elif pattern.endswith("*"):
                regex_pattern = "^" + re.escape(pattern[:-1])
            else:
                # Exact match or single-letter class match
                regex_pattern = "^" + re.escape(pattern) + r"($|\.)"
            try:
                compiled.append(re.compile(regex_pattern))
            except re.error:
                pass
        return compiled
    
    def _matches_app_focused_patterns(self, class_name: str) -> bool:
        if not self._compiled_patterns:
            # Default: match package_id prefix
            return class_name.startswith(self.package_id)
        
        for pattern in self._compiled_patterns:
            if pattern.search(class_name):
                return True
        return False
    
    def classify_class_source(
        self, 
        class_name: str, 
        loader_type: str = None,
        loader_path: str = None
    ) -> SourceType:
        # Step 1: Use ClassLoader as source of truth (100% accurate)
        if loader_type:
            # Check if loaded by system ClassLoader
            if loader_type in ["null", "java.lang.BootClassLoader"]:
                return SourceType.SYSTEM
            
            # Everything else (PathClassLoader, DexClassLoader, InMemoryDexClassLoader) is from APK
            # Now sub-classify APK content
            if class_name.startswith(self.package_id):
                return SourceType.APP
            else:
                return SourceType.BUNDLED
        
        # Step 2: Fallback to name-based classification (for legacy data without loader info)
        if class_name.startswith(self.package_id):
            return SourceType.APP
        
        if loader_path and self.package_id in loader_path:
            return SourceType.APP
        
        for prefix in self._system_packages:
            if class_name.startswith(prefix):
                return SourceType.SYSTEM
        
        return SourceType.BUNDLED
    
    def classify_module_source(self, module_name: str, module_path: str) -> SourceType:
        if self.package_id in module_path:
            return SourceType.APP
        
        package_path_variant = self.package_id.replace(".", "")
        if "/data/app/" in module_path and package_path_variant in module_path:
            return SourceType.APP
        
        for system_path in self._system_paths:
            if module_path.startswith(system_path):
                return SourceType.SYSTEM
        
        return SourceType.BUNDLED
    
    def should_include_class(
        self, 
        class_name: str, 
        loader_type: str = None,
        loader_path: str = None
    ) -> Tuple[bool, str]:
        if class_name.startswith("["):
            return False, "array_type_descriptor"
        
        source = self.classify_class_source(class_name, loader_type, loader_path)
        
        if self.filter_mode == FilterMode.FOCUSED:
            # When custom patterns are configured, use pattern matching
            # Otherwise fall back to source == APP check
            if self._compiled_patterns:
                include = self._matches_app_focused_patterns(class_name)
                reason = "pattern_match" if include else f"source:{source.value}"
            else:
                include = source == SourceType.APP
                reason = f"source:{source.value}"
            return include, reason
        elif self.filter_mode == FilterMode.PACKAGE:
            include = source in [SourceType.APP, SourceType.BUNDLED]
        else:  # FilterMode.ALL
            include = True
        
        return include, f"source:{source.value}"
    
    def should_include_module(self, module_name: str, module_path: str) -> Tuple[bool, str]:
        source = self.classify_module_source(module_name, module_path)
        
        if self.filter_mode == FilterMode.FOCUSED:
            include = source == SourceType.APP
        elif self.filter_mode == FilterMode.PACKAGE:
            include = source in [SourceType.APP, SourceType.BUNDLED]
        else:  # FilterMode.ALL
            include = True
        
        return include, f"source:{source.value}"
    
    def is_class_obfuscated(self, class_name: str) -> bool:
        obf_config = self._rules.get("obfuscation_detection", {})
        min_single_char = obf_config.get("min_package_parts_single_char", 2)
        max_class_len = obf_config.get("max_class_name_length", 2)
        
        parts = class_name.split(".")
        if len(parts) > 1:
            single_char_parts = sum(1 for p in parts[:-1] if len(p) == 1)
            if single_char_parts >= min_single_char:
                return True
        
        class_simple = parts[-1] if parts else class_name
        if len(class_simple) <= max_class_len and class_simple.isalpha():
            if not class_simple[0].isupper():
                return True
            if len(class_simple) == 1:
                return True
        
        if re.match(r'^[a-z]{1,2}\.[a-z]{1,2}\.[a-z]{1,2}', class_name):
            return True
        
        return False
    
    def filter_class(
        self, 
        class_name: str, 
        class_data: Dict[str, Any], 
        loader_type: str = None,
        loader_path: str = None
    ):
        self._total_classes_seen += 1
        source = self.classify_class_source(class_name, loader_type, loader_path)
        include, reason = self.should_include_class(class_name, loader_type, loader_path)
        
        self._source_stats["classes"][source.value] += 1
        
        if include:
            class_data["source"] = source.value
            class_data["filter_reason"] = reason
            class_data["is_obfuscated"] = self.is_class_obfuscated(class_name)
            
            # Store loader info in class data
            if loader_type:
                class_data["loader_type"] = loader_type
                class_data["loader_path"] = loader_path
                class_data["is_from_apk"] = loader_type not in ["null", "java.lang.BootClassLoader"]
            
            self.included_classes.append(class_data)
        else:
            self.skipped_classes.append({
                "name": class_name,
                "source": source.value,
                "reason": reason
            })
        
        return include
    
    def filter_module(self, module_name: str, module_data: Dict[str, Any], module_path: str):
        self._total_modules_seen += 1
        source = self.classify_module_source(module_name, module_path)
        include, reason = self.should_include_module(module_name, module_path)
        
        self._source_stats["modules"][source.value] += 1
        
        if include:
            module_data["source"] = source.value
            module_data["is_system"] = source == SourceType.SYSTEM
            module_data["filter_reason"] = reason
            self.included_modules.append(module_data)
        else:
            self.skipped_modules.append({
                "name": module_name,
                "path": module_path,
                "source": source.value,
                "reason": reason
            })
        
        return include
    
    def set_total_counts(self, total_classes: int, total_modules: int):
        self._total_classes_seen = total_classes
        self._total_modules_seen = total_modules
    
    def get_verification_stats(self) -> Dict[str, Any]:
        total_classes = max(self._total_classes_seen, len(self.included_classes) + len(self.skipped_classes))
        total_modules = max(self._total_modules_seen, len(self.included_modules) + len(self.skipped_modules))
        
        classes_check = f"{len(self.included_classes)} + {len(self.skipped_classes)} = {total_classes}"
        modules_check = f"{len(self.included_modules)} + {len(self.skipped_modules)} = {total_modules}"
        
        classes_ok = len(self.included_classes) + len(self.skipped_classes) == total_classes
        modules_ok = len(self.included_modules) + len(self.skipped_modules) == total_modules
        
        return {
            "total_classes_found": total_classes,
            "classes_included": len(self.included_classes),
            "classes_skipped": len(self.skipped_classes),
            "total_modules_found": total_modules,
            "modules_included": len(self.included_modules),
            "modules_skipped": len(self.skipped_modules),
            "filter_mode": self.filter_mode.value,
            "source_breakdown": self._source_stats,
            "verification": {
                "classes_check": f"{classes_check} ({'OK' if classes_ok else 'MISMATCH'})",
                "modules_check": f"{modules_check} ({'OK' if modules_ok else 'MISMATCH'})",
                "nothing_lost": classes_ok and modules_ok
            },
            "skipped_classes_sample": self.skipped_classes[:100],
            "skipped_modules_sample": self.skipped_modules[:50]
        }
    
    def reset(self):
        self.included_classes = []
        self.skipped_classes = []
        self.included_modules = []
        self.skipped_modules = []
        self._source_stats = {
            "classes": {"app": 0, "bundled": 0, "system": 0},
            "modules": {"app": 0, "bundled": 0, "system": 0}
        }
        self._total_classes_seen = 0
        self._total_modules_seen = 0
