<template>
  <div>
    <!-- Device Specifications Grid -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
      <div class="stat bg-neutral-900/60 backdrop-blur-sm rounded-lg p-4 border border-primary/20">
        <div class="stat-title text-slate-400 text-xs">Serial</div>
        <div class="stat-value text-white text-sm font-mono">{{ device.serial }}</div>
      </div>
      <div class="stat bg-neutral-900/60 backdrop-blur-sm rounded-lg p-4 border border-primary/20">
        <div class="stat-title text-slate-400 text-xs">Android Version</div>
        <div class="stat-value text-white text-sm">{{ device.android_version }}</div>
        <div class="stat-desc text-slate-500 text-xs">SDK {{ device.sdk_version }}</div>
      </div>
      <div class="stat bg-neutral-900/60 backdrop-blur-sm rounded-lg p-4 border border-primary/20">
        <div class="stat-title text-slate-400 text-xs">Architecture</div>
        <div class="stat-value text-white text-sm font-mono">{{ device.architecture }}</div>
      </div>
      <div class="stat bg-neutral-900/60 backdrop-blur-sm rounded-lg p-4 border border-primary/20">
        <div class="stat-title text-slate-400 text-xs">Root Access</div>
        <div class="stat-value text-sm" :class="device.has_root ? 'text-green-400' : 'text-red-400'">
          {{ device.has_root ? 'Available' : 'Not Available' }}
        </div>
      </div>
    </div>

    <!-- Install Frida (Auto) Details Modal -->
    <div v-if="showInstallDetailsModal" class="modal modal-open">
      <div class="modal-box bg-neutral-900 border border-primary/30 max-w-3xl">
        <h3 class="font-bold text-lg text-white mb-2">Install Frida (Auto) - Details</h3>
        <div class="bg-blue-900/20 border border-blue-500/30 rounded-lg p-3 mb-3">
          <div class="flex items-start gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-blue-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div class="text-blue-200">
              <p class="font-medium mb-1">Automatic Configuration</p>
              <p class="text-blue-300/90">
                The system selects the appropriate Frida server binary based on your device and deploys it with optimal settings.
              </p>
            </div>
          </div>
        </div>
        <div v-if="device" class="bg-black/30 rounded-lg p-3 border border-primary/20">
          <div class="text-[10px] text-slate-400 uppercase tracking-wider mb-2">Download Configuration</div>
          <div class="space-y-2">
            <div class="flex items-center justify-between text-xs">
              <span class="text-slate-400">Frida Version:</span>
              <code class="text-primary font-mono font-semibold">{{ autoFridaVersion || 'Loading...' }}</code>
            </div>
            <div class="flex items-center justify-between text-xs">
              <span class="text-slate-400">Platform:</span>
              <code class="text-white font-mono">Android</code>
            </div>
            <div class="flex items-center justify-between text-xs">
              <span class="text-slate-400">Device Architecture:</span>
              <code class="text-white font-mono">{{ device.architecture }}</code>
            </div>
            <div class="flex items-center justify-between text-xs">
              <span class="text-slate-400">Frida Architecture:</span>
              <code class="text-green-400 font-mono font-semibold">{{ getMappedArchitecture(device.architecture) }}</code>
            </div>
            <div class="divider my-2"></div>
            <div class="flex items-start justify-between text-xs">
              <span class="text-slate-400">Download URL:</span>
              <code class="text-blue-400 font-mono text-right ml-2 break-all">{{ getFridaDownloadUrl() }}</code>
            </div>
            <div class="flex items-start justify-between text-xs">
              <span class="text-slate-400">Cache Path:</span>
              <code class="text-slate-300 font-mono text-right ml-2 break-all">{{ getFridaBinaryPath() }}</code>
            </div>
            <div class="flex items-start justify-between text-xs">
              <span class="text-slate-400">Device Path:</span>
              <code class="text-yellow-400 font-mono text-right ml-2 break-all">/data/local/tmp/frida-server</code>
            </div>
          </div>
        </div>
        <div class="modal-action">
          <button type="button" class="btn btn-ghost" @click="$emit('update:showInstallDetailsModal', false)">Close</button>
        </div>
      </div>
    </div>

    <!-- Push Cached Server (Custom) Details Modal -->
    <div v-if="showPushDetailsModal" class="modal modal-open">
      <div class="modal-box bg-neutral-900 border border-primary/30 max-w-xl">
        <h3 class="font-bold text-lg text-white mb-2">Push Cached Server (Custom) - Details</h3>
        <p class="text-sm text-slate-300 mb-3">
          Push a previously downloaded Frida server binary to the device without re-downloading. Use this for custom versions cached from the Frida dropdown menu.
        </p>
        <div class="bg-black/30 rounded-lg p-3 border border-primary/20 text-xs space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-slate-400">Selected Version:</span>
            <code class="text-primary font-mono">{{ selectedCachedVersion || 'None' }}</code>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-slate-400">Device Architecture:</span>
            <code class="text-white font-mono">{{ device ? device.architecture : 'Unknown' }}</code>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-slate-400">Frida Architecture:</span>
            <code class="text-green-400 font-mono">{{ device ? getMappedArchitecture(device.architecture) : 'Unknown' }}</code>
          </div>
        </div>
        <div class="modal-action">
          <button type="button" class="btn btn-ghost" @click="$emit('update:showPushDetailsModal', false)">Close</button>
        </div>
      </div>
    </div>

    <!-- Frida Controls Details Modal -->
    <div v-if="showFridaControlsDetailsModal" class="modal modal-open">
      <div class="modal-box bg-neutral-900 border border-primary/30 max-w-md">
        <h3 class="font-bold text-lg text-white mb-2">Frida Controls - Details</h3>
        <p class="text-sm text-slate-300 mb-3">
          Start, stop, or restart the Frida server on the device. Use this widget to manage the server process quickly without shell commands.
        </p>
        <div class="modal-action">
          <button type="button" class="btn btn-ghost" @click="$emit('update:showFridaControlsDetailsModal', false)">Close</button>
        </div>
      </div>
    </div>

    <!-- Summary Row: Connection, Frida Status, Install Auto, Push Cached -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
      <div class="card card-compact bg-neutral-900/60 backdrop-blur-sm shadow-xl border border-primary/20">
        <div class="card-body">
          <h3 class="card-title text-white mb-2">Connection Status</h3>
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
            <div class="flex items-center justify-between text-sm">
              <span class="text-slate-400">ADB Diagnostics</span>
              <div class="flex items-center gap-2">
                <span class="text-white">
                  {{ diagnosticResults && diagnosticResults.summary ? diagnosticResults.summary.passed : 0 }}/{{ diagnosticResults && diagnosticResults.tests ? diagnosticResults.tests.length : 0 }}
                </span>
                <button 
                  type="button" 
                  class="btn btn-xs btn-outline btn-primary"
                  @click.prevent.stop="runDiagnostics"
                  :disabled="runningDiagnostics"
                >
                  <span v-if="runningDiagnostics" class="loading loading-spinner loading-xs"></span>
                  {{ runningDiagnostics ? 'Testing...' : 'Run' }}
                </button>
                <button 
                  type="button"
                  class="btn btn-sm btn-ghost"
                  @click.prevent.stop="$emit('update:showDiagnosticsModal', true)"
                  :disabled="!diagnosticResults"
                >
                  Details
                </button>
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
      <div class="card card-compact bg-neutral-900/60 backdrop-blur-sm shadow-xl border border-primary/20">
        <div class="card-body">
          <h3 class="card-title text-white mb-2">Frida Server Status</h3>
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
      
      <!-- Install + Push (Combined) - Compact Widget -->
      <div class="card card-compact bg-neutral-900/60 backdrop-blur-sm shadow-xl border border-primary/20">
        <div class="card-body">
          <h3 class="card-title text-white mb-2">Install Frida (Auto)</h3>
          <div class="text-xs text-slate-400">
            v{{ autoFridaVersion || 'Loading...' }} • {{ device ? getMappedArchitecture(device.architecture) : '...' }}
          </div>
          <div class="flex gap-2 mt-2">
            <button 
              type="button"
              class="btn btn-sm btn-primary flex-1"
              @click.prevent.stop="installFridaAuto"
              :disabled="installing || !autoFridaVersion"
            >
              <span v-if="installing" class="loading loading-spinner loading-xs"></span>
              {{ installing ? 'Installing...' : `Install Frida ${autoFridaVersion || ''}` }}
            </button>
            <button 
              type="button"
              class="btn btn-sm btn-ghost"
              @click.prevent.stop="$emit('update:showInstallDetailsModal', true)"
              :disabled="!autoFridaVersion"
            >
              Details
            </button>
          </div>
          <div class="border-t border-neutral-700 mt-3 pt-3">
            <div class="text-xs text-white mb-2 font-semibold">Push Cached Server (Custom)</div>
            <div class="flex gap-2">
              <select 
                v-model="selectedCachedVersionModel" 
                class="select select-sm select-bordered bg-neutral-900 border-primary/30 focus:border-primary text-white flex-1"
                @focus="loadCachedVersions"
              >
                <option value="" disabled>Select cached version</option>
                <option v-for="(architectures, version) in cachedVersions" :key="version" :value="version">
                  {{ version }} ({{ architectures.join(', ') }})
                </option>
              </select>
              <button 
                type="button"
                class="btn btn-sm btn-primary"
                @click.prevent.stop="pushCachedServer"
                :disabled="pushing || !selectedCachedVersion"
              >
                <span v-if="pushing" class="loading loading-spinner loading-xs"></span>
                {{ pushing ? 'Pushing...' : 'Push' }}
              </button>
            </div>
            <div class="flex gap-2 mt-2">
              <button 
                type="button"
                class="btn btn-sm btn-ghost"
                @click.prevent.stop="$emit('update:showPushDetailsModal', true)"
              >
                Details
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Frida Controls - Compact Widget -->
      <div class="card card-compact bg-neutral-900/60 backdrop-blur-sm shadow-xl border border-primary/20">
        <div class="card-body">
          <h3 class="card-title text-white mb-2">Frida Controls</h3>
          <div class="flex flex-wrap gap-2">
            <button 
              type="button"
              class="btn btn-sm btn-success gap-2"
              @click.prevent.stop="startFrida"
              :disabled="starting || (device && device.frida_server_running)"
            >
              <span v-if="starting" class="loading loading-spinner loading-xs"></span>
              <span v-else>Start</span>
            </button>
            <button 
              type="button"
              class="btn btn-sm btn-error gap-2"
              @click.prevent.stop="stopFrida"
              :disabled="stopping || (device && !device.frida_server_running)"
            >
              <span v-if="stopping" class="loading loading-spinner loading-xs"></span>
              <span v-else>Stop</span>
            </button>
            <button 
              type="button"
              class="btn btn-sm btn-warning gap-2"
              @click.prevent.stop="restartFrida"
              :disabled="restarting"
            >
              <span v-if="restarting" class="loading loading-spinner loading-xs"></span>
              <span v-else>Restart</span>
            </button>
          </div>
          <div class="flex gap-2 mt-2">
            <button 
              type="button"
              class="btn btn-sm btn-ghost"
              @click.prevent.stop="$emit('update:showFridaControlsDetailsModal', true)"
            >
              Details
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Discovery and Permissions (Compact, side-by-side) -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
      <!-- Frida Server Discovery & Cleanup -->
      <div class="card card-compact bg-neutral-900/60 backdrop-blur-sm shadow-xl border border-primary/20">
        <div class="card-body py-4">
          <div class="flex items-center justify-between mb-2">
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
          <div class="text-sm text-slate-300 font-semibold">
            Servers: {{ discoveredServers.length }}
            <span class="mx-1 text-slate-600">•</span>
            Standard:
            <span :class="permissionStatus.exists ? (permissionStatus.is_executable ? 'text-green-400' : 'text-red-400') : 'text-slate-500'">
              {{ permissionStatus.exists ? (permissionStatus.is_executable ? 'Executable' : 'Not Executable') : 'Not Found' }}
            </span>
          </div>
          <div class="collapse collapse-arrow mt-2">
            <input type="checkbox" />
            <div class="collapse-title text-sm">Details</div>
            <div class="collapse-content">
              <div v-if="discoveredServers.length === 0 && !discovering" class="text-center py-6 text-slate-400">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 mx-auto mb-2 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p>No Frida servers discovered yet</p>
              </div>
              <div v-else-if="discoveredServers.length > 0" class="space-y-2">
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
            <div class="flex gap-2 mt-2">
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
        </div>
      </div>
      
      <!-- Permission Management -->
      <div class="card card-compact bg-neutral-900/60 backdrop-blur-sm shadow-xl border border-primary/20">
        <div class="card-body py-4">
          <div class="flex items-start justify-between mb-2">
            <div>
              <h3 class="card-title text-white">Permission Management</h3>
              <p class="text-sm text-slate-300 font-semibold mt-1">
                Manage and fix executable permissions for Frida servers discovered on this device.
              </p>
            </div>
            <div
              class="badge badge-sm"
              :class="permissionStatus.exists ? (permissionStatus.is_executable ? 'badge-success' : 'badge-error') : 'badge-ghost text-slate-400'"
            >
              {{ permissionStatus.exists ? (permissionStatus.is_executable ? 'Executable' : 'Not Executable') : 'Not Found' }}
            </div>
          </div>
          <div class="collapse collapse-arrow mt-3">
            <input type="checkbox" />
            <div class="collapse-title text-sm">Details</div>
            <div class="collapse-content">
              <div class="space-y-3">
                <div class="flex items-center justify-between p-3 bg-black/30 rounded-lg border" :class="permissionStatus.is_executable ? 'border-green-500/30' : 'border-red-500/30'">
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
                <div 
                  v-if="discoveredServers.filter(s => s.path !== '/data/local/tmp/frida-server').length > 0" 
                  class="collapse collapse-arrow mt-2"
                >
                  <input type="checkbox" />
                  <div class="collapse-title text-sm">Other Discovered Servers</div>
                  <div class="collapse-content">
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
          </div>
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
          <button 
            type="button" 
            class="btn btn-ghost" 
            @click="$emit('update:showCleanupModal', false)"
          >
            Cancel
          </button>
          <button 
            type="button" 
            class="btn btn-error" 
            @click.prevent.stop="cleanupServers"
          >
            Remove
          </button>
        </div>
      </div>
    </div>

    <!-- Diagnostics Details Modal -->
    <div v-if="showDiagnosticsModal" class="modal modal-open">
      <div class="modal-box bg-neutral-900 border border-primary/30 max-w-3xl">
        <h3 class="font-bold text-lg text-white mb-2">ADB Diagnostics</h3>
        <div class="text-sm text-slate-400 mb-3">
          <template v-if="diagnosticResults && diagnosticResults.summary">
            {{ diagnosticResults.summary.passed }} passed • {{ diagnosticResults.summary.failed }} failed
          </template>
          <template v-else>
            No diagnostic results yet
          </template>
        </div>
        <div class="max-h-[60vh] overflow-y-auto pr-1">
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
          </div>
          <div v-else class="text-center py-6 text-slate-400">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 mx-auto mb-2 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            <p>No diagnostic results yet</p>
          </div>
        </div>
        <div class="modal-action">
          <button 
            type="button" 
            class="btn btn-ghost" 
            @click="$emit('update:showDiagnosticsModal', false)"
          >
            Close
          </button>
        </div>
      </div>
    </div>

    <!-- Log Viewer -->
    <LogViewer v-if="device" :device-id="device.serial" class="mb-6" />
  </div>
