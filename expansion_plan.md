# Epifania Expansion Plan

## Overview

This document outlines the strategic expansion of Epifania from a Frida server management tool into a comprehensive dynamic analysis platform. The focus is on building two foundational tabs (Processes and Applications) that will serve as the reconnaissance layer before implementing the Workshop for active analysis.

## Current State

**What We Have:**
- Solid device management and Frida server lifecycle control
- Real-time log streaming infrastructure
- Health monitoring and diagnostics
- Clean, compact UI optimized for information density

**What We're Building:**
- Runtime process monitoring (Processes tab)
- Application inventory and management (Applications tab)
- Tab navigation structure for future expansion

**What Comes Later:**
- Workshop (active analysis, script injection, plugins)
- Files browser
- Additional specialized tools

---

## Navigation Structure

### Tab Layout

The DeviceDetails page has been restructured with a horizontal tab navigation:

```
┌─────────────────────────────────────────────────────────────┐
│  ← Back to Dashboard                                         │
├─────────────────────────────────────────────────────────────┤
│  Google Pixel 3   │  Emulator  │  online  │  SDK 28  │ Root ✓│ ← Compact header
├─────────────────────────────────────────────────────────────┤
│ [Device] [Processes] [Packages] [Files] [Workshop]          │ ← Tab bar
├─────────────────────────────────────────────────────────────┤
│                                                              │
│              Active Tab Content                              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Tab Definitions:**
- **Device** - Device management (Frida server controls, diagnostics, discovery, permissions, logs)
- **Processes** - Runtime process monitoring and analysis (Coming Soon)
- **Packages** - Installed package catalog and management (Coming Soon)
- **Files** - File system browser (Coming Soon)
- **Workshop** - Active analysis workspace (Coming Soon)

**Device Header Implementation:**
The header displays essential device information in a compact single line: device name, device type badge (Emulator/Physical), connection status badge, SDK version, and root status. The detailed device specifications and all Frida management controls remain in the Device tab.

**Tab Structure:**
The tab navigation uses a reusable `TabNavigation` component that accepts tab definitions and emits change events. URL query parameters (`?tab=processes`) enable deep linking to specific tabs. All placeholder tabs display a centered informational message with an icon and description of the planned functionality.

---

## Tab 1: Processes

### Purpose

Monitor runtime behavior, track resource consumption, detect spawned services, and identify analysis targets by observing what's actually executing on the device at any given moment.

### Core Concept

This is a **live dashboard** - data updates continuously. Think of it as the device's "Task Manager" but enhanced for security analysis. You're watching the device breathe, seeing processes spawn and die, observing resource spikes, tracking suspicious behavior.

### Visual Layout

**Top Section: Stats Overview**
- Total processes count (with breakdown: user vs system)
- Live CPU usage gauge (percentage with mini-graph)
- Live Memory usage gauge (used/total with percentage)
- Active Frida attachments indicator (how many processes currently have scripts running)

**Control Bar:**
- Search input (filter by process name, package, PID)
- Filter dropdown: All | User Processes | System Processes | Frida-Attached | High CPU | High Memory
- Sort dropdown: Name | PID | CPU Usage | Memory Usage | User
- Auto-refresh toggle: ON (2s) / OFF (manual refresh button)
- Refresh rate selector: 1s / 2s / 5s / 10s

**Main Content: Process Table**

Table columns:
- PID (numeric, sortable)
- Process Name (truncated with tooltip for full path)
- Package Name (if available, linked to Applications tab)
- User (system, root, u0_aXX)
- CPU % (with mini spark-line showing trend)
- Memory MB (with mini spark-line showing trend)
- Status Badge (Running, Sleeping, Zombie, Traced)
- Actions (icon buttons: Send to Workshop, Kill, Inspect)

**Table Behaviors:**
- Rows highlight on hover
- New processes flash briefly in green when spawned
- Killed processes fade out with red tint
- Processes with Frida attached show purple accent border
- Click row to expand for detailed view

**Expanded Row Details:**
When you click a process row, it expands to show:
- Full command line with arguments
- Parent process (clickable to jump to parent)
- Child processes count (expandable list)
- Threads count
- Open files count (clickable to view list)
- Network connections count (clickable to view list)
- Start time and uptime
- Detailed graphs: CPU usage over last 60s, Memory usage over last 60s

**Bottom Section: Activity Feed**
- Scrolling log of recent events (last 50 events)
- Event types: Process Started, Process Killed, CPU Spike Detected, Memory Warning, Frida Attached
- Each event shows timestamp, PID, process name, and brief description
- Events color-coded by severity (info: blue, warning: yellow, critical: red)

### Functionality Deep Dive

#### Real-Time Updates

**Backend Requirements:**
- New endpoint: `GET /api/devices/{device_id}/processes`
- Returns: List of processes with PID, name, command line, user, CPU%, memory MB, parent PID, state
- Uses ADB command: `ps -A -o PID,USER,NAME,CPU,%MEM,COMMAND` (or equivalent)
- Polling-based initially (frontend polls every 2s by default)
- Future enhancement: WebSocket stream for process events

**Frontend Behavior:**
- On tab mount, start polling if auto-refresh is ON
- On tab unmount, stop polling
- Store previous process list to detect changes (spawns/deaths)
- Animate changes: fade-in for new, fade-out for killed
- Debounce search input to avoid excessive filtering

#### Process Actions

**Send to Workshop:**
- Captures process context (PID, package name, user)
- Navigates to Workshop tab
- Pre-fills target selector with this process
- Pre-selects "Attach" mode (since process is already running)
- User can then select scripts/plugins to inject

**Kill Process:**
- Shows confirmation modal with warning (especially for system processes)
- Backend endpoint: `POST /api/devices/{device_id}/processes/{pid}/kill`
- Uses ADB command: `kill -9 {pid}` (with root if available)
- On success, process fades from list
- On failure, shows error toast

**Inspect:**
- Opens modal with detailed process information
- Tabs within modal: Overview, Threads, Files, Network, Memory Maps
- Overview: Full command line, environment variables, working directory
- Threads: Thread IDs, names, CPU usage per thread
- Files: Open file descriptors with paths and modes
- Network: Active connections (local/remote addresses, ports, state)
- Memory Maps: Virtual memory regions (address ranges, permissions, backing files)

**Backend Requirements for Inspect:**
- Endpoint: `GET /api/devices/{device_id}/processes/{pid}/details`
- Aggregate data from multiple ADB commands:
  - `cat /proc/{pid}/cmdline` - command line
  - `cat /proc/{pid}/status` - process status
  - `ls -l /proc/{pid}/fd/` - open files
  - `cat /proc/{pid}/net/tcp` and `/proc/{pid}/net/tcp6` - network connections
  - `cat /proc/{pid}/maps` - memory maps
  - `ls /proc/{pid}/task/` - threads

#### CPU and Memory Monitoring

**Data Collection:**
- Backend stores last 60 data points per process (covers 2 minutes at 2s intervals)
- Circular buffer to avoid unbounded memory growth
- New endpoint: `GET /api/devices/{device_id}/processes/metrics?duration=60`
- Returns time-series data for graphing

**Visualization:**
- Mini spark-lines in table cells (inline SVG, very small)
- Full graphs in expanded row (using chart library like Chart.js or native canvas)
- Color-coded: Green (normal), Yellow (elevated), Red (critical)
- Threshold indicators: CPU >80%, Memory >90%

#### Activity Feed

**Event Detection:**
- Backend compares current process list with previous snapshot
- Detects: New PIDs (spawned), Missing PIDs (killed)
- Detects: CPU jumps >50% in one interval (spike)
- Detects: Memory increase >100MB in one interval (leak warning)
- Broadcasts events to frontend

**Feed Behavior:**
- Scrollable, newest at top
- Auto-scroll to newest event (with pause button if user is reading)
- Clickable events: clicking process name jumps to that row in table
- Filter buttons: Show All | Spawns Only | Kills Only | Alerts Only

### User Workflows

**Workflow 1: Monitoring App Launch**
1. User opens Applications tab, clicks "Launch" on target app
2. User immediately switches to Processes tab
3. Sees new processes spawn in real-time (green flash)
4. Identifies main app process and related services
5. Observes CPU spike during app initialization
6. Clicks "Send to Workshop" on main process to attach Frida

**Workflow 2: Detecting Background Activity**
1. User leaves Processes tab open with auto-refresh ON
2. Goes about other tasks (maybe in Workshop tab)
3. Notices activity feed shows unexpected process spawn
4. Clicks on event to jump to process in table
5. Inspects process to see what triggered it
6. Kills process or sends to Workshop for analysis

**Workflow 3: Performance Investigation**
1. Device feels slow
2. User opens Processes tab
3. Sorts by CPU usage (descending)
4. Identifies rogue process consuming 90% CPU
5. Expands row to see full details and CPU graph over time
6. Decides to kill process or investigate further

**Workflow 4: Finding Hidden Services**
1. User filters by "User Processes"
2. Scrolls through list looking for suspicious names
3. Finds process with obfuscated name (e.g., "com.system.update.v2")
4. Clicks "Inspect" to see network connections
5. Discovers it's connecting to suspicious IPs
6. Sends to Workshop for deeper analysis with network hooks

### Design Considerations

**Performance:**
- Process list can be 100+ entries on a typical device
- Use virtual scrolling for table (only render visible rows)
- Debounce filtering and sorting operations
- Lazy-load detailed inspection data (only fetch when modal opens)
- Consider pagination if device has 500+ processes (unlikely but possible)

**Visual Hierarchy:**
- Use color sparingly: green for good, yellow for warnings, red for critical
- Icon-based actions to save space (tooltip on hover explains action)
- Monospace font for PIDs and command lines
- Condensed table rows with option to expand

**Accessibility:**
- Keyboard navigation through table rows
- Screen reader announcements for new processes spawned
- Clear focus states on interactive elements

**Responsive Behavior:**
- On smaller screens, hide less critical columns (User, Status)
- Stack stats horizontally on mobile
- Activity feed collapses to icon badge with count

---

## Tab 2: Packages

### Purpose

Provide a comprehensive catalog of all installed packages, serve as the primary target selection interface for analysis, and manage package lifecycle (install, uninstall, launch, stop, clear data).

### Core Concept

This is an **inventory and control panel** for packages. Unlike Processes (which shows what's running now), this shows what's installed (whether running or not). Think of it as a combination of the Android Settings app, APK analyzer, and launch pad. Data updates on-demand, not continuously.

### Visual Layout

**Top Section: Stats Bar**
- Total installed packages (with breakdown: user vs system)
- Currently running packages count
- Total storage used by packages
- Last scanned timestamp

**Control Bar:**
- Search input (filter by package name or identifier)
- Category filter: All | User Packages | System Packages | Running Only | Recently Updated | Recently Installed
- Sort dropdown: Name (A-Z) | Name (Z-A) | Install Date | Size | Last Updated
- View mode toggle: Cards / List
- Scan button (refresh package list from device)

**Main Content: Package Grid/List**

**Card View Mode:**
Each package displayed as a card with:
- Package icon (extracted from APK or default icon)
- Package name (bold, prominent)
- Package identifier (small, monospace, gray)
- Version number
- Running status indicator (green dot if running, gray if not)
- Size (MB)
- Quick actions: Launch button, Send to Workshop button

**List View Mode:**
Compact table with columns:
- Icon (small thumbnail)
- Name
- Package ID
- Version
- Size
- Install Date
- Status (Running/Not Running)
- Actions (icons: Launch, Stop, Workshop, Details)

**Card/List Behaviors:**
- Click anywhere on card/row (except action buttons) to open details modal
- Hover shows quick action buttons
- Running packages have subtle green accent border
- System packages have gray tint to differentiate from user packages

**Package Details Modal:**
When you click a package, opens a modal with comprehensive information:

**Modal Structure:**
- Header: Package icon, name, package ID, version
- Sub-tabs within modal: Overview | Permissions | Files | Activity | APK Info

**Overview Tab:**
- Version name and code
- Install date and last update date
- Target SDK version and minimum SDK version
- Size breakdown: Package (MB) + Data (MB) + Cache (MB)
- Signature hash (for identifying repackaged packages)
- Installation source (Play Store, ADB, Unknown)
- Running status: Not Running / Running (PID: XXXX - clickable to jump to Processes tab)
- Data directory path (clickable to jump to Files tab)

**Permissions Tab:**
- List of all declared permissions
- Categorized: Location, Camera, Storage, Network, SMS, etc.
- Badge showing permission level: Normal, Dangerous, Signature
- Highlight dangerous permissions in red

**Files Tab (within modal):**
- Quick view of package's data directory structure
- File tree showing: databases, shared_prefs, files, cache
- File actions: Download, Delete, View (for text files)
- SQLite database preview (table list for .db files)
- Quick "Open in Files Tab" button for full file browser

**Activity Tab:**
- List of declared Activities, Services, Receivers, Providers
- Exported components highlighted (potential attack surface)
- Deep links and intent filters
- Launch specific Activity button (for testing)

**APK Info Tab:**
- APK file path on device
- APK hash (MD5, SHA1, SHA256)
- Extract APK button (downloads APK to host machine)
- Native libraries list (armeabi-v7a, arm64-v8a, x86, x86_64)
- Resources: Layout files, assets, raw files (counts)

**Action Buttons (in modal footer):**
- Launch Package
- Stop Package (if running)
- Clear Package Data
- Clear Cache
- Uninstall Package
- Send to Workshop (Spawn)
- Send to Workshop (Attach - if running)
- Export APK

### Functionality Deep Dive

#### Package Discovery

**Backend Requirements:**
- New endpoint: `GET /api/devices/{device_id}/packages`
- Uses ADB command: `pm list packages -f` (gets package names and APK paths)
- For each package, fetch metadata using `dumpsys package {package_name}`
- Parse output for: version, install date, permissions, components, etc.
- Extract app icon from APK (using aapt or direct APK parsing)
- Return structured JSON with all metadata

**Caching Strategy:**
- Backend caches package list for 5 minutes (configurable)
- Frontend stores in component state
- Manual refresh via Scan button invalidates cache
- Cache per device (different devices have different apps)

**Icon Handling:**
- Backend extracts icons from APKs and serves them
- New endpoint: `GET /api/devices/{device_id}/packages/{package_name}/icon`
- Returns PNG image
- Frontend caches in browser (via standard HTTP cache headers)
- Fallback to default Android icon if extraction fails

#### Package Actions

**Launch Package:**
- Backend endpoint: `POST /api/devices/{device_id}/packages/{package_name}/launch`
- Uses ADB command: `monkey -p {package_name} -c android.intent.category.LAUNCHER 1`
- Alternative: `am start -n {package_name}/{main_activity}`
- Returns success/failure
- Frontend shows toast notification
- Updates app status to "Running" after 2s delay

**Stop Package:**
- Backend endpoint: `POST /api/devices/{device_id}/packages/{package_name}/stop`
- Uses ADB command: `am force-stop {package_name}`
- Requires confirmation modal (warn about data loss)
- Updates app status to "Not Running"

**Clear Data:**
- Backend endpoint: `POST /api/devices/{device_id}/packages/{package_name}/clear-data`
- Uses ADB command: `pm clear {package_name}`
- Shows warning modal: "This will delete all app data including databases, preferences, and cache. Continue?"
- Useful for resetting app state between analysis runs

**Clear Cache:**
- Backend endpoint: `POST /api/devices/{device_id}/packages/{package_name}/clear-cache`
- Uses ADB command: `pm clear-cache {package_name}` or `rm -rf /data/data/{package_name}/cache`
- Less destructive than clearing data
- No confirmation needed

**Uninstall Package:**
- Backend endpoint: `POST /api/devices/{device_id}/packages/{package_name}/uninstall`
- Uses ADB command: `pm uninstall {package_name}`
- Shows confirmation modal: "Permanently remove {package_name}?"
- Removes package from list on success
- Cannot uninstall system packages without root

**Extract APK:**
- Backend endpoint: `GET /api/devices/{device_id}/packages/{package_name}/apk`
- Pulls APK from device using: `adb pull {apk_path} /tmp/{package_name}.apk`
- Streams APK file as download to browser
- Filename: `{package_name}_v{version}.apk`
- Shows progress indicator for large APKs

**Send to Workshop:**
- Captures package context (package name, version, running status)
- Navigates to Workshop tab
- Pre-fills target selector with package name
- If package is running: pre-selects "Attach" mode, shows PID
- If package is not running: pre-selects "Spawn" mode
- User can then configure scripts and inject

#### Detailed Package Information

**Backend Requirements:**
- Endpoint: `GET /api/devices/{device_id}/packages/{package_name}/details`
- Aggregates data from multiple sources:
  - `dumpsys package {package_name}` - comprehensive metadata
  - `aapt dump badging {apk_path}` - APK structure and permissions
  - `ls -lR /data/data/{package_name}/` - file structure
  - `stat {apk_path}` - APK file info
- Parses and structures data into JSON

**Permission Analysis:**
- Parse permissions from manifest
- Categorize by protection level
- Highlight dangerous permissions (Location, Camera, SMS, Contacts, Storage)
- Show runtime permission grant status (granted/denied)

**Component Discovery:**
- Extract Activities, Services, BroadcastReceivers, ContentProviders from manifest
- Identify exported components (security risk)
- Parse intent filters (deep links, custom schemes)
- Show component names and states (enabled/disabled)

**File Structure Preview:**
- List files in app data directory recursively
- Identify SQLite databases (*.db files)
- Identify SharedPreferences (XML files)
- Show file sizes and modification dates
- Allow individual file download

**SQLite Database Preview:**
- Endpoint: `GET /api/devices/{device_id}/packages/{package_name}/databases/{db_name}/tables`
- Pulls database from device temporarily
- Uses Python sqlite3 module to read schema
- Returns list of tables with row counts
- Frontend displays in tree structure
- Click table to see first 100 rows (lazy-loaded)

#### Search and Filtering

**Search Implementation:**
- Frontend-side filtering for instant results
- Search matches: Package name (case-insensitive), Package identifier
- Highlight matched text in results
- Show "No results" message if no matches

**Category Filters:**
- User Packages: Filter where package doesn't start with "com.android", "android", "com.google" (configurable)
- System Packages: Opposite of User Packages
- Running Only: Filter where package has active process (cross-reference with Processes data)
- Recently Updated: Filter where update date is within last 7 days
- Recently Installed: Filter where install date is within last 7 days

**Sorting:**
- All sorting done frontend-side after initial data load
- Stable sort (maintains relative order of equal elements)
- Remember sort preference in localStorage

### User Workflows

**Workflow 1: Target Selection for Analysis**
1. User opens Packages tab
2. Searches for "banking" in search bar
3. Sees 5 banking packages installed
4. Clicks on "com.chase.mobile" card
5. Reviews permissions (notices SMS and Location access)
6. Checks "Activity" sub-tab to see exported components
7. Clicks "Send to Workshop (Spawn)"
8. Workshop opens with Chase pre-selected
9. Loads SSL pinning bypass script
10. Clicks "Inject & Run" to start analysis

**Workflow 2: Package Data Inspection**
1. User has been analyzing a package, wants to see stored data
2. Opens Packages tab
3. Clicks on the package card
4. Switches to "Files" sub-tab in modal
5. Sees databases directory with "user.db"
6. Clicks on "user.db"
7. Sees tables: users, sessions, credentials
8. Clicks "credentials" table
9. Sees plaintext passwords stored (security issue found!)
10. Downloads database for reporting

**Workflow 3: Clean Analysis Environment**
1. User has run analysis on a package, wants to re-test from clean state
2. Opens Packages tab
3. Finds the package in list
4. Clicks "Clear Data" action
5. Confirms in modal
6. Package data is wiped
7. Clicks "Send to Workshop (Spawn)"
8. Re-runs analysis with fresh package state

**Workflow 4: APK Collection**
1. User wants to collect APKs of all user packages for offline analysis
2. Opens Packages tab
3. Filters by "User Packages"
4. For each package of interest, clicks to open modal
5. Goes to "APK Info" tab
6. Clicks "Extract APK"
7. APK downloads to host machine
8. Repeats for other packages

**Workflow 5: Finding Exported Components**
1. User is looking for attack surface in packages
2. Opens Packages tab
3. Iterates through packages
4. For each package, opens modal and goes to "Activity" tab
5. Scans for exported components (highlighted in red/orange)
6. Notes packages with exported Activities or Services
7. Tests those components for vulnerabilities

### Design Considerations

**Performance:**
- Initial package scan can take 10-30 seconds for 100+ packages
- Show loading skeleton during initial fetch
- Once loaded, all operations should be instant (data is in memory)
- Lazy-load package icons (load as user scrolls)
- Virtual scrolling if more than 200 packages

**Visual Design:**
- Card view is visually appealing, good for browsing
- List view is efficient, good for scanning many packages
- Use package's actual icon for familiarity
- Color-code status: Green (running), Gray (not running), Red (crashed/disabled)
- Badge overlays: System package badge, Debuggable badge, Root-required badge

**Data Freshness:**
- Show "Last scanned" timestamp prominently
- Show "Scan" button to refresh
- Auto-refresh when tab is re-focused (if data is older than 5 minutes)
- Show spinner during refresh

**Modal Design:**
- Modal should be large (80% viewport width/height)
- Sub-tabs within modal for organized information
- Scrollable content areas
- Sticky header with app name and icon
- Sticky footer with action buttons

**Accessibility:**
- Keyboard navigation through package grid/list
- Clear focus indicators
- Action buttons have descriptive aria-labels
- Status announced to screen readers

**Error Handling:**
- If APK extraction fails, show clear error message
- If package launch fails, suggest checking package is installed correctly
- If uninstall fails (system package), explain why
- Network timeout handling for long operations

---

## Backend Implementation Strategy

### New Core Module: Package Manager

Create `backend/core/package_manager.py`:

**Responsibilities:**
- Enumerate installed packages
- Fetch package metadata
- Extract APK icons
- Manage package lifecycle (install, uninstall, launch, stop)
- Query package details (permissions, components, files)

**Key Methods:**
- `list_packages(device_serial, package_type=None)` - List all packages or filter by type
- `get_package_details(device_serial, package_name)` - Comprehensive package info
- `get_package_icon(device_serial, package_name)` - Extract icon from APK
- `launch_package(device_serial, package_name)` - Start app
- `stop_package(device_serial, package_name)` - Force stop app
- `clear_package_data(device_serial, package_name)` - Clear app data
- `uninstall_package(device_serial, package_name)` - Remove app
- `extract_apk(device_serial, package_name)` - Pull APK from device
- `get_package_files(device_serial, package_name)` - List app data files
- `get_database_schema(device_serial, package_name, db_name)` - SQLite schema

**Caching:**
- Cache package list and metadata to avoid repeated ADB calls
- Cache duration: 5 minutes
- Cache key: device_serial + "packages"
- Invalidate cache on manual refresh

### New Core Module: Process Manager

Create `backend/core/process_monitor.py`:

**Responsibilities:**
- Enumerate running processes
- Track process metrics (CPU, memory over time)
- Detect process lifecycle events (spawn, kill)
- Provide detailed process information

**Key Methods:**
- `list_processes(device_serial)` - Get all running processes
- `get_process_details(device_serial, pid)` - Detailed info for specific process
- `kill_process(device_serial, pid)` - Terminate process
- `get_process_metrics(device_serial, duration=60)` - Time-series CPU/memory data
- `get_process_threads(device_serial, pid)` - Thread list
- `get_process_files(device_serial, pid)` - Open file descriptors
- `get_process_network(device_serial, pid)` - Network connections
- `get_process_maps(device_serial, pid)` - Memory maps

**Time-Series Data:**
- Store last 120 data points per process (2 minutes at 1s intervals)
- Circular buffer implementation
- Per-device storage (dict of dicts)
- Cleanup old data for processes that no longer exist

### API Endpoints to Add

**Processes:**
- `GET /api/devices/{device_id}/processes` - List all processes
- `GET /api/devices/{device_id}/processes/{pid}` - Process details
- `POST /api/devices/{device_id}/processes/{pid}/kill` - Kill process
- `GET /api/devices/{device_id}/processes/metrics` - Time-series metrics

**Packages:**
- `GET /api/devices/{device_id}/packages` - List all packages
- `GET /api/devices/{device_id}/packages/{package_name}` - Package details
- `GET /api/devices/{device_id}/packages/{package_name}/icon` - App icon
- `POST /api/devices/{device_id}/packages/{package_name}/launch` - Launch app
- `POST /api/devices/{device_id}/packages/{package_name}/stop` - Stop app
- `POST /api/devices/{device_id}/packages/{package_name}/clear-data` - Clear data
- `POST /api/devices/{device_id}/packages/{package_name}/clear-cache` - Clear cache
- `POST /api/devices/{device_id}/packages/{package_name}/uninstall` - Uninstall
- `GET /api/devices/{device_id}/packages/{package_name}/apk` - Download APK
- `GET /api/devices/{device_id}/packages/{package_name}/files` - List app files
- `GET /api/devices/{device_id}/packages/{package_name}/databases/{db_name}` - DB schema

### Logging Integration

Use existing log_streamer infrastructure:
- Process lifecycle events → `process_events` log type
- Package operations → `package_operations` log type
- Add these as new log categories in LogViewer component

---

## Frontend Implementation Strategy

### Component Structure

**New Components:**

1. **TabNavigation.vue** - Reusable tab bar component
   - Props: tabs (array of {name, label, badge}), activeTab
   - Emits: tab-change event
   - Features: Active state styling, badge support (for counts), keyboard navigation

2. **ProcessTable.vue** - Process list table
   - Props: processes (array), autoRefresh (boolean), refreshInterval (number)
   - Emits: process-selected, kill-process, send-to-workshop
   - Features: Sorting, filtering, expandable rows, mini graphs

3. **ProcessInspector.vue** - Process detail modal
   - Props: device, pid
   - Features: Tabbed modal, lazy data loading, real-time updates

4. **PackageGrid.vue** - Package grid/list view
   - Props: packages (array), viewMode (cards/list)
   - Emits: package-selected, package-action (launch, stop, etc.)
   - Features: Virtual scrolling, lazy icon loading, filtering

5. **PackageModal.vue** - Package detail modal
   - Props: device, package
   - Features: Tabbed modal, permission viewer, file browser, APK info

6. **StatsBar.vue** - Reusable stats display
   - Props: stats (array of {label, value, icon, color})
   - Compact horizontal layout

### State Management

**Composable: useProcesses.js**
- Manages process data fetching and polling
- Methods: fetchProcesses(), startPolling(), stopPolling(), killProcess()
- State: processes (array), loading, error, lastUpdate
- Polling logic with cleanup on unmount

**Composable: usePackages.js**
- Manages package data
- Methods: fetchPackages(), launchPackage(), stopPackage(), clearData(), uninstallPackage()
- State: packages (array), loading, error, lastUpdate
- Cache management

### Routing Updates

Update `frontend/src/router/index.js`:

Add query parameter support for tabs:
- `/device/:id?tab=processes`
- `/device/:id?tab=packages`
- `/device/:id?tab=files`
- `/device/:id?tab=workshop`
- Default tab: "device"

This allows deep linking: "Send to Workshop" can link to `/device/emulator-5554?tab=workshop&target=com.example.app`

### DeviceDetails.vue Restructure

**Current structure:**
- Single monolithic component with all content

**New structure (IMPLEMENTED):**
- DeviceDetails.vue is now the tab container
- Current Frida management content extracted into DeviceTab.vue
- ProcessesTab.vue created (placeholder)
- PackagesTab.vue created (placeholder)
- FilesTab.vue created (placeholder)
- WorkshopTab.vue created (placeholder)

**DeviceDetails.vue responsibilities:**
- Render compact device header
- Render TabNavigation component
- Render active tab component
- Handle tab switching
- Pass device context to all child tabs

---

## Design System Guidelines

### Color Palette

Maintain existing color scheme:
- Primary: `#7100d0` (purple accent)
- Background: `#0a0a0a` (near black)
- Surface: `#1a1a1a` (cards, modals)
- Border: `rgba(113, 0, 208, 0.2)` (subtle purple)

