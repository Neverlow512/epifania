# Architecture Principles

## Core Philosophy

**Separation of Concerns**: Each module should have a single, well-defined responsibility. Features should be isolated, composable, and independently testable.

**Terminology**:
- **Module**: A single file with related functions/classes (e.g., `process_monitor.py`, `useProcesses.js`)
- **Package/Namespace**: A directory containing multiple related modules (e.g., `processes_tab/`, `monitoring/`)

## Directory Organization

### Feature-Based Structure

Organize code by **feature/domain**, not by technical role. Each feature owns its complete vertical slice.

**Backend Example:**
```
backend/
├── core/              # Shared infrastructure (ADB, logging, diagnostics)
├── device/            # Device-related features
│   ├── processes_tab/ # Process monitoring feature
│   │   ├── routes.py          # API endpoints
│   │   └── monitoring/        # Business logic
│   └── packages_tab/  # Package management feature (future)
├── frida_mgmt/        # Frida management features
└── monitoring/        # System health features
```

**Frontend Example:**
```
frontend/src/
├── components/        # Shared UI components (TabNavigation, ToastNotification)
├── composables/       # Shared state logic (useApiConnection, useToast)
├── views/
│   └── device/        # Device-related features
│       ├── overview/  # Device tab feature
│       │   ├── DeviceTab.vue
│       │   ├── components/    # Feature-specific components
│       │   └── composables/   # Feature-specific logic
│       └── processes/ # Process monitoring feature
│           ├── ProcessesTab.vue
│           ├── components/    # ProcessTable, ProcessDetailsModal, etc.
│           └── composables/   # useProcesses, useProcessFilters, etc.
```

### Rules

1. **Feature Isolation**: Each feature package contains everything needed for that feature
2. **Shared at Top**: Only truly shared code lives in top-level packages (core/, components/, composables/, utils/)
3. **No Cross-Feature Imports**: Features should not import from sibling features
4. **Clear Boundaries**: Entry points, business logic, and presentation are clearly separated within each feature

## Language-Agnostic Structure

### Three-Layer Pattern

**Layer 1 - Entry Point**: Handles external interface (HTTP, CLI, UI events)
**Layer 2 - Business Logic**: Core functionality, algorithms, data transformation
**Layer 3 - Shared Infrastructure**: Utilities used by multiple features

### Separation by Language/Framework

**Backend (any language)**:
- Entry Point: Route handlers, controllers, command handlers
- Business Logic: Service classes, domain logic in subdirectories
- Infrastructure: Database clients, external API wrappers, logging

**Frontend (any framework)**:
- Entry Point: Views, pages, top-level components
- Business Logic: State management, data transformation (stores, composables, hooks)
- Infrastructure: API clients, shared utilities, base components

## Backend Structure (Language-Agnostic)

### Layers

1. **Entry Point** (routes, controllers, handlers): External interface, request/response handling, validation
2. **Business Logic** (services, domain logic): Core functionality, algorithms, data transformation
3. **Shared Infrastructure** (core, shared): Utilities used by multiple features

### Responsibilities

- **Entry Point**: Parse input, call business logic, format output. No business logic here.
- **Business Logic**: Feature implementation. Independent of external interface.
- **Infrastructure**: Shared utilities across features (clients, logging, config)

## Frontend Structure (Language-Agnostic)

### Layers

1. **View/Page**: Layout, composition, minimal logic
2. **Feature Components**: UI elements specific to this feature
3. **State Management**: Reactive state and business logic for this feature (stores, composables, hooks, services)
4. **Shared**: Components and utilities used by multiple features

### State Management Responsibilities (applies to stores, composables, hooks)

- **Data Fetching**: API calls, polling, caching
- **Transform/Filter**: Search, sort, pagination, computed values
- **Actions**: User actions with side effects (save, delete, etc.)

**Single Responsibility**: Each state module handles one concern. Don't mix data fetching with filtering.

## File/Module Naming

- Follow language conventions (snake_case for Python, camelCase for JS, PascalCase for classes/components)
- Use descriptive names: `ProcessDetailsModal`, not `Modal`; `process_monitor.py`, not `monitor.py`
- Prefix interfaces/abstract classes where appropriate (language-specific)

## When to Create a New Feature Package

Create a new feature package when:
- Feature has 3+ modules/files
- Feature has distinct domain logic
- Feature will evolve independently

Keep simple features flat until complexity justifies the structure.

## Anti-Patterns to Avoid

❌ **God Modules**: One file doing everything  
❌ **Cross-Feature Coupling**: Feature A importing from Feature B  
❌ **Mixing Layers**: Entry point logic mixed with business logic  
❌ **Generic Names**: `utils`, `helpers`, `common` without context  
❌ **Deep Nesting**: More than 3 levels deep becomes hard to navigate

