# Process Inspector / Overview Module

Backend module for detailed per-process inspection on Android devices via ADB.

## Architecture

```
overview/
├── __init__.py
├── process_inspector.py      # Orchestrator - combines all collectors
└── collectors/
    ├── __init__.py
    ├── identity.py           # Process identity, scheduling, timing
    ├── memory.py             # PSS/USS, smaps_rollup, dumpsys meminfo
    ├── threads.py            # Thread list with names and states
    ├── files.py              # File descriptors, limits, categorization
    ├── network.py            # TCP/UDP connections for PID
    ├── io_stats.py           # I/O statistics (root-dependent)
    └── relationships.py      # Parent/children process tree
```

## API Endpoint

```
GET /api/devices/{device_id}/processes/{pid}/overview
```

Returns comprehensive process data. Root access is automatically detected and used when available.

## Response Structure

```json
{
  "pid": 1234,
  "identity": { ... },
  "memory": { ... },
  "threads": { ... },
  "files": { ... },
  "network": { ... },
  "io": { ... },
  "relationships": { ... },
  "permissions": {
    "has_root": true,
    "io_stats_available": true,
    "detailed_memory_available": true,
    "dumpsys_memory_available": true,
    "full_fd_access": true
  }
}
```

---

## Testing Guide

### Prerequisites

1. Backend server running: `cd backend && source venv/bin/activate && uvicorn main:app --reload`
2. Android device/emulator connected via ADB
3. Device ID (run `adb devices` to get it)

### Quick Test (All Data)

```bash
# Replace DEVICE_ID with your device serial (e.g., emulator-5554)
# Replace PID with a valid process ID from the device

# Get a list of processes first
curl -s http://localhost:8000/api/devices/DEVICE_ID/processes | jq '.processes[:5]'

# Pick a PID and get full overview
curl -s http://localhost:8000/api/devices/DEVICE_ID/processes/PID/overview | jq
```

---

## Testing Individual Collectors

### 1. Identity Collector

**What it collects:**
- PID, PPID, process name, state
- UID/GID
- Thread count
- Nice value, priority
- CPU time (utime, stime)
- Running duration (seconds since start)
- Full command line

**Test command:**
```bash
curl -s http://localhost:8000/api/devices/DEVICE_ID/processes/PID/overview | jq '.identity'
```

**Expected output:**
```json
{
  "pid": 1234,
  "name": "com.example.app",
  "state": "sleeping",
  "state_char": "S",
  "ppid": 567,
  "uid": 10123,
  "gid": 10123,
  "thread_count": 15,
  "nice": 0,
  "priority": 20,
  "utime_ticks": 12345,
  "stime_ticks": 6789,
  "cpu_time_ticks": 19134,
  "running_seconds": 3600,
  "cmdline": "com.example.app"
}
```

**Manual verification:**
```bash
adb -s DEVICE_ID shell cat /proc/PID/stat
adb -s DEVICE_ID shell cat /proc/PID/status
adb -s DEVICE_ID shell cat /proc/PID/cmdline
```

---

### 2. Memory Collector

**What it collects:**
- RSS, VSZ, Peak, HWM, Swap (from /proc/PID/status)
- PSS, USS, Private/Shared Clean/Dirty (from /proc/PID/smaps_rollup)
- Detailed heap breakdown for Android apps (from dumpsys meminfo)

**Test command:**
```bash
curl -s http://localhost:8000/api/devices/DEVICE_ID/processes/PID/overview | jq '.memory'
```

**Expected output:**
```json
{
  "rss_kb": 45000,
  "vsz_kb": 120000,
  "peak_kb": 48000,
  "hwm_kb": 47000,
  "swap_kb": 0,
  "pss_kb": 32000,
  "uss_kb": 28000,
  "private_clean_kb": 8000,
  "private_dirty_kb": 20000,
  "shared_clean_kb": 10000,
  "shared_dirty_kb": 5000,
  "smaps_available": true,
  "dumpsys_available": true,
  "dumpsys": {
    "total_pss_kb": 32000,
    "java_heap_kb": 8000,
    "native_heap_kb": 12000,
    "code_kb": 5000,
    "stack_kb": 500,
    "graphics_kb": 3000,
    "system_kb": 3500
  }
}
```

**Manual verification:**
```bash
adb -s DEVICE_ID shell cat /proc/PID/status | grep -E "Vm|Swap"
adb -s DEVICE_ID shell cat /proc/PID/smaps_rollup
adb -s DEVICE_ID shell dumpsys meminfo PID
```

**Notes:**
- `smaps_rollup` requires Android 9+ (API 28)
- `dumpsys meminfo` only works for Android apps, not native processes
- If `smaps_available` is false, PSS/USS will be null

---

### 3. Threads Collector

**What it collects:**
- Thread count
- List of threads with TID, name, state, CPU time
- Main thread identification

