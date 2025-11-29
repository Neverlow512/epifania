# New Backend Monitoring Features

## Overview

Extended the `processes_tab` monitoring subsystem with four new modules for comprehensive device telemetry.

## New Modules

### CPU Monitor (`cpu_monitor.py`)
- Overall CPU usage percentage (delta-based calculation from `/proc/stat`)
- Top N CPU-consuming processes with PID, name, and CPU %

### Memory Monitor (`memory_monitor.py`)
- System RAM: total, used, free, available, buffers, cached (all in MB)
- Per-process memory when a focused PID is provided: RSS, VSZ, peak, high-water mark

### Storage Monitor (`storage_monitor.py`)
- Partition usage: total, used, free (in GB) and percent used
- Default targets `/data`, supports querying any partition
- Bulk endpoint for all relevant partitions

### Network Monitor (`network_monitor.py`)
- Throughput: bytes sent/received per second (delta-based)
- Per-process TCP connections when focused PID provided: local/remote addresses, connection state
- Recent endpoints: top 10 remote IPs/ports seen in last 5 minutes with hit counts

### Process Churn (extended `dprocess_monitor.py`)
- Tracks spawn/kill events with timestamps
- Returns counts for configurable time windows (default 60s)
- Lists recent spawned/killed processes with names and time since event

## API Endpoints

| Endpoint | Returns |
|----------|---------|
| `GET /{device_id}/system/cpu?top_n=5` | `overall_percent`, `top_consumers[]` |
| `GET /{device_id}/system/memory?pid=` | `total_mb`, `used_mb`, `free_mb`, `available_mb`, optional `focused_process{}` |
| `GET /{device_id}/system/storage?partition=/data` | `total_gb`, `used_gb`, `free_gb`, `percent_used` |
| `GET /{device_id}/system/storage/all` | `partitions[]` with all mountpoints |
| `GET /{device_id}/system/network?pid=` | `throughput{}`, `recent_endpoints[]`, optional `focused_process{}` with connections |
| `GET /{device_id}/system/network/connections` | All TCP connections on device |
| `GET /{device_id}/processes/churn?window=60` | `spawned_count`, `killed_count`, `net_change`, `recent_spawned[]`, `recent_killed[]` |

## Frontend Display Options

**Stats Bar / Dashboard:**
- CPU load gauge or percentage with sparkline
- RAM usage bar (used/total) with free amount
- Storage usage bar for /data partition
- Network throughput indicators (upload/download speeds)
- Process churn indicator (spawned/killed in last N seconds)

**Process Table Integration:**
- Click row to set "focused process"
- Focused process gets detailed memory breakdown
- Focused process shows active TCP connections and remote endpoints

**Detailed Panels:**
- Top CPU consumers list with live percentages
- Network connections table with local/remote addresses and states
- Recent remote endpoints with connection frequency
- Process activity timeline showing spawns/kills

