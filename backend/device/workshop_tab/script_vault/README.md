# Frida JavaScript Scripts Vault

This directory contains all Frida JavaScript and TypeScript scripts used by the Workshop backend, organized by purpose.

## Structure

```
script_vault/
├── package.json           # NPM project with frida-java-bridge dependency
├── node_modules/
│   └── frida-java-bridge/
├── discovery/             # Scripts for method/class/module discovery
│   ├── enumerate_classes.ts           # Java classes (TypeScript + bridge)
│   ├── enumerate_classes.compiled.js  # Pre-compiled bundle
│   ├── enumerate_methods.ts           # Java methods via RPC (TypeScript + bridge)
│   ├── enumerate_methods.compiled.js  # Pre-compiled bundle
│   ├── enumerate_modules.js           # Native modules (plain JS)
│   └── enumerate_exports.js           # Native exports via RPC (plain JS)
├── hooking/               # Scripts for runtime hooking (future)
└── tracing/               # Scripts for execution tracing (future)
```

## Script Types

### TypeScript (.ts) - Java Bridge Required
Used when accessing Java APIs via `frida-java-bridge`. These scripts are compiled to JavaScript bundles that include the bridge.

**When to use:**
- Enumerating Java classes (`Java.enumerateLoadedClassesSync()`)
- Accessing Java methods (`Java.use()`, `Java.cast()`)
- Any operation requiring the Java runtime

**Compilation:**
- Handled by `script_compiler.py` using Frida's Compiler API
- Pre-compiled bundles cached for performance (~750KB each)
- Automatically recompiled if source changes

### JavaScript (.js) - Native API
Used for Frida's core APIs that don't require bridges.

**When to use:**
- Enumerating native modules (`Process.enumerateModules()`)
- Enumerating exports (`Module.enumerateExports()`)
- Native memory operations
- Core Frida functionality

**Loading:**
- Loaded directly by `script_loader.py`
- No compilation needed

## Discovery Scripts

### enumerate_classes.ts (TypeScript)
Enumerates all loaded Java classes in the target process using `frida-java-bridge`.
- **Output:** Array of class names sent via `send()` message
- **Bridge:** Requires `frida-java-bridge`
- **Usage:** Script loaded once, runs immediately, sends all classes

### enumerate_methods.ts (TypeScript + RPC)
Enumerates methods for Java classes using RPC exports for efficient batch processing.
- **Architecture:** RPC-based - script loaded once, `getMethods(className)` called per class
- **RPC Export:** `rpc.exports.getMethods(className: string)` returns `{success, class_name, methods[], error?}`
- **Output:** Method objects with name, signature, return_type, parameters, modifiers
- **Bridge:** Requires `frida-java-bridge`
- **Usage:** Script loaded once at start, RPC called for each class, unloaded at end
- **No timeouts:** Runs until all classes processed

### enumerate_modules.js (JavaScript)
Enumerates all native modules (shared libraries) loaded in the process.
- **Output:** Array of module objects with name, path, base_address, size
- **API:** Uses `Process.enumerateModules()` (no bridge needed)
- **Usage:** Script loaded, runs immediately, sends all modules

### enumerate_exports.js (JavaScript + RPC)
Enumerates exports from native modules using RPC exports for efficient batch processing.
- **Architecture:** RPC-based - script loaded once, `getExports(moduleName)` called per module
- **RPC Export:** `rpc.exports.getExports(moduleName: string)` returns `{success, exports[], error?}`
- **Output:** Export objects with name, address, type
- **API:** Uses `Module.enumerateExports()` (no bridge needed)
- **Usage:** Script loaded once at start, RPC called for each module, unloaded at end
- **No timeouts:** Runs until all modules processed

## RPC Architecture (No Template Variables)

Scripts use Frida's RPC mechanism instead of template variable replacement. This prevents issues with compiled bundle corruption.

**Why RPC instead of templates:**
- Template replacement (`{{CLASS_NAME}}`) corrupts Frida's compiled bundle byte count header
- RPC allows passing parameters dynamically without modifying the script
- Script is loaded once and reused for multiple calls (more efficient)
- No per-item timeouts - processing continues until complete

**RPC Pattern:**
```typescript
// TypeScript script
rpc.exports = {
    getMethods(className: string): Promise<Result> {
        return new Promise((resolve) => {
            Java.perform(() => {
                // ... enumerate methods for className
                resolve({ success: true, methods: [...] });
            });
        });
    }
};
```

```python
# Python caller
script = session.create_script(compiled_code)
script.load()
for class_name in classes:
    result = script.exports_sync.get_methods(class_name)
script.unload()
```

## Categorization Integration

All enumerated data is sent back to Python where the categorizer adds category fields:

**Java:**
- Each class gets: `class_category`, `class_confidence`, `class_category_reason`
- Each method gets: `method_category`, `method_confidence`, `method_category_reason`

**Native:**
- Each module gets: `module_category`, `module_confidence`, `module_category_reason`
- Each export gets: `export_category`, `export_confidence`, `export_category_reason`

Scripts only collect raw data; Python handles all categorization logic.

## Console Logging

Scripts use `console.log()` for debugging. These logs appear in:
- Frida's console output
- Workshop discovery logs (`logs/workshop/discovery/`)

## Error Handling

All scripts should:
1. Wrap risky operations in try-catch blocks
2. Return success/error status in RPC responses
3. Include error messages for debugging
4. Never throw - always resolve with error info

Example (RPC pattern):
```typescript
rpc.exports = {
    getData(param: string): Promise<any> {
        return new Promise((resolve) => {
            try {
                const result = performOperation(param);
                resolve({ success: true, data: result });
            } catch (e: any) {
                resolve({ success: false, data: [], error: e.toString() });
            }
        });
    }
};
```

## Dependencies

Install dependencies before first use:
```bash
cd backend/device/workshop_tab/script_vault
npm install
```

This installs `frida-java-bridge` required for TypeScript scripts.

## Compilation

TypeScript scripts must be compiled before use:
```python
# Automatic compilation via script_compiler.py
from device.workshop_tab.discovery.script_compiler import script_compiler
compiled_code = script_compiler.compile("discovery", "enumerate_methods.ts")
```

Pre-compiled `.compiled.js` files are cached and reused if source hasn't changed.
