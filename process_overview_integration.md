# Process Overview Panel Integration

**Date:** 2025-12-03  
**Feature:** Process Overview inline panel (replaces modal-based process details)  
**Backend Status:** Ready (see `assessment.md`)

---

## Overview

This document explains how to integrate the Process Overview backend into the frontend. The goal is to replace the current modal-based process details with an inline expandable panel that appears when clicking a process row.

---

## Design Requirements

### Behavior
1. **Click to Expand**: Clicking a process row in `ProcessTable` expands an inline panel below that row
2. **Single Selection**: Only one process can be expanded at a time
3. **Scroll Together**: The overview panel scrolls with the process list (not sticky like Runtime Overview)
4. **Close on Click**: Clicking the same row again or a close button collapses the panel

### UI Changes
1. **Remove Actions Column**: Remove the "Actions" column from `ProcessTable` (inspect button, kill button)
2. **Row Click Handler**: Make entire row clickable to toggle the overview panel
3. **Kill Action**: Move kill functionality to a button inside the overview panel (or a context menu - TBD)
4. **Permission Indicators**: Show unavailable data sections with a lock icon and "Requires root" message

### Layout Position
- The panel appears **below the clicked row** within the process table
- It should have the same card styling as the rest of the UI
- When expanded, the table row should have a highlighted border/background

---

## Backend API

### Endpoint
```
GET /api/devices/{device_id}/processes/{pid}/overview
```

### Response Structure
```json
{
  "pid": 1234,
  "identity": {
    "pid": 1234,
    "name": "com.example.app",
    "state": "sleeping",
    "state_char": "S",
    "ppid": 1,
    "uid": 10123,
    "gid": 10123,
    "thread_count": 15,
    "nice": 0,
    "priority": 120,
    "utime_ticks": 12345,
    "stime_ticks": 6789,
    "cpu_time_ticks": 19134,
    "running_seconds": 3600,
    "cmdline": "com.example.app --flag"
  },
  "memory": {
    "rss_kb": 45678,
    "pss_kb": null,
    "uss_kb": null,
    "swap_kb": 0,
    "smaps_available": false,
    "dumpsys_available": true,
    "dumpsys": {
      "total_pss_kb": 42000,
      "java_heap_kb": 12000,
      "native_heap_kb": 8000,
      "code_kb": 5000,
      "stack_kb": 500,
      "graphics_kb": 10000,
      "private_other_kb": 2000,
      "system_kb": 4500
    }
  },
  "threads": {
    "count": 15,
    "threads": [
      { "tid": 1234, "name": "main", "state": "S", "cpu_time_ticks": 5000, "is_main": true },
      { "tid": 1235, "name": "worker-1", "state": "S", "cpu_time_ticks": 1000, "is_main": false }
    ]
  },
  "files": {
    "count": 42,
    "max_fds": 1048576,
    "soft_limit": 1024,
    "hard_limit": 1048576,
    "categories": { "socket": 10, "pipe": 5, "file": 20, "device": 7 },
    "fds": [ { "fd": 0, "target": "/dev/null", "type": "device" } ],
    "truncated": false,
    "full_access": true
  },
  "network": {
    "tcp": {
      "connections": [
        { "local_addr": "10.0.0.1", "local_port": 54321, "remote_addr": "142.250.80.46", "remote_port": 443, "state": "ESTABLISHED" }
      ],
      "count": 5,
      "truncated": false
    },
    "udp": { "connections": [], "count": 0, "truncated": false },
    "unix": { "sockets": [], "count": 0, "truncated": false }
  },
  "io": {
    "read_bytes": 1234567,
    "write_bytes": 987654,
    "read_chars": 2345678,
    "write_chars": 1234567,
    "syscr": 5000,
    "syscw": 3000,
    "cancelled_write_bytes": 0
  },
  "relationships": {
    "parent": { "pid": 1, "name": "init" },
    "children": [
      { "pid": 5678, "name": "child-process" }
    ],
    "children_count": 1,
    "tree_depth": 2
  },
  "permissions": {
    "has_root": true,
    "io_stats_available": false,
    "detailed_memory_available": false,
    "dumpsys_memory_available": true,
    "full_fd_access": true
  }
}
```

---

## Frontend Architecture

Follow `ARCHITECTURE.md` and `DEVELOPMENT_RULES.md`:
- Feature-based structure with clear separation of concerns
- Single-responsibility modules
- No cross-feature imports
- Clean code with minimal comments

