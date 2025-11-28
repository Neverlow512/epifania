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

## Summary

- **Feature packages own their complete vertical slice**
- **Shared code lives at top level, not scattered in features**
- **Each module has one clear responsibility**
- **Business logic is independent of external interface (HTTP/UI/CLI)**
- **Names are descriptive and follow language conventions**
- **Three-layer pattern: Entry Point → Business Logic → Infrastructure**

