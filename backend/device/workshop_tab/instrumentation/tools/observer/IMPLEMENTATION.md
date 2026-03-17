# Observer Tool - Implementation & Testing

## Overview

Observer tool for real-time Java and Native method hooking with comprehensive logging and WebSocket streaming.

## Architecture

```
instrumentation/
├── instrumentation_routes.py     # API endpoints
└── tools/observer/
    ├── observer.py                # Core Observer logic
    ├── hook_manager.py           # Session state management
    ├── script_generator.py       # Script compilation
    └── logging/
        ├── observer_logger.py    # Multi-file logging
        └── log_paths.py          # Path configuration
```

## Critical Implementation Detail: RPC-Based Hook Injection

**Problem:** Initial implementation used template variables (`{{HOOKS_JSON}}`) injected into compiled JavaScript, which corrupted Frida's bundle header causing `malformed package` errors.

**Solution:** Hooks are now passed via RPC after script loading:

```python
# script_generator.py
script_code = script_compiler.compile("instrumentation/observer/java", "observer_java.ts")
return script_code, hooks_with_ids  # No template vars

# observer.py
self._script = self.session.create_script(script_code)
self._script.load()
result = self._script.exports_sync.install_hooks(hooks_with_ids)  # Pass via RPC
```

TypeScript scripts accept hooks as function parameters:
```typescript
rpc.exports = {
    installHooks(hooks: HookConfig[]): Promise<{...}> {
        // Install hooks
    }
};
```

**Benefits:**
- No bundle corruption
- Script compiled once and cached
- Different hooks can be passed without recompilation
- Consistent with Discovery scripts pattern

## API Endpoints

All require existing Frida session (attach/spawn first).

### POST `/api/devices/{device_id}/observer/start`
```json
{
  "client_id": "string",
  "app_package": "com.example.app",
  "hooks": [
    {
      "type": "java",
      "class_name": "android.app.Activity",
      "method_name": "onResume",
      "return_type": "void",
      "parameters": []
    }
  ],
  "time_limit": 300  // Optional: auto-stop after N seconds
}
```

### POST `/api/devices/{device_id}/observer/stop`
```json
{
  "client_id": "string"
}
```

### GET `/api/devices/{device_id}/observer/status?client_id=...`
Returns session info, hooks status, call counts, elapsed time.

### POST `/api/devices/{device_id}/observer/logs`
```json
{
  "client_id": "string",
  "log_files": ["aggregated", "summary", "operations"]
}
```

### WebSocket `/ws/devices/{device_id}/instrumentation/observer`
Streams status updates every 100ms.

### POST `/{device_id}/observer/save_script`
Saves the compiled Frida script bundle for the active session to `script_vault/personal/observer/{session_name}/`.

```json
{
  "client_id": "string"
}
```

Files written:
- `hooks.json` — hook list with IDs, types, class/method names, and signatures
- `compiled_script.js` — compiled Frida script retrieved via `HookManager.get_script_code()`
- `observer_template.ts` — source TypeScript template copied from `script_vault/instrumentation/observer/{type}/`
- `README.md` — generated from `README_TEMPLATE.md` with session name, package, device, and hook sample

Returns `{ "success": true, "path": "/absolute/path", "session_name": "..." }`.

### POST `/open_folder`
Opens a path in the system file manager. Platform-aware; does not require an active device session.

```json
{
  "path": "/absolute/or/relative/path"
}
```

On Linux, tries `xdg-open` → `gio` → `nautilus` → `dolphin` → `thunar` in order, using the first available command. Inherits `DISPLAY`, `XAUTHORITY`, and `DBUS_SESSION_BUS_ADDRESS` from the server environment. On macOS uses `open`; on Windows uses `explorer`. Launched as a detached process — non-blocking.

## Log Structure

`logs/instrumentation/observer/{package}/{date}/{session_number}/`

Files created per session:
- `frida_operations.log` - Script lifecycle events
- `aggregated.log` - All hook events chronologically
- `console_raw.log` - Raw Frida console output
- `summary.log` - Session statistics (JSON)
- `metadata.json` - Session configuration
- `hooks/{hook_id}.log` - Individual method logs (created on first call)

## Hook Manager

Thread-safe singleton tracking active Observer sessions per device.

Key methods:
- `start_observer_session()` - Initialize session; stores `script_code` in session data
- `stop_observer_session()` - Cleanup and unload script
- `get_session_status()` - Current session info with aggregated stats
- `increment_hook_call_count()` - Update call statistics atomically
- `increment_hook_error_count()` - Update error statistics atomically
- `is_session_active()` - Check if monitoring
- `get_top_hooks(limit)` - Returns top N hooks sorted by call rate descending; each entry includes `hook_id`, `class_name`, `method_name`, `call_count`, `call_rate`, `error_count`
- `get_script_code()` - Returns the compiled script code stored at session start