**New semantic colors:**
- Success: `#10b981` (green for running, healthy)
- Warning: `#f59e0b` (yellow for elevated resources)
- Danger: `#ef4444` (red for critical, killed)
- Info: `#3b82f6` (blue for information)
- Neutral: `#6b7280` (gray for inactive, system)

### Typography

Existing stack works well, add specific use cases:
- Process names, PIDs: Monospace font (`font-mono` class)
- Package identifiers: Monospace, smaller size
- CPU/Memory percentages: Tabular numbers for alignment
- Timestamps: Relative format ("2 minutes ago") with tooltip for absolute time

### Spacing

Use compact spacing to maximize information density:
- Table row padding: `py-2` (8px vertical)
- Card padding: `p-4` (16px)
- Section spacing: `mb-6` (24px)
- Modal padding: `p-6` (24px)

### Icons

Use existing icon library (heroicons):
- Processes: CPU icon, memory icon, list icon
- Actions: Play (launch), stop (square), trash (delete), arrow-right (send to workshop)
- Status: Check (running), x-circle (not running), exclamation (warning)

### Animations

Subtle, purposeful animations:
- New process spawn: Fade-in with green flash (200ms)
- Process kill: Fade-out with red tint (300ms)
- Tab switch: Smooth transition, no slide (just opacity fade, 150ms)
- Modal open/close: Scale + opacity (200ms)
- Loading states: Spinner or skeleton, not jarring

