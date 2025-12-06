# Packages Tab API Documentation

## Overview

Fast, stateless API for Android package management. No polling sessions required - use manual refresh.

## Performance

- List user packages (7): **0.07s**
- List all packages (102): **0.7s**
- Package details (1): **~0.2s**

## Endpoints

### List Packages

```http
GET /api/devices/{device_id}/packages?filter={type}
```

**Query Parameters:**
- `filter`: `"user"` | `"system"` | `"all"` (default: `"all"`)

**Response:**
```json
{
  "packages": [
    {
      "package_id": "com.google.android.gm",
      "name": "Gmail",
      "is_system": false,
      "pid": 12345,
      "is_running": true,
      "version": null,
      "version_code": null,
      "install_date": null,
      "size_mb": null
    }
  ],
  "count": 102,
  "stats": {
    "user": 7,
    "system": 95,
    "running": 19
  }
}
```

**Note:** List returns lightweight data. Version/size are `null` - fetch details for full metadata.

### Get Package Details

```http
GET /api/devices/{device_id}/packages/{package_id}
```

**Response:**
```json
{
  "package_id": "com.google.android.gm",
  "name": "Gmail",
  "is_system": false,
  "version": "2024.11.10.696147426.Release",
  "version_code": 64865294,
  "install_source": "com.android.vending",
  "apk_path": "/data/app/.../base.apk",
  "size_mb": 153.0,
  "data_size_mb": 2.0,
  "cache_size_mb": 0.5,
  "permissions": ["android.permission.INTERNET", "..."],
  "permissions_count": 20,
  "target_sdk": 35,
  "min_sdk": 23,
  "signing_cert": "SHA256:abc123...",
  "main_activity": ".ui.MainActivity",
  "pid": 12345,
  "is_running": true
}
```

### Install Package

```http
POST /api/devices/{device_id}/packages/install
```

**Request Body:**
```json
{
  "apk_source": "/home/user/Downloads/app.apk",
  "is_local_file": true,
  "device_temp_path": "/data/local/tmp/temp_install.apk"
}
```

**Parameters:**
- `apk_source`: Local file path (if `is_local_file=true`) or device path (if `false`)
- `is_local_file`: `true` = install from computer, `false` = install from device
- `device_temp_path`: Staging path on device (optional, default: `/data/local/tmp/temp_install.apk`)

**Response:**
```json
{
  "success": true,
  "message": "Package installed successfully from /home/user/app.apk"
}
```

### Uninstall Package

```http
DELETE /api/devices/{device_id}/packages/{package_id}?keep_data={bool}
```

**Query Parameters:**
- `keep_data`: `true` to preserve app data (optional, default: `false`)

**Response:**
```json
{
  "success": true,
  "message": "Package com.example.app uninstalled successfully"
}
```

### Extract APK

```http
POST /api/devices/{device_id}/packages/{package_id}/pull
```

**Request Body:**
```json
{
  "destination_path": "/home/user/Downloads/apps/com.example.app.apk"
}
```

**Parameters:**
- `destination_path`: Where to save APK locally (auto-creates dirs, auto-appends `.apk` if directory)

**Response:**
```json
{
  "success": true,
  "message": "Package com.example.app pulled successfully",
  "local_path": "/home/user/Downloads/apps/com.example.app.apk"
}
```

### Launch Package

```http
POST /api/devices/{device_id}/packages/{package_id}/launch
```

**Response:**
```json
{
  "success": true,
  "message": "Package com.example.app launched successfully"
}
```

### Force Stop Package

```http
POST /api/devices/{device_id}/packages/{package_id}/stop
```

**Response:**
```json
{
  "success": true,
  "message": "Package com.example.app force stopped successfully"
}
```

### Clear Cache

```http
POST /api/devices/{device_id}/packages/{package_id}/clear-cache
```

**Response:**
```json
{
  "success": true,
  "message": "Cache cleared for com.example.app"
}
```

### Clear Data

```http
POST /api/devices/{device_id}/packages/{package_id}/clear-data
```

**Response:**
```json
{
  "success": true,
  "message": "Data cleared for com.example.app"
}
```

## Frontend Integration

### Recommended Flow

1. **Initial Load**: Fetch user packages only (`filter=user`)
2. **User Action**: Show system toggle to fetch all if needed
3. **Package Selection**: Fetch full details on click
4. **Actions**: Call action endpoints, then refresh list
5. **Process Tab Link**: Use `pid` field to link to Processes tab

### Settings to Configure

```javascript
const settings = {
  // Paths
  deviceTempPath: "/data/local/tmp/temp_install.apk",
  extractDir: "~/Downloads/epifania_extracted_apks/",
  
  // Display
  defaultFilter: "user",
  autoRefreshOnAction: true,
  
  // Confirmations
  confirmUninstall: true,
  confirmClearData: true
}
```

### Error Handling

All endpoints return:
- **404**: Device not found or package not found
- **500**: Operation failed (check `detail` for error message)

### PID Integration with Processes Tab

When `is_running: true` and `pid` is present, create a clickable link:
```javascript
if (package.is_running && package.pid) {
  // Navigate to: /device/{device_id}/processes?highlight={pid}
}
```

## Notes

- No caching on backend - implement client-side caching if needed
- No session management - all endpoints are stateless
- Package IDs validated with regex: `^[a-zA-Z][a-zA-Z0-9_]*(\.[a-zA-Z][a-zA-Z0-9_]*)+$`
- All paths validated, no shell injection possible