### File Structure
```
frontend/src/views/device/processes/
├── ProcessesTab.vue                    # Main view (modify)
├── components/
│   ├── ProcessTable.vue                # Modify: remove Actions, add row click
│   ├── ProcessOverviewPanel.vue        # NEW: inline expandable panel
│   ├── ProcessOverviewIdentity.vue     # NEW: identity section
│   ├── ProcessOverviewMemory.vue       # NEW: memory section
│   ├── ProcessOverviewThreads.vue      # NEW: threads section
│   ├── ProcessOverviewFiles.vue        # NEW: files section
│   ├── ProcessOverviewNetwork.vue      # NEW: network section
│   ├── ProcessOverviewIO.vue           # NEW: I/O section
│   ├── ProcessOverviewRelationships.vue# NEW: relationships section
│   ├── ProcessControlBar.vue           # Keep as-is
│   ├── ProcessStatsBar.vue             # Keep as-is
│   ├── ProcessDetailsModal.vue         # DELETE after migration
│   └── ProcessKillModal.vue            # Keep (use from panel)
└── composables/
    ├── useProcesses.js                 # Keep as-is
    ├── useProcessFilters.js            # Keep as-is
    ├── useProcessActions.js            # Modify: add fetchProcessOverview
    ├── useProcessOverview.js           # NEW: overview state management
    └── useSystemMetrics.js             # Keep as-is
```

---

## Implementation Steps

### Phase 1: Create Composable

**File:** `composables/useProcessOverview.js`

Responsibilities:
- Fetch overview data from `/api/devices/{device_id}/processes/{pid}/overview`
- Track expanded PID state
- Handle loading/error states
- Provide toggle function

```javascript
// Pseudo-structure
export function useProcessOverview(deviceSerial) {
  const expandedPid = ref(null)
  const overviewData = ref(null)
  const loading = ref(false)
  const error = ref(null)

  async function toggleOverview(pid) { ... }
  async function fetchOverview(pid) { ... }
  function closeOverview() { ... }

  return { expandedPid, overviewData, loading, error, toggleOverview, closeOverview }
}
```

### Phase 2: Create Panel Components

**Main Panel:** `ProcessOverviewPanel.vue`
- Container component that orchestrates sub-sections
- Receives full overview data as prop
- Renders sections conditionally based on `permissions` object
- Shows loading spinner while fetching
- Shows error state if fetch fails

**Sub-sections:** Each section is a separate component for maintainability:

| Component | Data Source | Has Detail Modal |
|-----------|-------------|------------------|
| `ProcessOverviewIdentity.vue` | `overview.identity` | No (always inline) |
| `ProcessOverviewMemory.vue` | `overview.memory` | No (heap breakdown inline) |
| `ProcessOverviewThreads.vue` | `overview.threads` | Yes - full thread table |
| `ProcessOverviewFiles.vue` | `overview.files` | Yes - full FD table |
| `ProcessOverviewNetwork.vue` | `overview.network` | Yes - connections per protocol |
| `ProcessOverviewIO.vue` | `overview.io` | No (simple stats) |
| `ProcessOverviewRelationships.vue` | `overview.relationships` | Yes - children list |

### Phase 3: Modify ProcessTable

**Changes:**
1. Remove `<th>Actions</th>` header
2. Remove actions column `<td>` with inspect/kill buttons
3. Add `@click="$emit('toggle-overview', process)"` to each `<tr>`
4. Add cursor pointer styling to rows
5. Add expanded state indicator (chevron icon or border)
6. After each `<tr>`, render `<ProcessOverviewPanel>` if that row's PID matches `expandedPid`

**Row structure:**
```html
<template v-for="process in paginatedProcesses">
  <tr @click="$emit('toggle-overview', process)" class="cursor-pointer">
    <!-- existing columns minus Actions -->
  </tr>
  <tr v-if="expandedPid === process.pid">
    <td colspan="5">
      <ProcessOverviewPanel :data="overviewData" :loading="loading" />
    </td>
  </tr>
</template>
```

### Phase 4: Update ProcessesTab

**Changes:**
1. Import and use `useProcessOverview` composable
2. Pass `expandedPid`, `overviewData`, `loading` to `ProcessTable`
3. Handle `toggle-overview` event from `ProcessTable`
4. Remove `ProcessDetailsModal` import and usage
5. Keep `ProcessKillModal` for kill confirmation

### Phase 5: Cleanup

1. Delete `ProcessDetailsModal.vue` (replaced by inline panel)
2. Remove related code from `useProcessActions.js`:
   - `showDetailsModal`
   - `processDetails`
   - `processMemoryDetails`
   - `processNetworkDetails`
   - `showProcessDetails`
   - `closeDetailsModal`

---

## UI Design Guidelines

### Panel Styling
- Same card style: `bg-neutral-900/60 backdrop-blur-sm border border-primary/20`
- Subtle animation on expand/collapse (max-height transition or Vue transition)
- Section headers with icons matching `ProcessStatsBar` style
- Compact data display using grid layouts

### Section Layout

**Hybrid approach:** Summary view by default, expandable/modal for full details.