### Responsive Breakpoints

- Desktop (lg+): Full layout, all columns visible
- Tablet (md): Hide less critical columns, reduce spacing
- Mobile (sm): Stack elements vertically, hide advanced features

---

## Implementation Phases

### Phase 1: Foundation (Week 1)

**Backend:**
- Create `backend/core/process_monitor.py` module
- Implement basic process listing endpoint
- Implement process kill endpoint
- Create `backend/core/package_manager.py` module  
- Implement basic package listing endpoint
- Add API endpoints to `backend/main.py`

**Frontend (COMPLETED):**
- ✓ Created TabNavigation component
- ✓ Restructured DeviceDetails.vue with tab support
- ✓ Created placeholder tab components (ProcessesTab, PackagesTab, FilesTab, WorkshopTab)
- ✓ Implemented tab switching logic and routing with query parameters

**Deliverable (COMPLETED):** 
- ✓ Tab navigation works, you can switch between tabs
- ✓ URL query parameters enable deep linking
- ✓ Device tab contains all Frida management functionality
- ✓ Placeholder tabs ready for implementation

### Phase 2: Processes Tab (Week 2)

**Backend:**
- Implement process details endpoint
- Implement metrics collection and time-series storage
- Add process inspect endpoints (threads, files, network)

**Frontend:**
- Build ProcessTable component with full features
- Add filtering, sorting, search
- Implement process action buttons (kill, inspect)
- Create ProcessInspector modal
- Add CPU/Memory mini graphs in table
- Implement auto-refresh with polling

