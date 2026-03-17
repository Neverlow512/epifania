import json
import hashlib
from typing import List, Dict
from device.workshop_tab.discovery.script_compiler import script_compiler


def generate_hook_id(hook_dict: Dict) -> str:
    if hook_dict.get("type") == "java":
        unique_str = f"{hook_dict.get('class_name', '')}.{hook_dict.get('method_name', '')}:{hook_dict.get('signature', '')}"
    else:
        unique_str = f"{hook_dict.get('module_name', '')}.{hook_dict.get('function_name', '')}"
    
    return hashlib.md5(unique_str.encode()).hexdigest()[:12]


def generate_java_observer_script(hooks: List[dict]) -> str:
    hooks_with_ids = []
    for hook in hooks:
        hook_copy = hook.copy()
        if "id" not in hook_copy:
            hook_copy["id"] = generate_hook_id(hook)
        hooks_with_ids.append(hook_copy)
    
    script_code = script_compiler.compile(
        "instrumentation/observer/java",
        "observer_java.ts"
    )
    
    return script_code, hooks_with_ids


def generate_native_observer_script(hooks: List[dict]) -> str:
    hooks_with_ids = []
    for hook in hooks:
        hook_copy = hook.copy()
        if "id" not in hook_copy:
            hook_copy["id"] = generate_hook_id(hook)
        hooks_with_ids.append(hook_copy)
    
    script_code = script_compiler.compile(
        "instrumentation/observer/native",
        "observer_native.ts"
    )
    
    return script_code, hooks_with_ids