**Test command:**
```bash
curl -s http://localhost:8000/api/devices/DEVICE_ID/processes/PID/overview | jq '.threads'
```

**Expected output:**
```json
{
  "count": 15,
  "threads": [
    {
      "tid": 1234,
      "name": "main",
      "state": "sleeping",
      "state_char": "S",
      "utime_ticks": 5000,
      "stime_ticks": 2000,
      "cpu_time_ticks": 7000,
      "is_main": true
    },
    {
      "tid": 1235,
      "name": "AsyncTask #1",
      "state": "sleeping",
      "state_char": "S",
      "utime_ticks": 100,
      "stime_ticks": 50,
      "cpu_time_ticks": 150,
      "is_main": false
    }
  ],
  "main_thread_tid": 1234
}
```

**Manual verification:**
```bash
adb -s DEVICE_ID shell ls /proc/PID/task
adb -s DEVICE_ID shell cat /proc/PID/task/TID/comm
adb -s DEVICE_ID shell cat /proc/PID/task/TID/stat
```

---

### 4. Files Collector

**What it collects:**
- Open file descriptor count
- FD limits (soft/hard)
- Categorized FD list (files, sockets, pipes, devices, etc.)

**Test command:**
```bash
curl -s http://localhost:8000/api/devices/DEVICE_ID/processes/PID/overview | jq '.files'
```

**Expected output:**
```json
{
  "count": 42,
  "max_fds": 32768,
  "soft_limit": 1024,
  "hard_limit": 32768,
  "categories": {
    "file": 10,
    "socket": 15,
    "pipe": 5,
    "device": 3,
    "anon_inode": 8,
    "eventfd": 1
  },
  "fds": [
    { "fd": 0, "target": "/dev/null", "type": "device" },
    { "fd": 1, "target": "/dev/null", "type": "device" },
    { "fd": 3, "target": "socket:[12345]", "type": "socket" },
    { "fd": 4, "target": "/data/data/com.example.app/databases/app.db", "type": "file" }
  ],
  "truncated": false,
  "full_access": true
}
```

**Manual verification:**
```bash
adb -s DEVICE_ID shell ls -la /proc/PID/fd
adb -s DEVICE_ID shell cat /proc/PID/limits | grep "Max open files"
```

**Notes:**
- Without root, some FDs may be inaccessible (Permission denied)
- `full_access` indicates whether all FDs were readable
- List is truncated to 100 entries; `truncated` flag indicates if there are more

---

### 5. Network Collector

**What it collects:**
- TCP connections (IPv4 and IPv6)
- UDP connections (IPv4 and IPv6)
- Connection states (ESTABLISHED, LISTEN, TIME_WAIT, etc.)
- State summary counts

**Test command:**
```bash
curl -s http://localhost:8000/api/devices/DEVICE_ID/processes/PID/overview | jq '.network'
```

**Expected output:**
```json
{
  "tcp_count": 5,
  "udp_count": 2,
  "total_count": 7,
  "tcp_connections": [
    {
      "protocol": "tcp",
      "local_address": "10.0.2.15",
      "local_port": 45678,
      "remote_address": "142.250.185.206",
      "remote_port": 443,
      "state": "ESTABLISHED"
    },
    {
      "protocol": "tcp6",
      "local_address": "::1",
      "local_port": 8080,
      "remote_address": "::",
      "remote_port": 0,
      "state": "LISTEN"
    }
  ],
  "udp_connections": [
    {
      "protocol": "udp",
      "local_address": "0.0.0.0",
      "local_port": 68,
      "remote_address": "0.0.0.0",
      "remote_port": 0,
      "state": "UNCONN"
    }
  ],
  "state_summary": {
    "ESTABLISHED": 3,
    "LISTEN": 1,
    "TIME_WAIT": 1
  },
  "truncated": false
}
```

**Manual verification:**
```bash
adb -s DEVICE_ID shell cat /proc/PID/net/tcp
adb -s DEVICE_ID shell cat /proc/PID/net/tcp6
adb -s DEVICE_ID shell cat /proc/PID/net/udp
adb -s DEVICE_ID shell cat /proc/PID/net/udp6
```

---

### 6. I/O Stats Collector

**What it collects:**
- Read/write character counts (rchar, wchar)
- Read/write syscall counts (syscr, syscw)
- Actual disk read/write bytes
- Cancelled write bytes

**Test command:**
```bash
curl -s http://localhost:8000/api/devices/DEVICE_ID/processes/PID/overview | jq '.io'
```

**Expected output (with root):**
```json
{
  "rchar": 123456789,
  "wchar": 987654321,
  "syscr": 5000,
  "syscw": 3000,
  "read_bytes": 50000000,
  "write_bytes": 30000000,
  "cancelled_write_bytes": 0,
  "available": true
}
```

**Expected output (without root):**
```json
null
```

**Manual verification:**
```bash
adb -s DEVICE_ID shell cat /proc/PID/io
# If permission denied:
adb -s DEVICE_ID shell su -c 'cat /proc/PID/io'
```