**Deliverable:**
- Fully functional Processes tab with live monitoring
- Can view process details, kill processes
- Graphs show resource usage trends

### Phase 3: Packages Tab (Week 3)

**Backend:**
- Implement package details endpoint
- Implement icon extraction and serving
- Add package lifecycle endpoints (launch, stop, clear, uninstall)
- Implement APK extraction endpoint
- Add file listing and database schema endpoints

**Frontend:**
- Build PackageGrid component (card + list views)
- Add filtering, sorting, search
- Implement package actions (launch, stop, etc.)
- Create PackageModal with sub-tabs
- Implement permission viewer, file browser, APK info

**Deliverable:**
- Fully functional Packages tab with comprehensive package management
- Can launch packages, view details, extract APKs
- Modal shows all relevant package information

### Phase 4: Polish and Integration (Week 4)

**Backend:**
- Add caching layer for expensive operations
- Optimize ADB command usage
- Add error handling and validation
- Write unit tests for new modules

**Frontend:**
- Add loading skeletons and error states
- Implement toast notifications for actions
- Add keyboard shortcuts
- Performance optimization (virtual scrolling, lazy loading)
- Accessibility improvements
- Mobile responsive adjustments

**Deliverable:**
- Production-ready Processes and Packages tabs
- Smooth user experience with proper feedback
- Good performance even with many processes/packages

