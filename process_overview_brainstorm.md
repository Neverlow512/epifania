# Process Overview Panel - Brainstorming Document

## The Vision

When you click on a process from the process list, a detailed overview panel slides in above the "Runtime Overview" widget. This panel becomes the central hub for deep-diving into everything happening with that specific process - think of it as an X-ray view of a single process.

---

## Current State Analysis

### What We Already Fetch (ProcessDetailsModal)

When you click "inspect" on a process, we already pull:
- Command line (`/proc/{pid}/cmdline`)
- Status information (`/proc/{pid}/status`)
- Thread list (`/proc/{pid}/task`)
- Open file descriptors (`/proc/{pid}/fd`)
- Memory maps (`/proc/{pid}/maps` - first 50 entries)
- Memory breakdown (RSS, VSZ, Peak, High-water mark)
- Network connections (TCP connections for that PID)

### What We Have System-Wide

- CPU usage (overall + top consumers)
- Memory stats (total, used, free, available, buffers, cached)
- Storage partitions
- Network throughput + recent endpoints
- Process churn tracking

---

## Proposed Panel Layout

### Option A: Horizontal Sliding Panel (Recommended)

When a process is selected, a panel slides down from above the Runtime Overview, pushing it down slightly. This keeps the process list visible for quick switching between processes.

```
+---------------------------+----------------------------+
|  Process List             |  [PROCESS OVERVIEW PANEL]  |
|  (filters + table)        |  (detailed view of PID)    |
|                           |                            |
|                           +----------------------------+
|                           |  Runtime Overview          |
|                           |  (existing widget)         |
+---------------------------+----------------------------+
```

### Option B: Expanded Right Column

The right column expands when a process is selected, with the overview panel at the top and Runtime Overview condensed below.

### Option C: Full-Width Overlay

A full-width panel that overlays the entire view, with a dismiss button. Good for maximum detail but loses context.

**Recommendation**: Option A gives the best balance - you can compare processes quickly while seeing deep details.

---

## What to Show in the Panel

### Tier 1: Critical Information (Always Visible)

1. **Process Identity Header**
   - Process name + PID (large, prominent)
   - User/UID running the process
   - Parent PID (PPID) with clickable link to parent
   - Android state (foreground, background, cached, etc.)
   - Running duration (if available via `/proc/{pid}/stat`)
   - Quick actions: Kill, Trace (if Frida enabled), Copy PID

2. **Resource Gauges (Real-time)**
   - CPU usage (with mini sparkline showing last 30 seconds)
   - Memory RSS (with delta indicator showing growth/shrink)
   - Memory PSS (more accurate, see below)
   - Thread count

3. **Command Line**
   - Full command with arguments
   - Expandable if long

### Tier 2: Detailed Breakdown (Collapsible Sections)

4. **Memory Deep Dive**
   - RSS (Resident Set Size) - what's in RAM
   - PSS (Proportional Set Size) - fair share accounting
   - USS (Unique Set Size) - private memory only
   - VSZ (Virtual Size) - total address space
   - Swap usage
   - Memory maps summary (heap, stack, libraries)
   - Visual breakdown: stacked bar showing private vs shared

5. **Thread Analysis**
   - Thread count
   - Thread list with TID, name, state
   - Identify main thread vs worker threads
   - Thread CPU distribution (which threads are busy)

6. **File Descriptors**
   - Open files count + limit
   - Categorized list: regular files, sockets, pipes, devices
   - Filter/search capability
   - Highlight suspicious patterns (too many open files, etc.)

7. **Network Connections**
   - Active TCP/UDP connections
   - Local and remote addresses
   - Connection states (ESTABLISHED, LISTEN, TIME_WAIT)
   - Data transfer stats if available

8. **Process Relationships**
   - Parent process (clickable)
   - Child processes (clickable list)
   - Process tree visualization (mini tree view)

### Tier 3: Advanced/Optional

9. **Security Context**
   - SELinux context
   - Capabilities
   - Seccomp status
   - UID/GID details

10. **I/O Statistics** (if available via `/proc/{pid}/io`)
    - Read/write bytes
    - Syscall counts

11. **Scheduling Info**
    - Nice value
    - Priority
    - CPU affinity
    - Scheduler policy

12. **Memory Maps Viewer**
    - Full `/proc/{pid}/maps` with filtering
    - Search for specific libraries
    - Identify shared vs private mappings

---

## Data Collection Strategy

### New Backend Endpoints Needed

1. **`GET /api/devices/{device_id}/processes/{pid}/detailed`**
   - Combines all process details in one call
   - Returns PSS/USS (requires `dumpsys meminfo {pid}` or `/proc/{pid}/smaps`)
   - Includes I/O stats, scheduling info

2. **`GET /api/devices/{device_id}/processes/{pid}/metrics/history`**
   - Returns historical metrics for this specific PID
   - CPU, memory over time (last N samples)
   - For sparklines/mini charts

3. **`GET /api/devices/{device_id}/processes/{pid}/tree`**
   - Returns process tree (parent chain + children)

