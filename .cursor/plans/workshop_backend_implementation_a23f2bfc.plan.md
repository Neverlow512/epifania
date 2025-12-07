---
name: Workshop Backend Implementation
overview: Implement the complete Workshop tab backend for Frida-based method discovery and categorization, following existing architecture patterns from packages_tab and processes_tab.
todos:
  - id: setup
    content: Create workshop_tab directory structure and __init__.py files
    status: pending
  - id: log-paths
    content: Add workshop log paths to core/log_paths.py and update .gitignore
    status: in_progress
  - id: logging
    content: Implement workshop_logger.py for dedicated workshop logging
    status: pending
  - id: storage-paths
    content: Implement storage/paths.py for workshop data directories
    status: pending
  - id: storage-store
    content: Implement storage/discovery_store.py for JSON save/load
    status: pending
  - id: config
    content: Implement config/rules_manager.py with default categorization rules
    status: pending
  - id: session
    content: Implement session/workshop_session.py for browser tab lock
    status: pending
  - id: frida-session
    content: Implement frida_session/session_manager.py for attach/detach
    status: pending
  - id: filter
    content: Implement discovery/filter.py for inclusion/exclusion logic
    status: pending
  - id: categorizer
    content: Implement discovery/categorizer.py for classification
    status: pending
  - id: java-discovery
    content: Implement discovery/java_discovery.py for Java enumeration
    status: pending
  - id: native-discovery
    content: Implement discovery/native_discovery.py for native enumeration
    status: pending
  - id: discoverer
    content: Implement discovery/discoverer.py orchestrator
    status: pending
  - id: routes
    content: Implement routes.py with all API endpoints
    status: pending
  - id: integration
    content: Register workshop router in main.py
    status: pending
---

# Workshop Tab Backend Implementation

## Overview

Build the complete Workshop backend following the design in [workshop_backend.md](workshop_backend.md), reusing patterns from existing tabs (packages, processes) and respecting [ARCHITECTURE.md](ARCHITECTURE.md) and [DEVELOPMENT_RULES.md](DEVELOPMENT_RULES.md).

## Module Structure

```
backend/device/workshop_tab/
├── __init__.py
├── routes.py                      # API endpoints
├── session/
│   ├── __init__.py
│   └── workshop_session.py        # Browser tab lock
├── discovery/
│   ├── __init__.py
│   ├── discoverer.py              # Main orchestrator (two-pass)
│   ├── java_discovery.py          # Java class/method enumeration
│   ├── native_discovery.py        # Native module/export enumeration
│   ├── categorizer.py             # Classification engine
│   └── filter.py                  # Inclusion/exclusion logic
├── config/
│   ├── __init__.py
│   └── rules_manager.py           # Load/save categorization rules
├── storage/
│   ├── __init__.py
│   ├── discovery_store.py         # JSON save/load
│   └── paths.py                   # Workshop data paths
├── logging/
│   ├── __init__.py
│   └── workshop_logger.py         # Workshop-specific logging
└── frida_session/
    ├── __init__.py
    └── session_manager.py         # Frida attach/detach
```

## Implementation Steps

### 1. Setup Infrastructure

Create directory structure and base files:

- [backend/device/workshop_tab/](backend/device/workshop_tab/) module structure
- Add workshop log paths to [backend/core/log_paths.py](backend/core/log_paths.py)
- Add `backend/workshop_data/` to [.gitignore](.gitignore)

### 2. Workshop Logging

Create dedicated logging for workshop in `logging/workshop_logger.py`:

- Per-discovery log files in `logs/workshop/discovery/`
- Frida session logs in `logs/workshop/frida/`
- Categorization logs in `logs/workshop/categorization/`
- Error logs in `logs/workshop/errors/`

### 3. Storage and Paths

Implement storage layer in `storage/`:

- `paths.py`: Define workshop data paths (config, discoveries)
- `discovery_store.py`: Save/load discovery JSON files (metadata, java_classes, native_modules)

### 4. Configuration Rules

Implement rules manager in `config/rules_manager.py`:

- Load default categorization rules
- Save user-modified rules
- API for frontend to read/update rules

### 5. Browser Tab Session Lock

Implement session lock in `session/workshop_session.py`:

- Reuse pattern from [backend/device/packages_tab/management/cache.py](backend/device/packages_tab/management/cache.py)
- One tab per device for Workshop
- 30-second timeout with heartbeat

### 6. Frida Session Manager

Implement Frida attach/detach in `frida_session/session_manager.py`:

- Attach to process (auto on discovery start)
- Detach from process (manual only)
- Session status tracking
- Reuse existing Frida server (no new server start)

### 7. Inclusion/Exclusion Filter

Implement filtering logic in `discovery/filter.py`:

- App identification (package prefix, APK path, lib path)
- Inclusion rules (always include app code)
- Exclusion rules (system libs only when toggle off)
- Verification (included + skipped = total)

### 8. Categorizer

Implement classification in `discovery/categorizer.py`:

- Load rules from config
- Categorize by class name patterns
- Confidence levels (high, medium, low)
- Obfuscation detection
- Return category with reason

### 9. Java Discovery

Implement Java enumeration in `discovery/java_discovery.py`:

- Enumerate all loaded classes via Frida
- Get methods for each class
- Extract method signatures, parameters, return types
- Mark native methods

### 10. Native Discovery

Implement native enumeration in `discovery/native_discovery.py`:

- Enumerate all modules via Frida
- Get exports for each module
- Extract function names, addresses, types

### 11. Discovery Orchestrator

Implement main orchestrator in `discovery/discoverer.py`:

- Two-pass process: enumerate first, categorize second
- Progress tracking (percentage-based)
- Verification step
- Build final result structure

### 12. API Routes

Implement endpoints in `routes.py`:

- Session: acquire, heartbeat, release
- Frida: attach, detach, status
- Config: get rules, update rules
- Discovery: start, cancel, status
- Storage: list, save, load, delete discoveries
- WebSocket: real-time progress streaming

### 13. Integration

Register workshop router in [backend/main.py](backend/main.py):

- Import workshop router
- Add to FastAPI app with prefix

## Key Patterns to Follow

**From packages_tab:**

- Session management pattern ([cache.py](backend/device/packages_tab/management/cache.py))
- Route structure ([routes.py](backend/device/packages_tab/routes.py))
- Error handling pattern

**From existing Frida code:**

- Frida device/session handling ([main.py](backend/main.py) lines 464-491)
- Server manager pattern ([server.py](backend/frida_mgmt/manage/server.py))

## Files to Modify

- [backend/core/log_paths.py](backend/core/log_paths.py) - Add workshop log paths
- [backend/main.py](backend/main.py) - Register workshop router
- [.gitignore](.gitignore) - Add workshop_data directory

## Code Standards

- No emojis
- No unnecessary comments
- Clean, self-documenting code
- Professional tone
- Input validation on all endpoints
- Sanitize inputs before Frida/subprocess calls