---

## Future Expansion: Workshop Tab (Planned)

**Purpose:** Active analysis workspace for script injection, plugin execution, and instrumentation.

**High-Level Structure:**
- Tool selector: Custom Scripts | Objection | Frida-Trace | CodeShare | Network Monitor | Memory Inspector
- Target selector: Process or Package (pre-fillable from other tabs)
- Mode selector: Spawn vs Attach
- Tool-specific interface (changes based on selected tool)
- Output/results viewer (shared across tools)

**Custom Scripts Tool:**
- Code editor (Monaco Editor integration)
- Template library dropdown (pre-built scripts)
- Inject button, Stop button
- Real-time output stream
- Save/load script profiles

**Objection Integration:**
- Embedded terminal
- Quick command buttons (dump keychain, bypass SSL, etc.)
- Command history

**Frida-Trace Integration:**
- Target selection (Java classes, native functions)
- Trace output viewer with filtering
- Export trace logs

**Network Monitor:**
- HTTP/HTTPS request logger (via Frida hooks)
- SSL key dumping
- PCAP capture controls
- Export functionality

**Memory Inspector:**
- Memory region viewer
- Hexdump display
- Memory search
- Dump export

**Implementation Timeline:** After Processes and Applications are complete and stable.

---

## Future Expansion: Files Tab (Planned)