`get_session_status()` computes the following aggregate fields across all hooks on every call:
- `total_calls` — sum of all hook `call_count` values
- `total_errors` — sum of all hook `error_count` values
- `active_hooks` — count of hooks with `call_count > 0`
- `calls_per_second` — `total_calls / elapsed` rounded to 2 decimal places
- Per-hook `call_rate` — `call_count / elapsed` rounded to 2 decimal places

## Real-Time Stats Updater

`Observer._start_stats_updater()` spawns a daemon thread that writes `stats.json` to the session directory once per second while the session is active. The same data is also flushed to `summary.log` on every tick via `update_summary()`.

`stats.json` structure:
```json
{
  "session_start": "2026-01-14T21:09:29",
  "last_update": "2026-01-14T21:09:45",
  "status": "active",
  "elapsed": 16.1,
  "time_limit": 300,
  "total_calls": 412,
  "total_errors": 0,
  "calls_per_second": 25.6,
  "active_hooks": 3,
  "hooks_count": 5,
  "top_hooks": [...]
}
```

On `stop_observation()`, a final `stats.json` is written with `"status": "stopped"` before the session is removed from `HookManager`. The updater thread is joined with a 2-second timeout before session cleanup.

`_script_code` is captured in `Observer.start_observation()` immediately after script generation and forwarded to `HookManager.start_observer_session()` as `script_code`. This allows `save_script` to retrieve the compiled JS after the Frida script object has been created.

## Observer Workflow

1. Frontend attaches/spawns Frida session
2. Frontend calls `/observer/start` with hooks
3. Observer:
   - Validates hooks
   - Compiles script (or uses cache)
   - Loads script into Frida session
   - Calls `installHooks(hooks)` via RPC
   - Registers message handlers
   - Creates log files
   - Starts time limit timer (if specified)
4. Hooks capture method entry/exit events
5. Events logged to files and streamed via WebSocket
6. Frontend calls `/observer/stop` when done

## Testing

Three test scripts in `tests/observer_backend/`:

1. **test_observer_simple.py** - Quick validation (8 steps)
   - Device detection, session management, spawn, start/stop, logs
   - **Result:** 100% pass

2. **test_observer_backend.py** - Comprehensive suite (11 tests)
   - Includes WebSocket testing, hook installation verification
   - **Result:** 85.7% pass (6/7 completed, stopped early)

3. **test_observer_native.py** - Native hooks with libc.so functions
   - Tests malloc/free/strlen hooks with 20s time limit
   - High-frequency call testing

**Run tests:**
```bash
cd /home/vladdum/Desktop/Projects/Development/epifania
source backend/venv/bin/activate
python3 tests/observer_backend/test_observer_simple.py
```

## Known Demands

1. **Methods with multiple overloads** require `.overload(signature)`:
   - Example: `onCreate` has 2 overloads, hook installation fails
   - Solution: Frontend must specify exact signature or handle overload selection
   - `onResume` works (single overload)

## Dependencies

- `websocket-client==1.9.0` (added to requirements.txt for testing)
- Existing: frida, frida-java-bridge

## Modified Files

- `backend/requirements.txt` - Added websocket-client
- `backend/core/log_paths.py` - Added LOGS_INSTRUMENTATION_OBSERVER
- `backend/main.py` - Registered instrumentation router, added WebSocket endpoint
- `backend/device/workshop_tab/discovery/script_compiler.py` - Added double-quote escaping (not used by RPC approach)
- `backend/device/workshop_tab/instrumentation/tools/observer/hook_manager.py` - Added `get_top_hooks()`, `increment_hook_error_count()`, `get_script_code()`; `get_session_status()` now computes aggregate stats; `start_observer_session()` accepts and stores `script_code`
- `backend/device/workshop_tab/instrumentation/tools/observer/observer.py` - Added `_start_stats_updater()`, `stats.json` writes, `_script_code` storage, `increment_hook_error_count()` call on error events
- `backend/device/workshop_tab/instrumentation/instrumentation_routes.py` - Added `save_script` and `open_folder` endpoints
- `frontend/src/views/device/workshop/composables/useObserverStats.js` - New composable
- `frontend/src/views/device/workshop/components/instrumentation/toolkit/tools/observer/ObserverStatsPanel.vue` - New component
- `frontend/src/views/device/workshop/components/instrumentation/toolkit/tools/observer/HookCard.vue` - New component
- `frontend/src/views/device/workshop/components/instrumentation/toolkit/tools/observer/SpeedometerGauge.vue` - New component

## Frontend Integration Notes

1. **Frida session required first:**
   ```
   POST /workshop/frida/attach or /workshop/frida/spawn
   → Then POST /observer/start
   ```

2. **Hook format** from Discovery data:
   ```javascript
   {
     type: "java",
     class_name: method.class_name,
     method_name: method.name,
     signature: method.signature,  // Important for overload resolution
     return_type: method.return_type,
     parameters: method.parameters
   }
   ```

3. **Status polling** or WebSocket for live updates

