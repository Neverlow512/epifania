# Workshop Tab - Backend Design

## Overview

The Workshop tab enables dynamic analysis of running applications by discovering and categorizing all hookable Java methods and native functions. It provides a foundation for Frida script injection and runtime manipulation.

## Core Functionality

### 1. Method Discovery

#### Two-Pass Discovery Process
**Pass 1: Raw Enumeration** - Get everything first
- Enumerate ALL classes without any filtering
- Enumerate ALL methods per class
- Enumerate ALL native modules and exports
- Store raw data before any categorization

**Pass 2: Categorization** - Apply rules to complete dataset
- Run categorizer on the complete raw data
- Apply user-configurable rules
- Track counts for verification

#### Discovery Operations
- **Attach to running process** using existing Frida server (reuse from Device tab)
- **Auto-attach only** when user starts discovery process
- **Manual detach only** - user controls when to disconnect
- **Enumerate Java classes** via Frida's `Java.enumerateLoadedClasses()`
- **Enumerate Java methods** for each class using `Java.use(className).$methods`
- **Enumerate native modules** (`.so` files) via `session.enumerate_modules()`
- **Enumerate native exports** for each module using `module.enumerate_exports()`
- **No time limits** - discovery runs until complete or user cancels
- **Progress shown as percentage** - no time estimates

### 2. Smart Categorization

#### Dynamic Rules Configuration
- **Rules stored in config file** - `backend/workshop_data/config/categorization_rules.json`
- **Frontend can modify rules** via API endpoints
- **Confidence levels configurable** per category
- **Changes persist** across sessions
- **Default rules provided** but fully customizable

#### Default Categories
- **Network**: http, url, okhttp, retrofit, websocket, socket, request, response
- **Crypto**: cipher, encrypt, decrypt, crypto, aes, rsa, ssl, tls, keystore
- **Storage**: sqlite, database, preference, sharedpref, file, contentprovider
- **Security**: auth, authentication, biometric, fingerprint, keyguard, token
- **UI**: activity, fragment, view, layout, widget
- **Unknown/Obfuscated**: single-letter packages (a.b.c), short class names
- **Unknown**: everything else that doesn't match patterns

#### Confidence Levels (Frontend-Configurable)
- **High**: Known Android/library packages (javax.crypto, okhttp3)
- **Medium**: Keyword found in class name only
- **Low**: No patterns matched (defaults to Unknown)
- **Threshold setting**: Frontend can set minimum confidence to display

#### Obfuscation Detection
- Multiple single-letter package parts (a.b.c)
- Class name is 1-2 characters long
- Random character combinations

#### Ensuring Nothing App-Related is Missed

**Inclusion Rules (Always Include):**
- Everything starting with app's package prefix (e.g., com.tiktok.*)
- Any class loaded from app's APK path
- Any .so file from app's lib directory (/data/app/{package}/lib/)
- Any class/module that doesn't match system exclusion patterns

**Exclusion Rules (Only When System Libraries Toggle is OFF):**
- Paths starting with `/system/`
- Packages starting with: `android.`, `java.`, `javax.`, `dalvik.`, `com.android.`
- **Never exclude** if path contains app's package name

**Verification:**
- Log total classes found vs classes included
- Track `skipped_classes` list with reasons (only system libs)
- Verify: `included + skipped = total` (nothing lost)
- Include verification stats in metadata

### 3. Session Management (Multi-Layer)

#### Layer 1: Browser Tab Lock
- **One tab per device** can access Workshop tab
- **Session timeout: 30 seconds** - stale locks auto-release
- **Heartbeat required** - frontend sends keep-alive every 10 seconds
- **Reuse existing pattern** from Processes/Packages polling session management
- **Lock key**: `{device_id}:workshop`