**Purpose:** Device file system browser with focus on app data directories.

**Features:**
- Tree-based file browser
- Quick access buttons (app data, sdcard, system)
- File operations: Download, upload, delete, rename
- Text file viewer
- SQLite database viewer (table browser)
- Image preview
- APK analyzer

**Implementation Timeline:** Lower priority, after Workshop basics are complete.

---

## Success Metrics

**For Processes Tab:**
- Can view all running processes in under 2 seconds
- Auto-refresh updates without UI lag
- Graphs render smoothly with no jank
- User can identify and kill problematic processes easily
- Activity feed captures all lifecycle events

**For Packages Tab:**
- Initial package list loads in under 5 seconds (for 100 packages)
- Search and filters work instantly
- Package icons load progressively without blocking
- All package actions (launch, stop, etc.) complete in under 3 seconds
- APK extraction works for packages of all sizes

**Overall:**
- Tab switching is instant (under 100ms)
- No crashes or freezes with 100+ processes or 200+ packages
- Mobile responsive on tablet-sized screens
- Accessible via keyboard navigation
- Clear error messages for all failures

---

## Technical Dependencies

**Python Packages:**
- No new dependencies required (use existing: requests, subprocess, frida, fastapi)

**JavaScript Packages to Add:**
- Consider: `chart.js` or `recharts` for graphs (or build custom with canvas)
- Consider: `@tanstack/vue-virtual` for virtual scrolling (or build custom)
- Consider: `date-fns` for timestamp formatting