## Example: Adding a New Feature

**Task**: Add "Packages" tab

**Backend**:
```
backend/device/packages_tab/
├── routes.py              # GET /api/devices/{id}/packages, etc.
└── management/
    └── package_manager.py # Package enumeration, lifecycle
```

**Frontend**:
```
frontend/src/views/device/packages/
├── PackagesTab.vue                 # Main view
├── components/
│   ├── PackageGrid.vue             # Grid/list display
│   └── PackageDetailsModal.vue     # Package info modal
└── composables/
    ├── usePackages.js              # Fetch packages from API
    └── usePackageActions.js        # Launch, stop, uninstall
```

**Integration**:
- Backend: Import routes in `main.py`
- Frontend: Import `PackagesTab.vue` in `DeviceDetails.vue`, add to component map

## Polling and Caching Pattern

For any feature that polls external resources (ADB, APIs, hardware):

### Backend

**1. Polling Session** (`cache.py` in feature package):
- **One session per device** - tracks which browser tab controls polling for that device
- Tracks primary/secondary clients (client_id = browser tab identifier)
- Session timeout: 15 seconds (3x heartbeat interval)
- Returns active interval to all clients

**2. Cache Layer** (`cache.py` in feature package):
- TTL = polling interval (dynamic, from session)
- Thread-safe with per-key locking
- Returns cached data if fresh, otherwise computes

**3. Entry Point** (routes):
- Register/unregister session endpoints
- Heartbeat endpoint for secondary tabs
- Data endpoints use cache for actual requests

**Pattern**:
```python
# In feature/cache.py
polling_session = PollingSession(session_timeout=15.0)
feature_cache = FeatureCache(polling_session=polling_session)

# In feature/routes.py
@router.post("/{device_id}/session/register")
async def register_session(device_id: str, request: SessionRequest):
    is_primary, message, active_interval = polling_session.register(
        device_id, request.client_id, request.interval_ms
    )
    return {
        "is_primary": is_primary,
        "message": message,
        "active_interval_ms": active_interval
    }

@router.get("/{device_id}/data")
async def get_data(device_id: str):
    def compute():
        return expensive_operation(device_id)
    
    return feature_cache.get_or_compute(
        key=f"data:{device_id}",
        compute_fn=compute
    )
```

### Frontend

**1. Session Management** (`usePollingSession.js` or similar):
- Generate unique client_id per composable instance (represents one browser tab)
- Register on mount, unregister on unmount
- Heartbeat every 5 seconds (for secondary tabs)
- Handle promotion to primary when primary tab closes

**2. Data Fetching** (`useFeatureData.js` or similar):
- Primary tab: polls at interval, makes real requests
- Secondary tabs: heartbeat only, no data requests
- Watch isPrimary to start/stop polling
- Watch activeIntervalMs to sync interval

**Pattern**:
```javascript
export function useFeatureData(deviceSerial) {
  const { isPrimary, activeIntervalMs, sessionRegistered, heartbeat } 
    = usePollingSession(deviceSerial)
  
  const autoRefresh = ref(true)
  const refreshInterval = ref(5000)
  
  // Sync interval from session
  watch(activeIntervalMs, (newInterval) => {
    if (newInterval !== refreshInterval.value) {
      refreshInterval.value = newInterval
      if (autoRefresh.value) startAutoRefresh()
    }
  })
  
  // Only primary polls
  watch(isPrimary, (isPrim) => {
    if (isPrim && autoRefresh.value) {
      startAutoRefresh()
    } else {
      stopAutoRefresh()
    }
  })
  
  function startAutoRefresh() {
    stopAutoRefresh()
    if (!isPrimary.value) {
      startHeartbeatTimer()  // Secondary: heartbeat only
      return
    }
    refreshTimer = setInterval(fetchData, refreshInterval.value)
  }
}
```

### Rules

1. **One session per device** - All tabs viewing same device share one session
2. **First tab is primary** - Controls the polling interval, makes actual requests
3. **Secondary tabs read only** - Send heartbeats, wait for cache, can be promoted
4. **Cache TTL = polling interval** - Serves concurrent requests in same tick
5. **15s session timeout** - Allows 3 missed heartbeats before expiry
6. **5s heartbeat interval** - Fast promotion detection for secondary tabs

### Reference Implementation

See `backend/device/processes_tab/monitoring/cache.py` and `frontend/src/views/device/processes/composables/usePollingSession.js`

---

## Summary

- **Feature packages own their complete vertical slice**
- **Shared code lives at top level, not scattered in features**
- **Each module has one clear responsibility**
- **Business logic is independent of external interface (HTTP/UI/CLI)**
- **Names are descriptive and follow language conventions**
- **Three-layer pattern: Entry Point → Business Logic → Infrastructure**
- **Polling features use session management + caching to prevent duplicate calls**