</template>

<script>
import LogViewer from '../../../components/LogViewer.vue'

export default {
  name: 'DeviceTab',
  components: {
    LogViewer
  },
  props: {
    device: {
      type: Object,
      required: true
    },
    adbConnected: Boolean,
    reconnecting: Boolean,
    refreshing: Boolean,
    installing: Boolean,
    pushing: Boolean,
    starting: Boolean,
    stopping: Boolean,
    restarting: Boolean,
    cachedVersions: Object,
    selectedCachedVersion: String,
    autoFridaVersion: String,
    discovering: Boolean,
    discoveredServers: Array,
    cleaning: Boolean,
    showCleanupModal: Boolean,
    showDiagnosticsModal: Boolean,
    showInstallDetailsModal: Boolean,
    showPushDetailsModal: Boolean,
    showFridaControlsDetailsModal: Boolean,
    hasSelectedServers: Boolean,
    selectedServerPaths: Array,
    permissionStatus: Object,
    fixingPermissions: Boolean,
    diagnosticResults: Object,
    runningDiagnostics: Boolean,
    fridaConnected: Boolean,
    testingConnection: Boolean,
    lastConnectionTest: String
  },
  emits: [
    'reconnect-device',
    'refresh-status',
    'load-cached-versions',
    'install-frida-auto',
    'push-cached-server',
    'start-frida',
    'stop-frida',
    'restart-frida',
    'discover-servers',
    'show-cleanup-confirmation',
    'cleanup-servers',
    'select-all-servers',
    'deselect-all-servers',
    'fix-permissions',
    'fix-server-permissions',
    'run-diagnostics',
    'update:selectedCachedVersion',
    'update:showCleanupModal',
    'update:showDiagnosticsModal',
    'update:showInstallDetailsModal',
    'update:showPushDetailsModal',
    'update:showFridaControlsDetailsModal'
  ],
  computed: {
    selectedCachedVersionModel: {
      get() {
        return this.selectedCachedVersion
      },
      set(value) {
        this.$emit('update:selectedCachedVersion', value)
      }
    }
  },
  methods: {
    reconnectDevice() {
      this.$emit('reconnect-device')
    },
    refreshStatus() {
      this.$emit('refresh-status')
    },
    loadCachedVersions() {
      this.$emit('load-cached-versions')
    },
    installFridaAuto() {
      this.$emit('install-frida-auto')
    },
    pushCachedServer() {
      this.$emit('push-cached-server')
    },
    startFrida() {
      this.$emit('start-frida')
    },
    stopFrida() {
      this.$emit('stop-frida')
    },
    restartFrida() {
      this.$emit('restart-frida')
    },
    discoverServers() {
      this.$emit('discover-servers')
    },
    showCleanupConfirmation() {
      this.$emit('show-cleanup-confirmation')
    },
    cleanupServers() {
      this.$emit('cleanup-servers')
    },
    selectAllServers() {
      this.$emit('select-all-servers')
    },
    deselectAllServers() {
      this.$emit('deselect-all-servers')
    },
    fixPermissions() {
      this.$emit('fix-permissions')
    },
    fixServerPermissions(path) {
      this.$emit('fix-server-permissions', path)
    },
    runDiagnostics() {
      this.$emit('run-diagnostics')
    },
    getMappedArchitecture(arch) {
      const mapping = {
        'armeabi-v7a': 'arm',
        'armeabi': 'arm',
        'arm64-v8a': 'arm64',
        'x86': 'x86',
        'x86_64': 'x86_64'
      }
      return mapping[arch] || arch
    },
    getFridaBinaryPath() {
      if (!this.device || !this.autoFridaVersion) {
        return 'Loading...'
      }
      const arch = this.getMappedArchitecture(this.device.architecture)
      return `backend/frida_servers/${this.autoFridaVersion}/${arch}/frida-server`
    },
    getFridaDownloadUrl() {
      if (!this.device || !this.autoFridaVersion) {
        return 'Loading...'
      }
      const arch = this.getMappedArchitecture(this.device.architecture)
      return `https://github.com/frida/frida/releases/download/${this.autoFridaVersion}/frida-server-${this.autoFridaVersion}-android-${arch}.xz`
    },
    formatSize(size) {
      if (!size || size === 'unknown') return 'Unknown'
      const bytes = parseInt(size)
      if (isNaN(bytes)) return size
      if (bytes < 1024) return `${bytes} B`
      if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
      if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
      return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`
    }
  }
}
</script>