**Keep it Minimal:**
- Prefer building custom components over heavy libraries
- Use existing Tailwind + DaisyUI where possible
- Only add dependencies if they save significant development time

---

## Risk Mitigation

**Risk: ADB command overhead**
- Mitigation: Cache aggressively, batch requests where possible
- Mitigation: Debounce user actions, don't query on every keystroke

**Risk: Large package count (200+) slows UI**
- Mitigation: Implement virtual scrolling for tables/grids
- Mitigation: Lazy-load icons and details
- Mitigation: Pagination as fallback

**Risk: Process monitoring creates excessive load**
- Mitigation: Configurable refresh rate (user can slow down or disable)
- Mitigation: Stop polling when tab is not active
- Mitigation: Sample processes instead of querying all every time (for metrics)

**Risk: APK extraction fails for large files**
- Mitigation: Stream file download instead of loading into memory
- Mitigation: Show progress bar for user feedback
- Mitigation: Timeout handling and retry logic

**Risk: Frontend state gets out of sync with device**
- Mitigation: Manual refresh buttons prominently available
- Mitigation: Timestamp "Last updated" shown clearly
- Mitigation: Auto-refresh when tab regains focus

---

## Open Questions for Future Discussion

1. **Metrics Granularity:** Should we track CPU/memory per-second (more data, smoother graphs) or every 2-5 seconds (less overhead)?