### Getting PSS/USS (Important for Accurate Memory)

PSS is critical for accurate memory analysis. Options:

**Option 1: Parse `/proc/{pid}/smaps`**
```bash
cat /proc/{pid}/smaps | grep -E "^(Pss|Private)" | awk '{sum+=$2} END {print sum}'
```
Slow but accurate. Works without root on most devices.

**Option 2: Use `dumpsys meminfo {pid}`**
```bash
dumpsys meminfo {pid}
```
Returns detailed breakdown including PSS, Private Dirty, Private Clean.
Requires the process to be an Android app (not native).

**Option 3: Use `/proc/{pid}/smaps_rollup`** (Android 9+)
```bash
cat /proc/{pid}/smaps_rollup
```
Pre-aggregated summary - much faster than parsing full smaps.

**Recommendation**: Try smaps_rollup first (fast), fall back to dumpsys meminfo for apps, then full smaps parsing as last resort.

---

## Real-Time Updates

### Polling Strategy

When a process is selected for overview:
1. Fetch initial detailed data (one-time heavy call)
2. Start lightweight polling for metrics only (CPU, memory) at the existing refresh interval
3. Update sparklines in real-time
4. Full refresh on manual request only

### Visual Indicators

- Pulsing indicator when data is updating
- Delta arrows (up/down) for memory changes
- Color coding for resource pressure (green/yellow/red)

---

## UI/UX Considerations

### Panel Behavior

1. **Selection**: Click a row in process table to select
2. **Deselection**: Click selected row again, or click "X" on panel
3. **Quick Switch**: Click different process to switch without closing
4. **Persistence**: Panel stays open during auto-refresh
5. **Collapse**: Allow collapsing to just the header for quick reference

### Keyboard Navigation

- Arrow keys to navigate process list
- Enter to select/deselect
- Escape to close panel

### Mobile/Responsive

- On smaller screens, panel could become full-width overlay
- Collapsible sections become accordion-style

---

## Integration Opportunities

### Frida Integration (Since You Have It)

If Frida server is running on the device:

1. **Live Hooking Button**
   - "Trace this process" button
   - Opens a trace view showing function calls in real-time

2. **Memory Inspection**
   - Dump memory regions
   - Search for strings/patterns

3. **Method Tracing**
   - For Android apps: trace Java methods
   - Show call stack

### Logcat Integration

1. **Process-Filtered Logs**
   - Show logcat output filtered to this PID
   - Real-time streaming

2. **Log Level Breakdown**
   - Count of errors, warnings, info by this process

### Performance Profiling

1. **CPU Profiling**
   - If device supports `simpleperf`, offer profiling
   - Show flame graph or call tree

2. **Memory Leak Detection**
   - Track RSS growth over time
   - Alert if consistent growth pattern detected

---

## Implementation Phases

### Phase 1: Core Panel (MVP)

- Panel UI with header (name, PID, state)
- Resource gauges (CPU, RSS, thread count)
- Command line display
- Basic memory breakdown (RSS, VSZ, Peak)
- Open files list
- Network connections
- Parent/child process links

### Phase 2: Enhanced Memory

- Add PSS/USS collection
- Memory maps viewer
- Visual breakdown (stacked bar)
- Memory history sparkline

### Phase 3: Process Relationships

- Process tree visualization
- Click-to-navigate between related processes
- Thread analysis with per-thread CPU

### Phase 4: Advanced Features

- I/O statistics
- Security context
- Frida integration hooks
- Logcat filtering

---

## Technical Considerations

### Performance

- Fetching smaps/smaps_rollup can be slow for large processes
- Consider caching with short TTL
- Lazy load sections (don't fetch everything upfront)

### Permissions

- Some data requires root (full smaps, I/O stats)
- Gracefully degrade when data unavailable
- Show "requires root" indicators

### Process Death

- Handle case where process dies while panel is open
- Show "Process no longer exists" state
- Offer to close panel or show last known state

---

## Open Questions

1. **Should we track historical data per-process?**
   - Pro: Can show trends, detect leaks
   - Con: Memory overhead, complexity

2. **How deep should Frida integration go?**
   - Basic tracing vs full instrumentation
   - Security implications

3. **Should we support multiple process selection?**
   - Compare two processes side-by-side
   - Useful for before/after analysis

4. **Export functionality?**
   - Export process details to JSON/CSV
   - Useful for bug reports, analysis

---

## Inspiration / References

- Android Studio Profiler (memory, CPU, network views)
- htop (process details, tree view)
- Activity Monitor (macOS) - process inspection
- Process Explorer (Windows) - detailed process view
- Instruments (macOS) - performance analysis

---

## Next Steps

1. Finalize panel layout choice (A, B, or C)
2. Define MVP scope (Phase 1 features)
3. Design backend endpoint for detailed process data
4. Create frontend component structure
5. Implement PSS/USS collection
6. Build UI incrementally

---

## Your Input Needed

- Which layout option appeals most to you?
- Any features you'd prioritize or deprioritize?
- Interest level in Frida integration for this panel?
- Any specific analysis scenarios you want to support?