```
┌─────────────────────────────────────────────────────────────────┐
│ [Identity] com.example.app                                      │
│ PID: 1234 | PPID: 1 | UID: 10123 | State: sleeping             │
│ Running: 1h 23m | Threads: 15 | Priority: 120                  │
│ cmdline: com.example.app --flag                                │
├─────────────────────────────────────────────────────────────────┤
│ [Memory]                    [Threads] 15 threads    [View all] │
│ RSS: 44.6 MB               main (5000 ticks)                   │
│ PSS: 41.0 MB (dumpsys)     worker-1 (1000 ticks)               │
│ Heap: Java 12MB Native 8MB worker-2 (800 ticks)                │
├─────────────────────────────────────────────────────────────────┤
│ [Files] 42 FDs   [View all] [Network]              [View all]  │
│ socket: 10, pipe: 5        TCP: 5 (3 ESTABLISHED)              │
│ file: 20, device: 7        UDP: 2                              │
│ Limit: 1024/1048576        Unix: 8                             │
├─────────────────────────────────────────────────────────────────┤
│ [I/O Stats]                [Relationships]         [View all]  │
│ Read: 1.2 MB               Parent: init (PID 1)                │
│ Write: 987 KB              Children: 3                         │
│ Syscalls: R 5000 W 3000    Depth: 2                            │
├─────────────────────────────────────────────────────────────────┤
│                                              [Kill Process]    │
└─────────────────────────────────────────────────────────────────┘
```

### Detail Views

Each section with lists gets a "View all" button. Opens a modal with full data:

| Section | Summary Shows | Modal Shows |
|---------|--------------|-------------|
| Threads | Top 3 by CPU time | Full thread table (TID, name, state, CPU time) |
| Files | Category counts | Full FD table (fd, target, type) |
| Network | Protocol counts | Connection tables per protocol (local, remote, state) |
| Relationships | Parent + child count | Full children list, clickable to inspect |

Modal reuses existing styling pattern (see `ProcessStatsBar` CPU/Memory detail modals).

### Unavailable Data Display
When a section has no data due to permissions:
```html
<div class="flex items-center gap-2 text-slate-500 text-xs">
  <LockIcon class="w-4 h-4" />
  <span>Requires root access</span>
</div>
```

Or for device limitations:
```html
<div class="flex items-center gap-2 text-slate-500 text-xs">
  <InfoIcon class="w-4 h-4" />
  <span>Not available on this device</span>
</div>
```

---

## Data Handling Notes

### From assessment.md

1. **Handle null values**: I/O stats and smaps data may be null
2. **Check permissions object**: Use it to conditionally render sections
3. **Respect truncation flags**: Show "Showing first 100 of X" when truncated
4. **Process name display**: Prefer `cmdline` over `name` for full names
5. **Memory fallback**: Use `dumpsys.total_pss_kb` when `pss_kb` is null

### Formatting Helpers
Create or reuse formatting functions:
- `formatBytes(bytes)` - bytes to KB/MB/GB
- `formatDuration(seconds)` - seconds to "1h 23m 45s"
- `formatTicks(ticks)` - CPU ticks to readable format

---

## Event Flow

```
User clicks process row
    ↓
ProcessTable emits 'toggle-overview' with process object
    ↓
ProcessesTab.vue handles event
    ↓
useProcessOverview.toggleOverview(pid) called
    ↓
If same PID: close panel (expandedPid = null)
If different PID: fetch overview data, set expandedPid
    ↓
ProcessTable receives new expandedPid
    ↓
Renders ProcessOverviewPanel below matching row
```

---

## Testing Checklist

- [ ] Panel expands when clicking a process row
- [ ] Panel collapses when clicking the same row again
- [ ] Only one panel can be open at a time
- [ ] Loading spinner shows while fetching
- [ ] Error state displays if fetch fails
- [ ] All sections render correctly with full data
- [ ] Unavailable sections show appropriate message
- [ ] Truncation indicators show when lists are truncated
- [ ] Kill button opens kill confirmation modal
- [ ] Panel scrolls with the table (not sticky)
- [ ] Panel styling matches existing theme
- [ ] Works on non-rooted devices (graceful degradation)

---

## Migration Notes

### Files to Modify
- `ProcessesTab.vue` - Add composable, remove modal
- `ProcessTable.vue` - Remove Actions, add click handler, render panel
- `useProcessActions.js` - Remove modal-related code

### Files to Create
- `useProcessOverview.js`
- `ProcessOverviewPanel.vue`
- `ProcessOverviewIdentity.vue`
- `ProcessOverviewMemory.vue`
- `ProcessOverviewThreads.vue`
- `ProcessOverviewFiles.vue`
- `ProcessOverviewNetwork.vue`
- `ProcessOverviewIO.vue`
- `ProcessOverviewRelationships.vue`
- `ProcessOverviewDetailModal.vue` (reusable modal for full lists)

### Files to Delete (after migration complete)
- `ProcessDetailsModal.vue`

---

## References

- Backend assessment: `assessment.md`
- Architecture guidelines: `ARCHITECTURE.md`
- Development rules: `DEVELOPMENT_RULES.md`
- Backend routes: `backend/device/processes_tab/routes.py`
- Backend inspector: `backend/device/processes_tab/overview/process_inspector.py`

