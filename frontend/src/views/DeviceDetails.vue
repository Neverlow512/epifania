<template>
  <div class="container mx-auto p-6 max-w-7xl">
    <!-- Back Button -->
    <button 
      type="button"
      class="btn btn-sm btn-ghost text-slate-400 hover:text-white mb-4"
      @click.prevent.stop="$router.push('/')"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
      </svg>
      Back to Dashboard
    </button>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-16">
      <span class="loading loading-spinner loading-lg text-primary"></span>
    </div>

    <!-- Device Not Found -->
    <div v-else-if="!device" class="alert alert-error shadow-lg">
      <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <span>Device not found</span>
    </div>

    <!-- Device Details -->
    <div v-else>
      <!-- Device Header Card -->
      <div class="card bg-neutral-900/60 backdrop-blur-sm shadow-2xl border border-primary/20 mb-6">
        <div class="card-body">
          <div class="flex items-center gap-4">
            <div class="avatar placeholder">
              <div class="w-16 h-16 rounded-lg" :class="getDeviceColor(device.type)">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
              </div>
            </div>
            <div class="flex-1">
              <h2 class="text-3xl font-bold text-white mb-1">{{ device.name }}</h2>
              <p class="text-slate-400">{{ device.brand }} {{ device.model }}</p>
            </div>
            <div class="badge badge-lg" :class="getStatusBadge(device.state)">
              {{ device.state }}
            </div>
          </div>

          <!-- Device Specifications Grid -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
            <div class="stat bg-black/30 rounded-lg p-4">
              <div class="stat-title text-slate-400 text-xs">Serial</div>
              <div class="stat-value text-white text-sm font-mono">{{ device.serial }}</div>
            </div>
            <div class="stat bg-black/30 rounded-lg p-4">
              <div class="stat-title text-slate-400 text-xs">Android Version</div>
              <div class="stat-value text-white text-sm">{{ device.android_version }}</div>
              <div class="stat-desc text-slate-500 text-xs">SDK {{ device.sdk_version }}</div>
            </div>
            <div class="stat bg-black/30 rounded-lg p-4">
              <div class="stat-title text-slate-400 text-xs">Architecture</div>
              <div class="stat-value text-white text-sm font-mono">{{ device.architecture }}</div>
            </div>
            <div class="stat bg-black/30 rounded-lg p-4">
              <div class="stat-title text-slate-400 text-xs">Root Access</div>
              <div class="stat-value text-sm" :class="device.has_root ? 'text-green-400' : 'text-red-400'">
                {{ device.has_root ? 'Available' : 'Not Available' }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Connection Status -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div class="card bg-neutral-900/60 backdrop-blur-sm shadow-xl border border-primary/20">
          <div class="card-body">
            <h3 class="card-title text-white mb-4">Connection Status</h3>
            <div class="space-y-3">
              <div class="flex items-center justify-between">
                <span class="text-slate-400">ADB Connection</span>
                <div class="flex items-center gap-2">
                  <div class="w-2 h-2 rounded-full" :class="adbConnected ? 'bg-green-500 status-indicator' : 'bg-red-500'"></div>
                  <span :class="adbConnected ? 'text-green-400' : 'text-red-400'">
                    {{ adbConnected ? 'Connected' : 'Disconnected' }}
                  </span>
                </div>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-slate-400">Frida Connection</span>
                <div class="flex items-center gap-2">
                  <div class="w-2 h-2 rounded-full" :class="device.frida_available ? 'bg-green-500 status-indicator' : 'bg-red-500'"></div>
                  <span :class="device.frida_available ? 'text-green-400' : 'text-red-400'">
                    {{ device.frida_available ? 'Available' : 'Not Available' }}
                  </span>
                </div>
              </div>
            </div>
            <button 
              type="button"
              class="btn btn-sm btn-outline btn-primary mt-4 w-full"
              @click.prevent.stop="reconnectDevice"
              :disabled="reconnecting"
            >
              <span v-if="reconnecting" class="loading loading-spinner loading-xs"></span>
              {{ reconnecting ? 'Reconnecting...' : 'Reconnect Device' }}
            </button>
          </div>
        </div>

        <!-- Frida Server Status -->
        <div class="card bg-neutral-900/60 backdrop-blur-sm shadow-xl border border-primary/20">
          <div class="card-body">
            <h3 class="card-title text-white mb-4">Frida Server Status</h3>
            <div class="space-y-3">
              <div class="flex items-center justify-between">
                <span class="text-slate-400">Installed Version</span>
                <span class="text-white font-mono text-sm">
                  {{ device.frida_server_version || 'Not Installed' }}
                </span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-slate-400">Server Process</span>
                <div class="flex items-center gap-2">
                  <div class="w-2 h-2 rounded-full" :class="device.frida_server_running ? 'bg-green-500 status-indicator' : 'bg-gray-500'"></div>
                  <span :class="device.frida_server_running ? 'text-green-400' : 'text-gray-400'">
                    {{ device.frida_server_running ? 'Running' : 'Stopped' }}
                  </span>
                </div>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-slate-400">Frida Connection</span>
                <div class="flex items-center gap-2">
                  <div class="w-2 h-2 rounded-full" :class="fridaConnected ? 'bg-green-500 status-indicator' : testingConnection ? 'bg-yellow-500 animate-pulse' : 'bg-gray-500'"></div>
                  <span :class="fridaConnected ? 'text-green-400' : testingConnection ? 'text-yellow-400' : 'text-gray-400'">
                    {{ fridaConnected ? 'Connected' : testingConnection ? 'Testing...' : 'Not Connected' }}
                  </span>
                </div>
              </div>
              <div v-if="lastConnectionTest" class="text-xs text-slate-500">
                Last checked: {{ lastConnectionTest }}
              </div>
            </div>
            <button 
              type="button"
              class="btn btn-sm btn-outline btn-primary mt-4 w-full"
              @click.prevent.stop="refreshStatus"
              :disabled="refreshing"
            >
              <svg v-if="!refreshing" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              <span v-if="refreshing" class="loading loading-spinner loading-xs"></span>
              {{ refreshing ? 'Refreshing...' : 'Refresh Status' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Frida Server Management -->
      <div class="card bg-neutral-900/60 backdrop-blur-sm shadow-xl border border-primary/20 mb-6">
        <div class="card-body">
          <h3 class="card-title text-white mb-4">Frida Server Management</h3>
          
          <!-- Install Section -->
          <div class="mb-6">
            <h4 class="text-lg font-semibold text-white mb-3">Install Frida Server Auto</h4>
            <div class="bg-blue-900/20 border border-blue-500/30 rounded-lg p-4 mb-4">
              <div class="flex items-start gap-3">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-blue-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div class="text-sm text-blue-200">
                  <p class="font-medium mb-1">Automatic Configuration</p>
                  <p class="text-blue-300/90">
                    The system will automatically select the appropriate Frida server binary based on your device's architecture, platform, and dependencies. The newest compatible version will be downloaded, deployed to the device, and started with optimal settings.
                  </p>
                </div>
              </div>
            </div>

            <div v-if="device" class="space-y-3 mb-4">
              <div class="bg-black/30 rounded-lg p-4 border border-primary/20">
                <div class="text-xs text-slate-400 uppercase tracking-wider mb-3">Download Configuration</div>
                
                <div class="space-y-2">
                  <div class="flex items-center justify-between text-sm">
                    <span class="text-slate-400">Frida Version:</span>
                    <code class="text-primary font-mono font-semibold">{{ autoFridaVersion || 'Loading...' }}</code>
                  </div>
                  
                  <div class="flex items-center justify-between text-sm">
                    <span class="text-slate-400">Platform:</span>
                    <code class="text-white font-mono">Android</code>
                  </div>
                  
                  <div class="flex items-center justify-between text-sm">
                    <span class="text-slate-400">Device Architecture:</span>
                    <code class="text-white font-mono">{{ device.architecture }}</code>
                  </div>
                  
                  <div class="flex items-center justify-between text-sm">
                    <span class="text-slate-400">Frida Architecture:</span>
                    <code class="text-green-400 font-mono font-semibold">{{ getMappedArchitecture(device.architecture) }}</code>
                  </div>
                  
                  <div class="divider my-2"></div>
                  
                  <div class="flex items-start justify-between text-sm">
                    <span class="text-slate-400">Download URL:</span>
                    <code class="text-blue-400 font-mono text-right ml-2 break-all text-xs">{{ getFridaDownloadUrl() }}</code>
                  </div>
                  
                  <div class="flex items-start justify-between text-sm">
                    <span class="text-slate-400">Cache Path:</span>
                    <code class="text-slate-300 font-mono text-right ml-2 break-all text-xs">{{ getFridaBinaryPath() }}</code>
                  </div>
                  
                  <div class="flex items-start justify-between text-sm">
                    <span class="text-slate-400">Device Path:</span>
                    <code class="text-yellow-400 font-mono text-right ml-2 break-all">/data/local/tmp/frida-server</code>
                  </div>
                </div>
              </div>
            </div>

            <button 
              type="button"
              class="btn btn-primary gap-2 w-full"
              @click.prevent.stop="installFridaAuto"
              :disabled="installing || !autoFridaVersion"
            >
              <svg v-if="!installing" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              <span v-if="installing" class="loading loading-spinner loading-sm"></span>
              {{ installing ? 'Installing...' : `Install Frida ${autoFridaVersion || 'Server'}` }}
            </button>
          </div>

          <div class="divider"></div>

          <!-- Push Cached Server -->
          <div class="mb-6">
            <h4 class="text-lg font-semibold text-white mb-3">Push Cached Server (Custom)</h4>
            <p class="text-sm text-slate-400 mb-4">
              Push a previously downloaded custom Frida server binary to the device without re-downloading. Use this for custom versions that were cached from the Frida dropdown menu.
            </p>
            <div class="flex gap-2">
              <select 
                v-model="selectedCachedVersion" 
                class="select select-bordered bg-neutral-900 border-primary/30 focus:border-primary text-white flex-1"
                @focus="loadCachedVersions"
              >
                <option value="" disabled>Select cached version</option>
                <option v-for="(architectures, version) in cachedVersions" :key="version" :value="version">
                  {{ version }} ({{ architectures.join(', ') }})
                </option>
              </select>
              <button 
                type="button"
                class="btn btn-primary"
                @click.prevent.stop="pushCachedServer"
                :disabled="pushing || !selectedCachedVersion"
              >
                <span v-if="pushing" class="loading loading-spinner loading-sm"></span>
                {{ pushing ? 'Pushing...' : 'Push to Device' }}
              </button>
            </div>
          </div>

          <div class="divider"></div>

          <!-- Server Controls -->
          <div>
            <h4 class="text-lg font-semibold text-white mb-3">Server Controls</h4>
            <p class="text-sm text-slate-400 mb-4">
              Control the Frida server process on the device. Start, stop, or restart as needed.
            </p>
            <div class="flex gap-2 flex-wrap">
              <button 
                type="button"
                class="btn btn-success gap-2"
                @click.prevent.stop="startFrida"
                :disabled="starting || (device && device.frida_server_running)"
              >
                <svg v-if="!starting" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span v-if="starting" class="loading loading-spinner loading-sm"></span>
                {{ starting ? 'Starting...' : 'Start Server' }}
              </button>
              <button 
                type="button"
                class="btn btn-error gap-2"
                @click.prevent.stop="stopFrida"
                :disabled="stopping || (device && !device.frida_server_running)"
              >
                <svg v-if="!stopping" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
                </svg>
                <span v-if="stopping" class="loading loading-spinner loading-sm"></span>
                {{ stopping ? 'Stopping...' : 'Stop Server' }}
              </button>
              <button 
                type="button"
                class="btn btn-warning gap-2"
                @click.prevent.stop="restartFrida"
                :disabled="restarting"
              >
                <svg v-if="!restarting" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                <span v-if="restarting" class="loading loading-spinner loading-sm"></span>
                {{ restarting ? 'Restarting...' : 'Restart Server' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Frida Server Discovery & Cleanup -->
      <div class="card bg-neutral-900/60 backdrop-blur-sm shadow-xl border border-primary/20 mb-6">
        <div class="card-body">
          <div class="flex items-center justify-between mb-4">
            <h3 class="card-title text-white">Frida Server Discovery</h3>
            <button 
              type="button"
              class="btn btn-sm btn-outline btn-primary"
              @click.prevent.stop="discoverServers"
              :disabled="discovering"
            >
              <svg v-if="!discovering" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <span v-if="discovering" class="loading loading-spinner loading-xs"></span>
              {{ discovering ? 'Scanning...' : 'Scan Device' }}
            </button>
          </div>

          <div v-if="discoveredServers.length === 0 && !discovering" class="text-center py-8 text-slate-400">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto mb-2 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p>No Frida servers discovered yet</p>
            <p class="text-sm mt-1">Click "Scan Device" to search for servers</p>
          </div>

          <div v-else-if="discoveredServers.length > 0" class="space-y-3">
            <div 
              v-for="server in discoveredServers" 
              :key="server.path"
              class="flex items-center gap-3 p-3 bg-black/30 rounded-lg border"
              :class="server.path === '/data/local/tmp/frida-server' ? 'border-primary/50' : 'border-neutral-700'"
            >
              <input 
                type="checkbox" 
                v-model="server.selected"
                class="checkbox checkbox-sm checkbox-primary"
              />
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 flex-wrap">
                  <code class="text-sm text-white font-mono break-all">{{ server.path }}</code>
                  <span v-if="server.path === '/data/local/tmp/frida-server'" class="badge badge-xs badge-primary">Standard</span>
                  <span v-if="server.is_executable" class="badge badge-xs badge-success">✓ Executable</span>
                  <span v-else class="badge badge-xs badge-error">✗ Not Executable</span>
                </div>
                <div class="flex items-center gap-3 mt-2 text-xs flex-wrap">
                  <span class="text-slate-400">
                    <span class="text-slate-500">Permissions:</span> 
                    <code class="text-primary ml-1">{{ server.permissions }}</code>
                  </span>
                  <span class="text-slate-400">
                    <span class="text-slate-500">Size:</span> 
                    <span class="text-white ml-1">{{ formatSize(server.size) }}</span>
                  </span>
                  <span v-if="server.version" class="text-slate-400">
                    <span class="text-slate-500">Version:</span> 
                    <code class="text-green-400 ml-1">{{ server.version }}</code>
                  </span>
                  <span v-else class="text-slate-400">
                    <span class="text-slate-500">Version:</span> 
                    <span class="text-red-400 ml-1">Unable to detect</span>
                  </span>
                </div>
              </div>
            </div>

            <div class="flex gap-2 mt-4">
              <button 
                type="button"
                class="btn btn-sm btn-error"
                @click.prevent.stop="showCleanupConfirmation"
                :disabled="!hasSelectedServers || cleaning"
              >
                <svg v-if="!cleaning" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                <span v-if="cleaning" class="loading loading-spinner loading-xs"></span>
                {{ cleaning ? 'Cleaning...' : 'Remove Selected' }}
              </button>
              <button 
                type="button"
                class="btn btn-sm btn-ghost"
                @click.prevent.stop="selectAllServers"
              >
                Select All
              </button>
              <button 
                type="button"
                class="btn btn-sm btn-ghost"
                @click.prevent.stop="deselectAllServers"
              >
                Deselect All
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Permission Management -->
      <div class="card bg-neutral-900/60 backdrop-blur-sm shadow-xl border border-primary/20 mb-6">
        <div class="card-body">
          <h3 class="card-title text-white mb-4">Permission Management</h3>
          <p class="text-sm text-slate-400 mb-4">
            Manage executable permissions for Frida servers on the device. Servers must have executable permissions to run.
          </p>
          
          <div class="space-y-3">
            <div class="flex items-center justify-between p-4 bg-black/30 rounded-lg border" :class="permissionStatus.is_executable ? 'border-green-500/30' : 'border-red-500/30'">
              <div class="flex items-center gap-3">
                <div v-if="permissionStatus.is_executable" class="w-10 h-10 rounded-full bg-green-500/20 flex items-center justify-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div v-else class="w-10 h-10 rounded-full bg-red-500/20 flex items-center justify-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
                <div class="flex-1 min-w-0">
                  <div class="text-white font-medium font-mono text-sm break-all">/data/local/tmp/frida-server</div>
                  <div class="text-sm text-slate-400 mt-1">
                    <span v-if="permissionStatus.exists">
                      Permissions: <code class="text-primary">{{ permissionStatus.permissions }}</code>
                      <span v-if="permissionStatus.is_executable" class="ml-2 text-green-400">✓ Executable</span>
                      <span v-else class="ml-2 text-red-400">✗ Not Executable</span>
                    </span>
                    <span v-else class="text-red-400">File does not exist</span>
                  </div>
                </div>
              </div>
              <button 
                type="button"
                class="btn btn-sm btn-primary flex-shrink-0"
                @click.prevent.stop="fixPermissions"
                :disabled="fixingPermissions || !permissionStatus.exists || permissionStatus.is_executable"
              >
                <svg v-if="!fixingPermissions" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                </svg>
                <span v-if="fixingPermissions" class="loading loading-spinner loading-xs"></span>
                {{ fixingPermissions ? 'Fixing...' : permissionStatus.is_executable ? 'Executable' : 'Fix Permissions' }}
              </button>
            </div>

            <div v-if="discoveredServers.filter(s => s.path !== '/data/local/tmp/frida-server').length > 0" class="mt-4">
              <div class="text-xs text-slate-400 uppercase tracking-wider mb-2">Other Discovered Servers</div>
              <div 
                v-for="server in discoveredServers.filter(s => s.path !== '/data/local/tmp/frida-server')" 
                :key="server.path"
                class="flex items-center justify-between p-3 bg-black/30 rounded-lg border mb-2"
                :class="server.is_executable ? 'border-green-500/30' : 'border-red-500/30'"
              >
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2 flex-wrap mb-1">
                    <code class="text-sm text-white font-mono break-all">{{ server.path }}</code>
                    <span v-if="server.is_executable" class="badge badge-xs badge-success">✓ Executable</span>
                    <span v-else class="badge badge-xs badge-error">✗ Not Executable</span>
                  </div>
                  <div class="text-xs text-slate-400 flex items-center gap-3 flex-wrap">
                    <span><code class="text-primary">{{ server.permissions }}</code></span>
                    <span>{{ formatSize(server.size) }}</span>
                    <span v-if="server.version" class="text-green-400">v{{ server.version }}</span>
                    <span v-else class="text-red-400">Version unknown</span>
                  </div>
                </div>
                <button 
                  v-if="!server.is_executable"
                  type="button"
                  class="btn btn-xs btn-primary flex-shrink-0 ml-2"
                  @click.prevent.stop="fixServerPermissions(server.path)"
                  :disabled="fixingPermissions"
                >
                  Fix
                </button>
                <span v-else class="badge badge-success badge-sm flex-shrink-0 ml-2">Ready</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ADB Diagnostics -->
      <div class="card bg-neutral-900/60 backdrop-blur-sm shadow-xl border border-primary/20 mb-6">
        <div class="card-body">
          <div class="flex items-center justify-between mb-4">
            <h3 class="card-title text-white">ADB Diagnostics</h3>
            <button 
              type="button"
              class="btn btn-sm btn-outline btn-primary"
              @click.prevent.stop="runDiagnostics"
              :disabled="runningDiagnostics"
            >
              <svg v-if="!runningDiagnostics" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
              <span v-if="runningDiagnostics" class="loading loading-spinner loading-xs"></span>
              {{ runningDiagnostics ? 'Running Tests...' : 'Run Tests' }}
            </button>
          </div>

          <div v-if="diagnosticResults" class="space-y-2">
            <div 
              v-for="test in diagnosticResults.tests" 
              :key="test.name"
              class="collapse collapse-arrow bg-black/30 border"
              :class="{
                'border-green-500/30': test.status === 'pass',
                'border-yellow-500/30': test.status === 'warning',
                'border-red-500/30': test.status === 'fail'
              }"
            >
              <input type="checkbox" />
              <div class="collapse-title flex items-center gap-3">
                <svg v-if="test.status === 'pass'" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <svg v-else-if="test.status === 'warning'" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div class="flex-1">
                  <div class="font-medium text-white">{{ test.name }}</div>
                  <div class="text-xs text-slate-400">{{ test.message }}</div>
                </div>
              </div>
              <div class="collapse-content">
                <div class="text-sm text-slate-300 mt-2">
                  <p class="mb-2">{{ test.description }}</p>
                  <div v-if="Object.keys(test.details).length > 0" class="bg-black/50 p-3 rounded">
                    <div v-for="(value, key) in test.details" :key="key" class="mb-1">
                      <span class="text-slate-400">{{ key }}:</span>
                      <span class="text-white ml-2">{{ value }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="diagnosticResults.summary" class="mt-4 p-4 bg-black/30 rounded-lg">
              <div class="flex items-center justify-between">
                <span class="text-white font-medium">Overall Status</span>
                <div class="flex items-center gap-2">
                  <span class="text-green-400">{{ diagnosticResults.summary.passed }} passed</span>
                  <span class="text-slate-500">•</span>
                  <span class="text-red-400">{{ diagnosticResults.summary.failed }} failed</span>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="text-center py-8 text-slate-400">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto mb-2 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            <p>No diagnostic results yet</p>
            <p class="text-sm mt-1">Click "Run Tests" to check device status</p>
          </div>
        </div>
      </div>

      <!-- Cleanup Confirmation Modal -->
      <div v-if="showCleanupModal" class="modal modal-open">
        <div class="modal-box bg-neutral-900 border border-primary/30">
          <h3 class="font-bold text-lg text-white mb-4">Confirm Cleanup</h3>
          <p class="text-slate-300 mb-4">
            Are you sure you want to remove {{ selectedServerPaths.length }} Frida server(s)?
          </p>
          <div class="bg-black/30 p-3 rounded mb-4 max-h-40 overflow-y-auto">
            <div v-for="path in selectedServerPaths" :key="path" class="text-sm text-slate-400 mb-1">
              <code>{{ path }}</code>
            </div>
          </div>
          <div class="modal-action">
            <button type="button" class="btn btn-ghost" @click="showCleanupModal = false">Cancel</button>
            <button type="button" class="btn btn-error" @click.prevent.stop="cleanupServers">Remove</button>
          </div>
        </div>
      </div>

      <!-- Log Viewer -->
      <LogViewer v-if="device" :device-id="device.serial" class="mb-6" />

      <!-- Placeholder Sections -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="card bg-neutral-900/40 backdrop-blur-sm shadow-xl border border-neutral-700/50">
          <div class="card-body items-center text-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-slate-600 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
            </svg>
            <h3 class="text-lg font-semibold text-slate-400">Processes</h3>
            <p class="text-sm text-slate-500">Coming soon</p>
          </div>
        </div>
        <div class="card bg-neutral-900/40 backdrop-blur-sm shadow-xl border border-neutral-700/50">
          <div class="card-body items-center text-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-slate-600 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <h3 class="text-lg font-semibold text-slate-400">Applications</h3>
            <p class="text-sm text-slate-500">Coming soon</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import LogViewer from '../components/LogViewer.vue'
import { useToast } from '../composables/useToast'

export default {
  name: 'DeviceDetails',
  components: {
    LogViewer
  },
  props: {
    selectedFridaVersion: {
      type: String,
      default: ''
    }
  },
  setup(props) {
    const route = useRoute()
    const toast = useToast()
    const device = ref(null)
    const loading = ref(true)
    const adbConnected = ref(true)
    const reconnecting = ref(false)
    const refreshing = ref(false)
    const installing = ref(false)
    const pushing = ref(false)
    const starting = ref(false)
    const stopping = ref(false)
    const restarting = ref(false)
    const cachedVersions = ref({})
    const selectedCachedVersion = ref('')
    const statusMessage = ref('')
    const statusType = ref('success')
    const autoFridaVersion = ref('')
    const autoFridaArch = ref('')
    
    // Expose selectedFridaVersion from props for template access
    const { selectedFridaVersion } = props
    
    const discovering = ref(false)
    const discoveredServers = ref([])
    const cleaning = ref(false)
    const showCleanupModal = ref(false)
    
    const permissionStatus = ref({
      exists: false,
      is_executable: false,
      permissions: null
    })
    const fixingPermissions = ref(false)
    
    const diagnosticResults = ref(null)
    const runningDiagnostics = ref(false)
    
    const fridaConnected = ref(false)
    const testingConnection = ref(false)
    const lastConnectionTest = ref('')
    
    let processCheckInterval = null
    let connectionCheckInterval = null

    const deviceId = computed(() => route.params.id)
    
    const hasSelectedServers = computed(() => {
      return discoveredServers.value.some(s => s.selected)
    })
    
    const selectedServerPaths = computed(() => {
      return discoveredServers.value.filter(s => s.selected).map(s => s.path)
    })

    const showStatus = (message, type = 'success') => {
      statusMessage.value = message
      statusType.value = type
      setTimeout(() => {
        statusMessage.value = ''
      }, 5000)
    }

    const loadDeviceDetails = async (showLoading = true) => {
      try {
        if (showLoading) {
          loading.value = true
        }
        const response = await axios.get(`http://localhost:8000/api/devices/${deviceId.value}`)
        device.value = response.data
      } catch (err) {
        console.error('Failed to load device details:', err)
        device.value = null
      } finally {
        if (showLoading) {
          loading.value = false
        }
      }
    }

    const refreshStatus = async () => {
      refreshing.value = true
      await loadDeviceDetails(false)
      refreshing.value = false
    }

    const reconnectDevice = async () => {
      try {
        reconnecting.value = true
        const response = await axios.post(`http://localhost:8000/api/devices/${deviceId.value}/connect`)
        adbConnected.value = response.data.connected
        showStatus(response.data.message, response.data.connected ? 'success' : 'error')
        await loadDeviceDetails(false)
      } catch (err) {
        showStatus('Failed to reconnect device', 'error')
      } finally {
        reconnecting.value = false
      }
    }

    const loadCachedVersions = async () => {
      if (Object.keys(cachedVersions.value).length > 0) return
      
      try {
        const response = await axios.get('http://localhost:8000/api/frida/cached')
        cachedVersions.value = response.data.cached
      } catch (err) {
        console.error('Failed to load cached versions:', err)
      }
    }

    const loadRecommendedVersion = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/api/devices/${deviceId.value}/frida/recommended`)
        autoFridaVersion.value = response.data.version
        autoFridaArch.value = response.data.architecture
        console.log(`Recommended Frida version: ${autoFridaVersion.value} for ${autoFridaArch.value}`)
      } catch (err) {
        console.error('Failed to load recommended version:', err)
        autoFridaVersion.value = 'Unable to determine'
      }
    }

    const installFridaAuto = async () => {
      if (!autoFridaVersion.value) {
        toast.error('Unable to determine compatible Frida version', 'Installation Failed')
        return
      }

      try {
        installing.value = true
        toast.info(`Installing Frida ${autoFridaVersion.value}...`, 'Frida Installation')
        const response = await axios.post(
          `http://localhost:8000/api/devices/${deviceId.value}/frida/install`,
          { version: autoFridaVersion.value }
        )
        showStatus(response.data.message, 'success')
        toast.success(response.data.message, 'Frida Installation')
        await loadDeviceDetails(false)
      } catch (err) {
        const errorMsg = err.response?.data?.detail || 'Failed to install Frida server'
        showStatus(errorMsg, 'error')
        toast.error(errorMsg, 'Installation Failed')
      } finally {
        installing.value = false
      }
    }

    const installFrida = async () => {
      if (!props.selectedFridaVersion) {
        showStatus('Please select a Frida version from the top menu', 'error')
        toast.error('Please select a Frida version from the top menu', 'Installation Failed')
        return
      }

      try {
        installing.value = true
        toast.info(`Installing Frida ${props.selectedFridaVersion}...`, 'Frida Installation')
        const response = await axios.post(
          `http://localhost:8000/api/devices/${deviceId.value}/frida/install`,
          { version: props.selectedFridaVersion }
        )
        showStatus(response.data.message, 'success')
        toast.success(response.data.message, 'Frida Installation')
        await loadDeviceDetails(false)
      } catch (err) {
        const errorMsg = err.response?.data?.detail || 'Failed to install Frida server'
        showStatus(errorMsg, 'error')
        toast.error(errorMsg, 'Installation Failed')
      } finally {
        installing.value = false
      }
    }

    const pushCachedServer = async () => {
      if (!selectedCachedVersion.value || !device.value) return

      try {
        pushing.value = true
        const architectures = cachedVersions.value[selectedCachedVersion.value]
        const fridaArch = mapArchitecture(device.value.architecture)
        
        if (!architectures.includes(fridaArch)) {
          showStatus(`No cached binary for architecture ${fridaArch}`, 'error')
          return
        }

        const response = await axios.post(
          `http://localhost:8000/api/devices/${deviceId.value}/frida/push`,
          { 
            version: selectedCachedVersion.value,
            architecture: fridaArch
          }
        )
        showStatus(response.data.message, 'success')
        await loadDeviceDetails(false)
      } catch (err) {
        showStatus(err.response?.data?.detail || 'Failed to push Frida server', 'error')
      } finally {
        pushing.value = false
      }
    }

    const startFrida = async () => {
      try {
        starting.value = true
        toast.info('Starting Frida server...', 'Frida Server')
        const response = await axios.post(`http://localhost:8000/api/devices/${deviceId.value}/frida/start`)
        showStatus(response.data.message, 'success')
        toast.success(response.data.message, 'Frida Server')
        await loadDeviceDetails(false)
      } catch (err) {
        const errorMsg = err.response?.data?.detail || 'Failed to start Frida server'
        showStatus(errorMsg, 'error')
        toast.error(errorMsg, 'Start Failed')
      } finally {
        starting.value = false
      }
    }

    const stopFrida = async () => {
      try {
        stopping.value = true
        toast.info('Stopping Frida server...', 'Frida Server')
        const response = await axios.post(`http://localhost:8000/api/devices/${deviceId.value}/frida/stop`)
        showStatus(response.data.message, 'success')
        toast.success(response.data.message, 'Frida Server')
        await loadDeviceDetails(false)
      } catch (err) {
        const errorMsg = err.response?.data?.detail || 'Failed to stop Frida server'
        showStatus(errorMsg, 'error')
        toast.error(errorMsg, 'Stop Failed')
      } finally {
        stopping.value = false
      }
    }

    const restartFrida = async () => {
      try {
        restarting.value = true
        const response = await axios.post(`http://localhost:8000/api/devices/${deviceId.value}/frida/restart`)
        showStatus(response.data.message, 'success')
        await loadDeviceDetails(false)
      } catch (err) {
        showStatus(err.response?.data?.detail || 'Failed to restart Frida server', 'error')
      } finally {
        restarting.value = false
      }
    }

    const mapArchitecture = (androidAbi) => {
      const mapping = {
        'armeabi-v7a': 'arm',
        'armeabi': 'arm',
        'arm64-v8a': 'arm64',
        'x86': 'x86',
        'x86_64': 'x86_64'
      }
      return mapping[androidAbi] || androidAbi
    }

    const getMappedArchitecture = (androidAbi) => {
      return mapArchitecture(androidAbi)
    }

    const getFridaBinaryPath = () => {
      if (!device.value || !autoFridaVersion.value) {
        return 'Loading...'
      }
      
      const arch = getMappedArchitecture(device.value.architecture)
      return `backend/frida_servers/${autoFridaVersion.value}/${arch}/frida-server`
    }

    const getFridaDownloadUrl = () => {
      if (!device.value || !autoFridaVersion.value) {
        return 'Loading...'
      }
      
      const arch = getMappedArchitecture(device.value.architecture)
      return `https://github.com/frida/frida/releases/download/${autoFridaVersion.value}/frida-server-${autoFridaVersion.value}-android-${arch}.xz`
    }

    const fixServerPermissions = async (path) => {
      try {
        fixingPermissions.value = true
        const response = await axios.post(
          `http://localhost:8000/api/devices/${deviceId.value}/frida/permissions`,
          null,
          { params: { path } }
        )
        
        toast.success(response.data.message, 'Permissions Updated')
        await checkPermissions()
        await discoverServers()
      } catch (err) {
        toast.error(err.response?.data?.detail || 'Failed to set permissions', 'Permission Error')
      } finally {
        fixingPermissions.value = false
      }
    }

    const getDeviceColor = (type) => {
      if (type === 'emulator') return 'bg-gradient-to-br from-[#7100d0] to-purple-700'
      if (type === 'physical') return 'bg-gradient-to-br from-[#7100d0] to-black'
      return 'bg-gradient-to-br from-slate-500 to-slate-600'
    }

    const getStatusBadge = (state) => {
      if (state === 'online') return 'badge-success'
      if (state === 'error') return 'badge-error'
      return 'badge-warning'
    }

    const formatSize = (size) => {
      if (!size || size === 'unknown') return 'Unknown'
      
      const bytes = parseInt(size)
      if (isNaN(bytes)) return size
      
      if (bytes < 1024) return `${bytes} B`
      if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
      if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
      return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`
    }

    const discoverServers = async () => {
      try {
        discovering.value = true
        const response = await axios.get(`http://localhost:8000/api/devices/${deviceId.value}/frida/discover`)
        discoveredServers.value = response.data.servers.map(s => ({ ...s, selected: false }))
        
        // Update permission status for standard location if found
        const standardServer = discoveredServers.value.find(s => s.path === '/data/local/tmp/frida-server')
        if (standardServer) {
          permissionStatus.value = {
            exists: true,
            is_executable: standardServer.is_executable,
            permissions: standardServer.permissions,
            path: standardServer.path
          }
        }
        
        if (discoveredServers.value.length === 0) {
          toast.info('No Frida servers found on device')
        } else {
          toast.success(`Found ${discoveredServers.value.length} Frida server(s)`)
        }
      } catch (err) {
        toast.error('Failed to discover Frida servers', 'Discovery Error')
        console.error('Discovery error:', err)
      } finally {
        discovering.value = false
      }
    }

    const selectAllServers = () => {
      discoveredServers.value.forEach(s => s.selected = true)
    }

    const deselectAllServers = () => {
      discoveredServers.value.forEach(s => s.selected = false)
    }

    const showCleanupConfirmation = () => {
      if (hasSelectedServers.value) {
        showCleanupModal.value = true
      }
    }

    const cleanupServers = async () => {
      try {
        cleaning.value = true
        showCleanupModal.value = false
        
        const response = await axios.post(
          `http://localhost:8000/api/devices/${deviceId.value}/frida/clean`,
          { paths: selectedServerPaths.value }
        )
        
        toast.success(response.data.message, 'Cleanup Complete')
        
        await discoverServers()
        await loadDeviceDetails(false)
      } catch (err) {
        toast.error(err.response?.data?.detail || 'Failed to clean Frida servers', 'Cleanup Error')
      } finally {
        cleaning.value = false
      }
    }

    const checkPermissions = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/api/devices/${deviceId.value}/frida/permissions`)
        permissionStatus.value = response.data
      } catch (err) {
        console.error('Failed to check permissions:', err)
      }
    }

    const fixPermissions = async () => {
      try {
        fixingPermissions.value = true
        const response = await axios.post(`http://localhost:8000/api/devices/${deviceId.value}/frida/permissions`)
        
        toast.success(response.data.message, 'Permissions Updated')
        await checkPermissions()
      } catch (err) {
        toast.error(err.response?.data?.detail || 'Failed to set permissions', 'Permission Error')
      } finally {
        fixingPermissions.value = false
      }
    }

    const runDiagnostics = async () => {
      try {
        runningDiagnostics.value = true
        const response = await axios.get(`http://localhost:8000/api/devices/${deviceId.value}/diagnostics/adb`)
        diagnosticResults.value = response.data
        
        const failed = response.data.tests.filter(t => t.status === 'fail')
        const warnings = response.data.tests.filter(t => t.status === 'warning')
        
        if (failed.length > 0) {
          failed.forEach(test => {
            let guidance = test.message
            if (test.details.note) {
              guidance += ` - ${test.details.note}`
            }
            toast.error(guidance, `${test.name} Failed`)
          })
        }
        
        if (warnings.length > 0) {
          warnings.forEach(test => {
            let guidance = test.message
            if (test.details.note) {
              guidance += ` - ${test.details.note}`
            }
            toast.warning(guidance, test.name)
          })
        }
        
        if (failed.length === 0 && warnings.length === 0) {
          toast.success('All diagnostic tests passed', 'Diagnostics Complete')
        }
      } catch (err) {
        toast.error('Failed to run diagnostics', 'Diagnostic Error')
        console.error('Diagnostics error:', err)
      } finally {
        runningDiagnostics.value = false
      }
    }

    const testFridaConnection = async () => {
      try {
        testingConnection.value = true
        const response = await axios.get(`http://localhost:8000/api/devices/${deviceId.value}/frida/test-connection`)
        
        fridaConnected.value = response.data.connected
        lastConnectionTest.value = new Date().toLocaleTimeString()
        
        if (!response.data.connected && device.value?.frida_server_running) {
          console.warn('Frida server running but not responding:', response.data.message)
        }
      } catch (err) {
        fridaConnected.value = false
        console.error('Connection test error:', err)
      } finally {
        testingConnection.value = false
      }
    }

    const startConnectionTracking = () => {
      processCheckInterval = setInterval(async () => {
        await loadDeviceDetails(false)
      }, 3000)
      
      connectionCheckInterval = setInterval(async () => {
        if (device.value?.frida_server_running) {
          await testFridaConnection()
        } else {
          fridaConnected.value = false
        }
      }, 10000)
    }

    const stopConnectionTracking = () => {
      if (processCheckInterval) {
        clearInterval(processCheckInterval)
        processCheckInterval = null
      }
      if (connectionCheckInterval) {
        clearInterval(connectionCheckInterval)
        connectionCheckInterval = null
      }
    }

    onMounted(async () => {
      await loadDeviceDetails()
      await loadRecommendedVersion()
      await loadCachedVersions()
      await checkPermissions()
      await discoverServers()
      
      startConnectionTracking()
      
      if (device.value?.frida_server_running) {
        await testFridaConnection()
      }
    })

    onUnmounted(() => {
      stopConnectionTracking()
    })

    return {
      device,
      loading,
      adbConnected,
      reconnecting,
      refreshing,
      installing,
      pushing,
      starting,
      stopping,
      restarting,
      cachedVersions,
      selectedCachedVersion,
      selectedFridaVersion,
      autoFridaVersion,
      autoFridaArch,
      statusMessage,
      statusType,
      discovering,
      discoveredServers,
      cleaning,
      showCleanupModal,
      hasSelectedServers,
      selectedServerPaths,
      permissionStatus,
      fixingPermissions,
      diagnosticResults,
      runningDiagnostics,
      fridaConnected,
      testingConnection,
      lastConnectionTest,
      refreshStatus,
      reconnectDevice,
      loadCachedVersions,
      loadRecommendedVersion,
      installFrida,
      installFridaAuto,
      pushCachedServer,
      startFrida,
      stopFrida,
      restartFrida,
      discoverServers,
      selectAllServers,
      deselectAllServers,
      showCleanupConfirmation,
      cleanupServers,
      checkPermissions,
      fixPermissions,
      runDiagnostics,
      testFridaConnection,
      getMappedArchitecture,
      getFridaBinaryPath,
      getFridaDownloadUrl,
      fixServerPermissions,
      formatSize,
      getDeviceColor,
      getStatusBadge
    }
  }
}
</script>