2. **Process Grouping:** Should we group processes by package in the UI, or keep flat list?

3. **System Package Visibility:** Should system packages be hidden by default in Packages tab, or just visually differentiated?

4. **Permission Risk Scoring:** Should we add a "risk score" for packages based on their permissions (e.g., package with SMS + Location + Internet = high risk)?

5. **Workshop Priority:** Which Workshop tool should be implemented first? Custom Scripts seems most critical, but Objection integration might provide faster value.

6. **File Browser Depth:** How deep should the Files tab go? Full-featured file manager, or just quick access to app data?

7. **Network Capture:** Should network monitoring be a separate tool in Workshop, or integrated into the Custom Scripts workflow?

---

## Conclusion

This plan establishes Processes and Packages tabs as the reconnaissance foundation of Epifania. These tabs provide visibility into device runtime state and installed software, enabling informed target selection before active analysis begins in the Workshop.

The phased implementation approach allows for iterative development with clear milestones. Phase 1 (tab navigation structure) has been completed successfully, with a clean separation between the Device tab (Frida management) and placeholder tabs for future functionality.

Once these two tabs are complete, Epifania will have transformed from a Frida server manager into a genuine dynamic analysis platform with reconnaissance capabilities. The Workshop tab will then build on this foundation to provide active instrumentation features.

The design prioritizes information density, performance, and practicality - core values for a tool aimed at security researchers who need efficiency and depth.

