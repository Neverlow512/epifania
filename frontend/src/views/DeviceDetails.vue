<template>
  <div class="container mx-auto p-6 max-w-7xl">
    <!-- Back Button -->
    <button 
      class="btn btn-sm btn-ghost text-slate-400 hover:text-white mb-4"
      @click="$router.push('/')"
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
              class="btn btn-sm btn-outline btn-primary mt-4 w-full"
              @click="reconnectDevice"
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
                <span class="text-slate-400">Server Status</span>
                <div class="flex items-center gap-2">
                  <div class="w-2 h-2 rounded-full" :class="device.frida_server_running ? 'bg-green-500 status-indicator' : 'bg-gray-500'"></div>
                  <span :class="device.frida_server_running ? 'text-green-400' : 'text-gray-400'">
                    {{ device.frida_server_running ? 'Running' : 'Stopped' }}
                  </span>
                </div>
              </div>
            </div>
            <button 
              class="btn btn-sm btn-outline btn-primary mt-4 w-full"
              @click="refreshStatus"
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
            <h4 class="text-lg font-semibold text-white mb-3">Install Frida Server</h4>
            <p class="text-sm text-slate-400 mb-4">
              Install the selected Frida version from the top menu. The server will be downloaded, pushed to the device, and started automatically.
            </p>
            <button 
              class="btn btn-primary gap-2"
              @click="installFrida"
              :disabled="installing || !selectedFridaVersion"
            >
              <svg v-if="!installing" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              <span v-if="installing" class="loading loading-spinner loading-sm"></span>
              {{ installing ? 'Installing...' : `Install Frida ${selectedFridaVersion || 'Server'}` }}
            </button>
          </div>

          <div class="divider"></div>

          <!-- Push Cached Server -->
          <div class="mb-6">
            <h4 class="text-lg font-semibold text-white mb-3">Push Cached Server</h4>
            <p class="text-sm text-slate-400 mb-4">
              Push a previously downloaded Frida server binary to the device without re-downloading.
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
                class="btn btn-primary"
                @click="pushCachedServer"
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
                class="btn btn-success gap-2"
                @click="startFrida"
                :disabled="starting || device.frida_server_running"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span v-if="starting" class="loading loading-spinner loading-sm"></span>
                {{ starting ? 'Starting...' : 'Start Server' }}
              </button>
              <button 
                class="btn btn-error gap-2"
                @click="stopFrida"
                :disabled="stopping || !device.frida_server_running"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
                </svg>
                <span v-if="stopping" class="loading loading-spinner loading-sm"></span>
                {{ stopping ? 'Stopping...' : 'Stop Server' }}
              </button>
              <button 
                class="btn btn-warning gap-2"
                @click="restartFrida"
                :disabled="restarting"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                <span v-if="restarting" class="loading loading-spinner loading-sm"></span>
                {{ restarting ? 'Restarting...' : 'Restart Server' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Status Messages -->
      <div v-if="statusMessage" class="alert shadow-lg mb-6" :class="statusType === 'success' ? 'alert-success' : 'alert-error'">
        <svg v-if="statusType === 'success'" xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ statusMessage }}</span>
      </div>

      <!-- Placeholder Sections -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="card bg-neutral-900/40 backdrop-blur-sm shadow-xl border border-neutral-700/50">
          <div class="card-body items-center text-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-slate-600 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 class="text-lg font-semibold text-slate-400">Logs</h3>
            <p class="text-sm text-slate-500">Coming soon</p>
          </div>
        </div>
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
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

export default {
  name: 'DeviceDetails',
  props: {
    selectedFridaVersion: {
      type: String,
      default: ''
    }
  },
  setup(props) {
    const route = useRoute()
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

    const deviceId = computed(() => route.params.id)

    const showStatus = (message, type = 'success') => {
      statusMessage.value = message
      statusType.value = type
      setTimeout(() => {
        statusMessage.value = ''
      }, 5000)
    }

    const loadDeviceDetails = async () => {
      try {
        loading.value = true
        const response = await axios.get(`http://localhost:8000/api/devices/${deviceId.value}`)
        device.value = response.data
      } catch (err) {
        console.error('Failed to load device details:', err)
        device.value = null
      } finally {
        loading.value = false
      }
    }

    const refreshStatus = async () => {
      refreshing.value = true
      await loadDeviceDetails()
      refreshing.value = false
    }

    const reconnectDevice = async () => {
      try {
        reconnecting.value = true
        const response = await axios.post(`http://localhost:8000/api/devices/${deviceId.value}/connect`)
        adbConnected.value = response.data.connected
        showStatus(response.data.message, response.data.connected ? 'success' : 'error')
        await loadDeviceDetails()
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

    const installFrida = async () => {
      if (!props.selectedFridaVersion) {
        showStatus('Please select a Frida version from the top menu', 'error')
        return
      }

      try {
        installing.value = true
        const response = await axios.post(
          `http://localhost:8000/api/devices/${deviceId.value}/frida/install`,
          { version: props.selectedFridaVersion }
        )
        showStatus(response.data.message, 'success')
        await loadDeviceDetails()
      } catch (err) {
        showStatus(err.response?.data?.detail || 'Failed to install Frida server', 'error')
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
        await loadDeviceDetails()
      } catch (err) {
        showStatus(err.response?.data?.detail || 'Failed to push Frida server', 'error')
      } finally {
        pushing.value = false
      }
    }

    const startFrida = async () => {
      try {
        starting.value = true
        const response = await axios.post(`http://localhost:8000/api/devices/${deviceId.value}/frida/start`)
        showStatus(response.data.message, 'success')
        await loadDeviceDetails()
      } catch (err) {
        showStatus(err.response?.data?.detail || 'Failed to start Frida server', 'error')
      } finally {
        starting.value = false
      }
    }

    const stopFrida = async () => {
      try {
        stopping.value = true
        const response = await axios.post(`http://localhost:8000/api/devices/${deviceId.value}/frida/stop`)
        showStatus(response.data.message, 'success')
        await loadDeviceDetails()
      } catch (err) {
        showStatus(err.response?.data?.detail || 'Failed to stop Frida server', 'error')
      } finally {
        stopping.value = false
      }
    }

    const restartFrida = async () => {
      try {
        restarting.value = true
        const response = await axios.post(`http://localhost:8000/api/devices/${deviceId.value}/frida/restart`)
        showStatus(response.data.message, 'success')
        await loadDeviceDetails()
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

    onMounted(() => {
      loadDeviceDetails()
      loadCachedVersions()
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
      statusMessage,
      statusType,
      refreshStatus,
      reconnectDevice,
      loadCachedVersions,
      installFrida,
      pushCachedServer,
      startFrida,
      stopFrida,
      restartFrida,
      getDeviceColor,
      getStatusBadge
    }
  }
}
</script>