4. **Log streaming** via `/observer/logs` endpoint for viewing events

5. **Session cleanup** happens automatically on:
   - Time limit reached
   - Manual stop
   - Frida session detach
   - Backend restart

## Frontend Components

```
frontend/src/views/device/workshop/
├── composables/
│   └── useObserverStats.js
└── components/instrumentation/toolkit/tools/observer/
    ├── ObserverStatsPanel.vue
    ├── HookCard.vue
    └── SpeedometerGauge.vue
```

### `useObserverStats.js`

Composable providing WebSocket state and processed hook data to Observer UI components.

WebSocket endpoint: `ws://localhost:8000/ws/devices/{device_id}/instrumentation/observer`

Behavior:
- Reconnects up to 3 times with exponential backoff on unexpected close.
- On each `status_update` message, computes windowed `calls_per_second` from the delta between consecutive `total_calls` values divided by wall-clock elapsed time (`dt`).
- Per-hook call rate is computed from delta `call_count` divided by `dt`, then smoothed with EMA (alpha = 0.35) to reduce visual noise.
- `maxCallRate` is an adaptive scale ceiling: raised at 25% speed, decayed at 6% speed, with 35% headroom above observed maximum and a floor of 5 calls/s.
- On `session_ended` message, disconnects after a 3-second delay.
- Clears all accumulated state on disconnect (counters, EMA map, `maxCallRate` reset to 10).

`sortedHooks` computed property applies filter then sort to the live hook list:

| Sort key | Order |
|---|---|
| `top_activity` (default) | call_rate descending |
| `most_calls` | call_count descending |
| `most_errors` | error_count descending |
| `alphabetical` | method_name ascending |

| Filter key | Condition |
|---|---|
| `all` (default) | no filter |
| `active_only` | call_count > 0 |
| `with_errors` | error_count > 0 |

### `ObserverStatsPanel.vue`

Fixed bottom-right overlay panel (z-index 9999). When expanded, occupies `75% - 2rem` of viewport width to the left of the right edge.

Props: `deviceSerial` (String), `clientId` (String), `isObserving` (Boolean), `showDashboard` (Boolean).
Emits: `close`.

Layout (expanded):
- **Left sidebar** (320 px fixed): 2×2 stat grid (Total Calls, Calls/s, Active Hooks, Errors) and an Actions section.
- **Right area**: hook count summary, sort/filter controls, paginated `HookCard` grid (10 per page, max height 260 px with custom scrollbar).

Connects to `useObserverStats` on mount when `isObserving` is true; disconnects on unmount or when `isObserving` becomes false. Resets to page 1 and expands the panel on observation start.

**Save Script action**: calls `POST /{device_id}/observer/save_script`, then immediately fires `POST /open_folder` with the returned absolute path. The open-folder call is non-blocking; errors are swallowed. Uses a toast notification to confirm success or report failure.

### `HookCard.vue`

Individual hook tile in the `ObserverStatsPanel` hook grid.

- Displays `class_name` (truncated to last 2 segments by default; expandable via toggle button for names longer than 26 characters) and `method_name`.
- Clicking the class name copies the full name to the clipboard and shows a transient "Copied!" badge.
- Centers a `SpeedometerGauge` with the hook's EMA-smoothed call rate and the panel-level `maxCallRate` as the scale ceiling.
- Displays call count, error count, and formatted rate below the gauge.
- Three CSS-driven visual states via `--hook-accent` CSS variable:
  - `hook-card--idle` — no calls (slate border, grey accent)
  - `hook-card--active` — call_rate > 0.01 (cyan border and accent stripe)
  - `hook-card--error` — error_count > 0 (red border and accent stripe)
- Triggers a 320 ms bottom accent-stripe pulse animation (`accentPulse`) on each new call event detected via a watcher on `hook.call_count`.

### `SpeedometerGauge.vue`

SVG tachometer arc gauge rendering a 270° arc with the 90° gap at the bottom.

- 46 tick marks (45 intervals); every 5th tick is a major tick with heavier stroke weight.
- Tick length and stroke weight increase progressively from start to end of arc.
- Tick color transitions by arc position: cyan (0–40%) → green (40–70%) → amber (70–90%) → red (90–100%).
- Fill animates via a `requestAnimationFrame` easeOutCubic loop. Duration scales with the size of the change: `clamp(180ms, 220 + delta*10, 900ms)`.
- A minimum fill of 2% is applied when value > 0 so the first tick is always visible.
- `maxValue` is supplied by `ObserverStatsPanel`'s adaptive `maxCallRate`; the gauge never displays a fixed maximum.

Props: `value` (Number), `maxValue` (Number, default 10), `size` (Number px, default 100).

## Performance Notes

- Script compilation: ~1-2 seconds (first time only, then cached)
- Hook installation: <100ms for typical hooks
- Memory: ~1MB per session for log files
- WebSocket: 10 updates/second (100ms interval)
- Cleanup: Old sessions kept (10 most recent per package)
