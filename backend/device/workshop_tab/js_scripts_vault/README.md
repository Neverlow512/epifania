# Frida JavaScript Scripts Vault

This directory contains all Frida JavaScript scripts used by the Workshop backend, organized by purpose.

## Structure

```
js_scripts_vault/
├── discovery/              # Scripts for method/class/module discovery
│   ├── enumerate_classes.js
│   ├── enumerate_methods.js
│   ├── enumerate_modules.js
│   └── enumerate_exports.js
├── hooking/               # Scripts for runtime hooking (future)
└── tracing/               # Scripts for execution tracing (future)
```

## Discovery Scripts

### enumerate_classes.js
Enumerates all loaded Java classes in the target process.
- **Output:** Array of class names
- **Usage:** Called once per discovery

### enumerate_methods.js
Enumerates all methods for a specific Java class.
- **Template Variables:** `{{CLASS_NAME}}` - fully qualified class name
- **Output:** Array of method objects with signatures and metadata
- **Usage:** Called once per class

### enumerate_modules.js
Enumerates all native modules (shared libraries) loaded in the process.
- **Output:** Array of module objects with name, path, base address, size
- **Usage:** Called once per discovery

### enumerate_exports.js
Enumerates all exported functions from a specific native module.
- **Template Variables:** `{{MODULE_NAME}}` - module name (e.g., libnative.so)
- **Output:** Array of export objects with name, address, type
- **Usage:** Called once per module

## Template Variables

Scripts may contain template variables in the format `{{VARIABLE_NAME}}` which are replaced by the Python code before execution.

## Console Logging

Scripts use `console.log()` for debugging. These logs appear in:
- Frida's console output
- Workshop discovery logs (`logs/workshop/discovery/`)

## Error Handling

All scripts should:
1. Wrap risky operations in try-catch blocks
2. Send success/error status in the response
3. Include error messages for debugging