**Notes:**
- Typically requires root access
- Returns `null` if not accessible
- Check `permissions.io_stats_available` to know if data was retrieved

---

### 7. Relationships Collector

**What it collects:**
- Parent process (PID, name, state)
- Child processes list
- Process tree depth (levels to init/PID 1)

**Test command:**
```bash
curl -s http://localhost:8000/api/devices/DEVICE_ID/processes/PID/overview | jq '.relationships'
```

**Expected output:**
```json
{
  "parent_pid": 567,
  "parent": {
    "pid": 567,
    "name": "zygote64",
    "state": "S"
  },
  "children_count": 2,
  "children": [
    { "pid": 1300, "name": "WebViewLoader", "state": "S" },
    { "pid": 1301, "name": "RenderThread", "state": "S" }
  ],
  "tree_depth": 3,
  "truncated": false
}
```

**Manual verification:**
```bash
# Get parent
adb -s DEVICE_ID shell cat /proc/PID/stat | awk '{print $4}'

# Find children (processes with this PID as parent)
adb -s DEVICE_ID shell "for p in /proc/[0-9]*; do grep -l 'PPid:\s*PID' \$p/status 2>/dev/null; done"
```

---

## Permissions Object

The `permissions` object tells you what data was successfully collected:

```json
{
  "has_root": true,
  "io_stats_available": true,
  "detailed_memory_available": true,
  "dumpsys_memory_available": true,
  "full_fd_access": true
}
```

| Field | Meaning |
|-------|---------|
| `has_root` | Device has root access (su available) |
| `io_stats_available` | `/proc/PID/io` was readable |
| `detailed_memory_available` | `smaps_rollup` was readable (PSS/USS available) |
| `dumpsys_memory_available` | `dumpsys meminfo` returned data (Android app) |
| `full_fd_access` | All file descriptors were readable |

---

## Test Script

Save this as `test_process_overview.sh`:

```bash
#!/bin/bash

API_BASE="http://localhost:8000/api/devices"
DEVICE_ID="${1:-emulator-5554}"

echo "=== Testing Process Overview API ==="
echo "Device: $DEVICE_ID"
echo

# Get first user process
PID=$(curl -s "$API_BASE/$DEVICE_ID/processes" | jq -r '.processes[] | select(.user | startswith("u0_")) | .pid' | head -1)

if [ -z "$PID" ]; then
    echo "No user process found, using system_server"
    PID=$(curl -s "$API_BASE/$DEVICE_ID/processes" | jq -r '.processes[] | select(.name == "system_server") | .pid')
fi

echo "Testing PID: $PID"
echo

echo "--- Full Overview ---"
curl -s "$API_BASE/$DEVICE_ID/processes/$PID/overview" | jq

echo
echo "--- Identity Only ---"
curl -s "$API_BASE/$DEVICE_ID/processes/$PID/overview" | jq '.identity'

echo
echo "--- Memory Only ---"
curl -s "$API_BASE/$DEVICE_ID/processes/$PID/overview" | jq '.memory'

echo
echo "--- Threads Summary ---"
curl -s "$API_BASE/$DEVICE_ID/processes/$PID/overview" | jq '{count: .threads.count, main_thread: .threads.main_thread_tid}'

echo
echo "--- Files Summary ---"
curl -s "$API_BASE/$DEVICE_ID/processes/$PID/overview" | jq '{count: .files.count, categories: .files.categories}'

echo
echo "--- Network Summary ---"
curl -s "$API_BASE/$DEVICE_ID/processes/$PID/overview" | jq '{tcp: .network.tcp_count, udp: .network.udp_count, states: .network.state_summary}'

echo
echo "--- I/O Stats ---"
curl -s "$API_BASE/$DEVICE_ID/processes/$PID/overview" | jq '.io'

echo
echo "--- Relationships ---"
curl -s "$API_BASE/$DEVICE_ID/processes/$PID/overview" | jq '.relationships'

echo
echo "--- Permissions ---"
curl -s "$API_BASE/$DEVICE_ID/processes/$PID/overview" | jq '.permissions'
```

Run with:
```bash
chmod +x test_process_overview.sh
./test_process_overview.sh YOUR_DEVICE_ID
```

---

## Common Issues

### Process Not Found
```json
{"detail": "Process 12345 not found or inaccessible"}
```
The process may have died. Get a fresh PID from `/processes` endpoint.

### Empty Memory Data
If `smaps_available` is false, the device may be running Android 8 or older. PSS/USS will be null.

### No dumpsys Data
`dumpsys meminfo` only works for Android app processes (those managed by ActivityManager). Native processes will have `dumpsys_available: false`.

### I/O Stats Null
Requires root access on most devices. Check `permissions.io_stats_available`.

### Partial FD List
Without root, some file descriptors may not be readable. Check `files.full_access`.

