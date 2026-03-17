# Frida script loader - loads JS scripts from the vault
from pathlib import Path
from typing import Dict

SCRIPTS_ROOT = Path(__file__).parent.parent / "script_vault"


class ScriptLoader:
    def __init__(self):
        self._cache: Dict[str, str] = {}
    
    def load_script(self, category: str, script_name: str, template_vars: Dict[str, str] = None) -> str:
        cache_key = f"{category}/{script_name}"
        
        if cache_key not in self._cache:
            script_path = SCRIPTS_ROOT / category / script_name
            
            if not script_path.exists():
                raise FileNotFoundError(f"Script not found: {script_path}")
            
            with open(script_path, 'r', encoding='utf-8') as f:
                self._cache[cache_key] = f.read()
        
        script_code = self._cache[cache_key]
        
        if template_vars:
            for var_name, var_value in template_vars.items():
                placeholder = f"{{{{{var_name}}}}}"
                # Escape special characters for JavaScript
                escaped_value = var_value.replace("\\", "\\\\").replace("'", "\\'").replace("$", "\\$")
                script_code = script_code.replace(placeholder, escaped_value)
        
        return script_code
    
    def clear_cache(self):
        self._cache.clear()


script_loader = ScriptLoader()

