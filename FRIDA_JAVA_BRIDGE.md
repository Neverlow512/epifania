# Frida Java Bridge Integration

## Problem

Starting with Frida 17.0.0, runtime bridges (Java, ObjC, Swift) are **no longer bundled** with Frida's core runtime. They are only included in `frida-tools` (the CLI).

Reference: [Frida 17.0.0 Release Notes](https://frida.re/news/2025/05/17/frida-17-0-0-released/)

This caused Java class enumeration to fail in Python with:
```
ReferenceError: 'Java' is not defined
```

## Solution

To use Java APIs in Frida Python scripts, you must:

1. Install the bridge package:
```bash
npm install frida-java-bridge
```

2. Create TypeScript files that import the bridge:
```typescript
import Java from "frida-java-bridge";

Java.perform(() => {
    const classes = Java.enumerateLoadedClassesSync();
    send({ type: 'classes', data: classes });
});
```

3. Compile using Frida's Compiler API:
```python
import frida

compiler = frida.Compiler()
bundle = compiler.build(
    entrypoint="/path/to/script.ts",
    project_root="/path/to/project"
)

# Use the compiled bundle
script = session.create_script(bundle)
script.load()
```

## Implementation in This Project

### Structure

```
backend/device/workshop_tab/
├── js_scripts_vault/
│   ├── package.json              # NPM project with frida-java-bridge
│   ├── node_modules/
│   │   └── frida-java-bridge/
│   └── discovery/
│       ├── enumerate_classes.ts           # Java-dependent (TypeScript)
│       ├── enumerate_classes.compiled.js  # Pre-compiled bundle (749KB)
│       ├── enumerate_methods.ts           # Java-dependent (TypeScript)
│       ├── enumerate_methods.compiled.js  # Pre-compiled bundle (751KB)
│       ├── enumerate_modules.js           # Native API (plain JS, no bridge needed)
│       └── enumerate_exports.js           # Native API (plain JS, no bridge needed)
└── discovery/
    ├── script_compiler.py        # Compiles TS → JS with bridges
    └── java_discovery.py         # Uses compiled bundles
```

### Key Components

**1. Script Compiler (`script_compiler.py`)**
- Compiles TypeScript scripts using `frida.Compiler`
- Caches pre-compiled bundles for performance
- Supports template variable substitution (e.g., `{{CLASS_NAME}}`)

**2. Java Discovery (`java_discovery.py`)**
- Uses `script_compiler.compile("discovery", "enumerate_classes.ts")` instead of raw JS
- Pre-compiled bundles are loaded from disk if available
- Only Java-dependent scripts need TypeScript + compilation

### Which Scripts Need Bridges?

**Java-dependent (TypeScript required):**
- `enumerate_classes.ts` - uses `Java.enumerateLoadedClassesSync()`
- `enumerate_methods.ts` - uses `Java.use()`, `Java.cast()`

**Native API (plain JavaScript):**
- `enumerate_modules.js` - uses `Process.enumerateModules()`
- `enumerate_exports.js` - uses `Module.enumerateExports()`

## Performance Notes

- Compiled bundles are ~750KB each (includes entire Java bridge)
- Pre-compiled bundles are cached and loaded from disk
- First compilation takes ~200ms, subsequent loads are instant
- No impact on runtime performance once loaded

## Testing

Verified working with:
- Frida 17.5.1 (client & server)
- Android 9 (Genymotion emulator)
- Successfully enumerated 12,568+ Java classes from `com.android.systemui`