#### Layer 2: Frida Session
- **Reuse Frida server** already running from Device tab (don't start new server)
- **Auto-attach only** when discovery starts (user initiates)
- **Manual detach only** - user explicitly detaches via UI control
- **No auto-detach** - session stays alive until user decides to disconnect
- **No auto-stop** - Frida server stays running until user stops it
- **Session pooling** - reuse if already attached to same PID

#### Layer 3: Discovery State
- **Track active discoveries** during runtime only
- **Progress tracking**: percentage-based, no time estimates
- **Status states**: idle, running, complete, error
- **One discovery at a time** per device
- **No memory caching** - results saved to disk, loaded on demand

### 4. Frida Control Panel (Workshop Tab)
- **Import Frida controls** from Device tab (start/stop/restart server)
- **Attach/Detach controls** for process connection
- **Connection status indicator** - show if attached to process
- **Server status indicator** - show if Frida server is running
- **All controls are manual** - no automatic actions

### 5. Data Storage

#### Directory Structure
```
backend/workshop_data/                    # Never committed to git
├── config/
│   └── categorization_rules.json        # User-configurable rules
└── discoveries/
    ├── com.tiktok/
    │   ├── 2024-12-07_v1.0.0/           # One folder per discovery
    │   │   ├── metadata.json            # Package info, device, timestamps, verification stats
    │   │   ├── java_classes.json        # All Java classes and methods
    │   │   ├── native_modules.json      # All native modules and exports
    │   │   └── user_data.json           # User notes, recategorization (future)
    │   └── 2024-12-08_v1.0.1/
    │       └── ...
    └── com.instagram/
        └── 2024-12-07_v2.5.0/
            └── ...
```

#### Storage Format: Separate JSON Files
- **One folder per discovery session**
- **Folder name**: `{date}_{version}`
- **Separate files** for metadata, Java, Native, and user data
- **Save only when user clicks "Save"** - not automatic
- **No limits** on number of saved discoveries

#### File: categorization_rules.json (User-Configurable)
```json
{
  "format_version": "1.0",
  "categories": {
    "Network": {
      "keywords": ["http", "url", "okhttp", "retrofit", "websocket", "socket"],
      "packages": ["okhttp3", "retrofit2", "com.squareup.okhttp"],
      "confidence": "high",
      "enabled": true
    },
    "Crypto": {
      "keywords": ["cipher", "encrypt", "decrypt", "crypto", "aes", "rsa", "ssl"],
      "packages": ["javax.crypto", "java.security"],
      "confidence": "high",
      "enabled": true
    }
  },
  "system_packages": ["android.", "java.", "javax.", "dalvik.", "com.android."],
  "system_paths": ["/system/"],
  "obfuscation_detection": {
    "min_package_parts_single_char": 2,
    "max_class_name_length": 2
  }
}
```

#### File: metadata.json
```json
{
  "format_version": "1.0",
  "package_id": "com.tiktok",
  "package_name": "TikTok",
  "package_version": "1.0.0",
  "version_code": 123456,
  "discovery_timestamp": "2024-12-07T15:30:00Z",
  "device_serial": "emulator-5554",
  "device_model": "Pixel 5",
  "android_version": "13",
  "pid": 12345,
  "stats": {
    "total_classes_found": 5000,
    "app_classes_included": 2453,
    "system_classes_skipped": 2547,
    "total_methods": 18456,
    "categorized_classes": 119,
    "unknown_classes": 2334,
    "total_native_modules_found": 150,
    "app_modules_included": 87,
    "system_modules_skipped": 63,
    "total_native_exports": 15234,
    "system_libraries_included": false
  },
  "verification": {
    "classes_check": "2453 + 2547 = 5000 (OK)",
    "modules_check": "87 + 63 = 150 (OK)",
    "nothing_lost": true
  },
  "skipped_classes": [
    {"name": "android.app.Activity", "reason": "system_package"},
    {"name": "java.lang.String", "reason": "system_package"}
  ],
  "skipped_modules": [
    {"name": "libc.so", "path": "/system/lib64/libc.so", "reason": "system_path"}
  ]
}
```

#### File: java_classes.json
```json
{
  "format_version": "1.0",
  "classes": [
    {
      "name": "com.tiktok.network.HttpManager",
      "category": "Network",
      "confidence": "high",
      "reason": "Keyword in package: network",
      "source": "app",
      "method_count": 15,
      "methods": [
        {
          "name": "sendRequest",
          "signature": "(Ljava/lang/String;[B)V",
          "return_type": "void",
          "parameters": ["String", "byte[]"],
          "is_native": false,
          "is_public": true,
          "is_static": false
        }
      ]
    }
  ]
}
```

#### File: native_modules.json
```json
{
  "format_version": "1.0",
  "modules": [
    {
      "name": "libnative.so",
      "path": "/data/app/.../lib/arm64/libnative.so",
      "base_address": "0x7b8c000000",
      "size": 524288,
      "is_system": false,
      "source": "app",
      "exports": [
        {
          "name": "SSL_write",
          "address": "0x7b8c001234",
          "type": "function",
          "category": "Network",
          "confidence": "high"
        }
      ]
    }
  ]
}
```

#### File: user_data.json (Future)
```json
{
  "format_version": "1.0",
  "recategorized": [],
  "notes": [],
  "bookmarks": []
}
```

### 6. Dedicated Workshop Logs

#### Log Directory Structure
```
logs/
├── application/              # Existing - backend logs
├── devices/                  # Existing - device logs
├── diagnostics/              # Existing - diagnostic logs
├── services/                 # Existing - service logs
└── workshop/                 # NEW - Workshop-specific logs
    ├── discovery/
    │   └── {package_id}_{timestamp}.log    # Per-discovery detailed log
    ├── frida/
    │   └── session_{device_id}.log         # Frida session operations
    ├── categorization/
    │   └── {package_id}_{timestamp}.log    # Categorization decisions
    └── errors/
        └── workshop_errors.log             # Workshop-specific errors
```

#### Per-Discovery Log File
Each discovery creates its own log file with:
- Discovery start time and parameters
- Each phase transition with progress
- Classes/methods enumerated (counts)
- Categorization decisions made
- Any warnings or issues encountered
- Verification results
- Discovery completion stats

#### Frida Session Log
- Attach/detach operations
- Connection status changes
- Any Frida-specific errors or warnings
- Session reuse events

#### Categorization Log
- Rules applied and results
- Why each class was categorized a certain way
- Obfuscation detection results
- Confidence level assignments

### 7. Progress Streaming

#### WebSocket Communication
- **Reuse existing WebSocket pattern** from log streaming
- **Real-time progress updates** during discovery
- **Percentage-based progress** - no time estimates or limits
- **Messages**: `{"progress": 35, "phase": "java_enum", "message": "Enumerating classes...", "count": 1500}`
- **Connection lifecycle**: open on discovery start, stays open until complete or cancelled

#### Progress Phases
1. **0-5%**: Attaching to process
2. **5-40%**: Enumerating Java classes and methods (raw)
3. **40-55%**: Categorizing Java classes
4. **55-75%**: Enumerating native modules and exports (raw)
5. **75-90%**: Categorizing native functions
6. **90-95%**: Verification and stats calculation
7. **95-100%**: Building final result

### 8. API Endpoints

#### Session Management
- `POST /api/devices/{device_id}/workshop/session/acquire` - Lock workshop tab
- `POST /api/devices/{device_id}/workshop/session/heartbeat` - Keep session alive
- `POST /api/devices/{device_id}/workshop/session/release` - Unlock on tab close

#### Frida Control (import from Device tab)
- `POST /api/devices/{device_id}/workshop/frida/attach` - Attach to process
- `POST /api/devices/{device_id}/workshop/frida/detach` - Detach from process (manual only)
- `GET /api/devices/{device_id}/workshop/frida/status` - Get attachment status

#### Configuration (Dynamic Rules)
- `GET /api/workshop/config/rules` - Get current categorization rules
- `PUT /api/workshop/config/rules` - Update categorization rules
- `POST /api/workshop/config/rules/reset` - Reset to default rules

#### Discovery
- `POST /api/devices/{device_id}/workshop/discover` - Start discovery
  - Body: `{package_id, pid, include_system_libs: bool}`
  - Returns: discovery_id
- `POST /api/devices/{device_id}/workshop/discover/cancel` - Cancel running discovery
- `GET /api/devices/{device_id}/workshop/discovery/status` - Get current progress
- `WS /ws/devices/{device_id}/workshop/discovery` - Real-time progress stream

#### Data Management
- `GET /api/devices/{device_id}/workshop/discoveries/{package_id}` - List saved discoveries
- `POST /api/devices/{device_id}/workshop/save` - Save current discovery to disk
- `GET /api/devices/{device_id}/workshop/load/{package_id}/{discovery_folder}` - Load saved discovery
- `DELETE /api/devices/{device_id}/workshop/discoveries/{package_id}/{discovery_folder}` - Delete discovery

## Module Structure

```
backend/device/workshop_tab/
├── __init__.py
├── routes.py                    # API endpoints
├── session/
│   ├── __init__.py
│   └── workshop_session.py      # Browser tab lock (reuse polling pattern)
├── discovery/
│   ├── __init__.py
│   ├── discoverer.py            # Main orchestrator (two-pass)
│   ├── java_discovery.py        # Java enumeration (raw)
│   ├── native_discovery.py      # Native enumeration (raw)
│   ├── categorizer.py           # Classification engine (configurable)
│   └── verifier.py              # Verification and stats
├── config/
│   ├── __init__.py
│   └── rules_manager.py         # Load/save/update categorization rules
├── storage/
│   ├── __init__.py
│   ├── discovery_store.py       # JSON save/load (separate files)
│   └── file_manager.py          # Directory management
├── logging/
│   ├── __init__.py
│   └── workshop_logger.py       # Workshop-specific logging
└── frida_session/
    ├── __init__.py
    └── session_manager.py       # Frida attach/detach (manual control)
```

## Integration with Existing System

### Reuse from Device Tab
- **Frida server management** - import existing start/stop/restart functions
- **Frida version check** - ensure server is running before discovery
- **ADB manager** - device communication
- **Log streamer** - WebSocket infrastructure for progress

### Reuse from Processes/Packages Tabs
- **Polling session pattern** - adapt for Workshop tab lock
- **Cache architecture patterns** - follow same thread-safety patterns

### New Log Directory
- **Create `logs/workshop/`** directory structure
- **Use existing logger patterns** but write to workshop-specific files
- **Separate concerns** - discovery logs, Frida logs, categorization logs, errors

## Error Handling

### No Automatic Aborts
- **Never auto-abort discovery** - user decides when to cancel
- **Report issues in logs** - let user see and decide
- **Continue on partial failures** - if one class fails, continue with others

### Common Scenarios
- **Process not found**: Log error, notify user, let them retry
- **Frida not running**: Show message to start Frida server from control panel
- **Permission denied**: Log which classes/modules failed, continue with accessible ones
- **Session conflict**: Show lock message with which tab has the lock
- **Slow enumeration**: Log progress, show in UI, but never timeout

### Recovery Strategy
- **Auto-retry Frida attachment** once on connection failure
- **Graceful degradation** - if Java discovery fails, still attempt native
- **User feedback** - clear error messages with actionable steps
- **No automatic cleanup** - user controls session lifecycle

## Performance Considerations

### Discovery Optimization
- **Batch class enumeration** - don't send one class at a time
- **No artificial limits** - enumerate all methods, all classes
- **System library toggle** - skip by default, include if user enables
- **Parallel processing** - enumerate classes and natives concurrently where possible

### Storage Efficiency
- **Separate files** - load only what's needed (Java or Native)
- **No memory caching** - load from disk on demand
- **No limits** on saved discoveries

## Security Considerations

### Data Privacy
- **Never commit workshop_data/** - add to .gitignore
- **No automatic cloud sync** - all data stays local
- **User controls saving** - opt-in, not automatic

### Frida Safety
- **Reuse existing Frida server** - don't expose new attack surface
- **No script execution yet** - only discovery, no injection (Phase 1)
- **Validate PIDs** - ensure process belongs to selected package

## Future Extensibility

### Phase 2 Features (Not in Initial Build)
- Version comparison (diff two discoveries)
- User recategorization (move methods between categories)
- User notes on classes/methods
- Hook script generation from method selection
- Export discoveries for sharing

### Design for Migration
- **format_version in JSON** - enables future schema changes
- **Categorizer as separate module** - easy to improve rules
- **Separate files per discovery** - easy to add new data types
- **Storage abstraction** - swap JSON for SQLite without changing API
- **Dynamic rules** - users can customize without code changes

## Success Criteria

A successful Workshop backend implementation will:
1. Discover ALL Java methods and native functions from the target app (nothing missed)
2. Categorize using user-configurable rules with adjustable confidence levels
3. Verify discovery completeness (included + skipped = total)
4. Prevent tab conflicts with session locking
5. Keep Frida session alive until user explicitly detaches
6. Save discoveries only when user requests (separate files per category)
7. Provide real-time percentage-based progress feedback
8. Log everything to dedicated workshop log files (not mixed with other tabs)
9. Never auto-abort or auto-disconnect - user controls everything
10. Integrate seamlessly with existing Device/Processes/Packages tabs
11. Handle errors gracefully without stopping the entire process
