# Observer Session: {session_name}

## Session Information
- **App Package**: {app_package}
- **Device**: {device_id}
- **Session Path**: {session_path}
- **Hooks Count**: {hooks_count}

## Files in This Directory
- **`hooks.json`** - Hook configuration (class names, methods, signatures) in JSON format
- **`observer_template.ts`** - Original TypeScript source template (~200 lines, readable)
- **`compiled_script.js`** - Full compiled script with frida-java-bridge bundled (~750KB)

## Quick Usage

### Option 1: Use with Frida CLI (Compiled Script)
Inject the compiled script directly into a running app:
```bash
frida -U -n "{app_package}" -l compiled_script.js
```

Or spawn the app:
```bash
frida -U -f "{app_package}" -l compiled_script.js
```

Then in the Frida REPL, install the hooks:
```javascript
rpc.exports.installHooks({hooks_sample})
```

### Option 2: Customize the TypeScript Template
1. Open `observer_template.ts` - it's clean, readable TypeScript
2. Modify the hook implementation logic as needed
3. The template uses RPC exports to install hooks dynamically
4. See `hooks.json` for the exact methods that were hooked

### Option 3: Use in Epifania
Load this session back into Epifania's Observer tool:
- Import the hooks from `hooks.json`
- Or reference this session for documentation

## Hook Details
View `hooks.json` for complete details including:
- Hook IDs
- Fully qualified class names
- Method names with signatures
- Return types and parameters

## Logs
Session logs are saved separately at:
`{session_path}`

This includes:
- `operations.log` - Hook installation events
- `aggregated.log` - All hook calls aggregated
- `console_raw.log` - Raw Frida console output
- Per-hook logs in `hooks/` subdirectory
