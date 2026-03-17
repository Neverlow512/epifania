# Frida script compiler - compiles TypeScript with bridges
# Supports both discovery and instrumentation scripts
import frida
import os
from pathlib import Path
from typing import Dict, Optional
from core.logger import get_logger

logger = get_logger(__name__, "backend")

SCRIPTS_ROOT = Path(__file__).parent.parent / "script_vault"
COMPILED_CACHE: Dict[str, str] = {}


class ScriptCompiler:
    def __init__(self):
        self._compiler = frida.Compiler()
        self._project_root = str(SCRIPTS_ROOT)
        self._diagnostics = []
        
        def on_diagnostics(diags):
            self._diagnostics = diags
            for d in diags:
                logger.warning(f"[Compile] {d['file']['path']}:{d['file']['line']} - {d['text']}")
        
        self._compiler.on("diagnostics", on_diagnostics)
    
    def compile(
        self, 
        category: str, 
        script_name: str, 
        use_cache: bool = True,
        template_vars: Dict[str, str] = None
    ) -> str:
        # Check for pre-compiled version first
        compiled_path = SCRIPTS_ROOT / category / script_name.replace('.ts', '.compiled.js')
        if compiled_path.exists() and use_cache:
            cache_key = f"{category}/{script_name}"
            if cache_key not in COMPILED_CACHE:
                with open(compiled_path, 'r') as f:
                    COMPILED_CACHE[cache_key] = f.read()
                logger.info(f"Loaded pre-compiled script: {compiled_path}")
            
            script_code = COMPILED_CACHE[cache_key]
            
            # Apply template variables if provided
            if template_vars:
                for var_name, var_value in template_vars.items():
                    placeholder = f"{{{{{var_name}}}}}"
                    escaped_value = var_value.replace("\\", "\\\\").replace('"', '\\"').replace("'", "\\'").replace("$", "\\$")
                    script_code = script_code.replace(placeholder, escaped_value)
            
            return script_code
        
        # Compile TypeScript file
        ts_path = SCRIPTS_ROOT / category / script_name
        if not ts_path.exists():
            raise FileNotFoundError(f"Script not found: {ts_path}")
        
        cache_key = f"{category}/{script_name}"
        if cache_key in COMPILED_CACHE and use_cache:
            script_code = COMPILED_CACHE[cache_key]
            if template_vars:
                for var_name, var_value in template_vars.items():
                    placeholder = f"{{{{{var_name}}}}}"
                    escaped_value = var_value.replace("\\", "\\\\").replace('"', '\\"').replace("'", "\\'").replace("$", "\\$")
                    script_code = script_code.replace(placeholder, escaped_value)
            return script_code
        
        logger.info(f"Compiling script: {ts_path}")
        self._diagnostics = []
        
        try:
            bundle = self._compiler.build(
                entrypoint=str(ts_path),
                project_root=self._project_root
            )
            
            COMPILED_CACHE[cache_key] = bundle
            logger.info(f"Compiled {script_name}: {len(bundle)} bytes")
            
            # Save compiled version for future use
            with open(compiled_path, 'w') as f:
                f.write(bundle)
            logger.info(f"Saved compiled script to: {compiled_path}")
            
            script_code = bundle
            if template_vars:
                for var_name, var_value in template_vars.items():
                    placeholder = f"{{{{{var_name}}}}}"
                    escaped_value = var_value.replace("\\", "\\\\").replace('"', '\\"').replace("'", "\\'").replace("$", "\\$")
                    script_code = script_code.replace(placeholder, escaped_value)
            
            return script_code
            
        except Exception as e:
            logger.error(f"Compilation failed for {script_name}: {e}")
            if self._diagnostics:
                for d in self._diagnostics:
                    logger.error(f"  {d['text']}")
            raise
    
    def get_compiled(self, category: str, script_name: str) -> Optional[str]:
        compiled_name = script_name.replace('.ts', '.compiled.js').replace('.js', '.compiled.js')
        compiled_path = SCRIPTS_ROOT / category / compiled_name
        
        if compiled_path.exists():
            with open(compiled_path, 'r') as f:
                return f.read()
        return None


script_compiler = ScriptCompiler()

