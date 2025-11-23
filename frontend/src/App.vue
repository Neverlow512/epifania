<template>
  <div class="min-h-screen bg-black">
    <!-- Header -->
    <div class="navbar bg-black/80 backdrop-blur-md shadow-xl border-b border-primary/20 relative z-50">
      <div class="flex-1">
        <div class="flex items-center px-4">
          <div class="leading-tight">
            <h1 class="brand-title text-2xl md:text-3xl font-extrabold tracking-[0.12em] text-[#7100d0] uppercase cursor-pointer" @click="$router.push('/')">
              Epifania
            </h1>
            <p class="mt-1 text-xs md:text-sm text-slate-400 tracking-[0.18em] uppercase">
              Dynamic Instrumentation Platform
            </p>
          </div>
        </div>
      </div>
      <div class="flex-none px-4 gap-4 flex items-center">
        <!-- Frida Menu Dropdown -->
        <div class="dropdown dropdown-end">
          <label tabindex="0" class="btn btn-sm btn-ghost text-slate-400 hover:text-white gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            Frida (Custom)
          </label>
          <div
            tabindex="0"
            class="dropdown-content fixed right-4 top-16 z-[9999] card card-compact w-80 p-4 shadow-2xl bg-neutral-900 border border-primary/30 mt-2"
          >
            <div class="card-body">
              <h3 class="font-bold text-white mb-3">Frida Custom Download</h3>
              
              <!-- Version Selector -->
              <div class="form-control mb-4">
                <label class="label">
                  <span class="label-text text-slate-400">Select Custom Version</span>
                </label>
                <select 
                  v-model="selectedFridaVersion" 
                  class="select select-sm select-bordered bg-black border-primary/30 focus:border-primary text-white"
                  @focus="loadFridaVersions"
                >
                  <option value="" disabled>Select version</option>
                  <option v-for="version in fridaVersions" :key="version.version" :value="version.version">
                    {{ version.version }}
                  </option>
                </select>
              </div>

              <!-- Download Button -->
              <button 
                type="button"
                class="btn btn-sm btn-primary w-full mb-4"
                @click="downloadCustomVersion"
                :disabled="!selectedFridaVersion || isDownloading"
              >
                <svg v-if="!isDownloading" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                <span v-if="isDownloading" class="loading loading-spinner loading-xs"></span>
                {{ isDownloading ? 'Downloading...' : 'Download & Cache' }}
              </button>

              <!-- Warning Message -->
              <div class="alert alert-warning shadow-lg border-0 bg-yellow-900/20 border border-yellow-700/30">
                <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-5 w-5" fill="none" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <span class="text-yellow-200 text-xs">
                  For best results, use the Auto mode which automatically selects the optimal Frida version for your device.
                </span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- ADB Status and Reconnect -->
        <div class="flex items-center gap-2">
          <div class="badge badge-sm" :class="adbConnected ? 'badge-success' : 'badge-error'">
            {{ adbConnected ? 'ADB Connected' : 'ADB Offline' }}
          </div>
          <button 
            v-if="!adbConnected"
            @click="restartAdb"
            :disabled="isRestartingAdb"
            class="btn btn-xs btn-ghost text-slate-400 hover:text-white gap-1"
            title="Restart ADB Server"
          >
            <svg v-if="!isRestartingAdb" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            {{ isRestartingAdb ? 'Restarting...' : 'Reconnect' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" :selected-frida-version="selectedFridaVersion" />
      </transition>
    </router-view>

    <!-- Toast Notifications -->
    <ToastNotification />
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'
import ToastNotification from './components/ToastNotification.vue'
import { useToast } from './composables/useToast'
import { useApiConnection } from './composables/useApiConnection'

export default {
  name: 'App',
  components: {
    ToastNotification
  },
  setup() {
    const adbConnected = ref(false)
    const fridaVersions = ref([])
    const selectedFridaVersion = ref('')
    const isRestartingAdb = ref(false)
    const isDownloading = ref(false)
    const { success, error, info, warning } = useToast()
    const { isBackendConnected, startAutoReconnect, checkConnection } = useApiConnection()

    const checkHealth = async () => {
      try {
        const response = await axios.get('http://localhost:8000/health', { timeout: 3000 })
        adbConnected.value = response.data.adb_connected
      } catch (err) {
        adbConnected.value = false
      }
    }

    // Watch backend connection status and show notifications
    watch(isBackendConnected, (connected, wasConnected) => {
      if (connected && wasConnected === false) {
        success('Backend connection restored', 'System Status')
        checkHealth()
      } else if (!connected && wasConnected === true) {
        warning('Backend connection lost, attempting to reconnect...', 'System Status')
      }
    })

    const loadFridaVersions = async () => {
      if (fridaVersions.value.length > 0) return
      
      try {
        const response = await axios.get('http://localhost:8000/api/frida/versions')
        fridaVersions.value = response.data.versions
        
        if (fridaVersions.value.length > 0 && !selectedFridaVersion.value) {
          selectedFridaVersion.value = fridaVersions.value[0].version
        }
      } catch (err) {
        console.error('Failed to load Frida versions:', err)
      }
    }

    const restartAdb = async () => {
      if (isRestartingAdb.value) return
      
      isRestartingAdb.value = true
      info('Restarting ADB server...', 'ADB Restart')
      
      try {
        const response = await axios.post('http://localhost:8000/api/adb/restart')
        
        if (response.data.success) {
          success('ADB server restarted successfully', 'ADB Restart')
          await checkHealth()
        } else {
          error(response.data.message || 'Failed to restart ADB server', 'ADB Restart')
        }
      } catch (err) {
        error(err.response?.data?.detail || 'Failed to restart ADB server', 'ADB Restart')
      } finally {
        isRestartingAdb.value = false
      }
    }

    const downloadCustomVersion = async () => {
      if (!selectedFridaVersion.value) {
        warning('Please select a Frida version first', 'Download')
        return
      }

      isDownloading.value = true

      try {
        // Check if already cached
        const cachedResponse = await axios.get('http://localhost:8000/api/frida/cached')
        const cached = cachedResponse.data.cached
        
        // Get device architecture to check if this specific version+arch is cached
        const devicesResponse = await axios.get('http://localhost:8000/api/devices')
        const devices = devicesResponse.data.devices
        
        if (devices.length === 0) {
          warning('No devices connected. Connect a device to download the appropriate architecture.', 'Download')
          isDownloading.value = false
          return
        }

        const device = devices[0]
        const deviceArch = device.architecture
        
        // Map architecture
        const archMapping = {
          'armeabi-v7a': 'arm',
          'armeabi': 'arm',
          'arm64-v8a': 'arm64',
          'x86': 'x86',
          'x86_64': 'x86_64'
        }
        const fridaArch = archMapping[deviceArch] || deviceArch
        
        // Check if this version+arch combo is already cached
        if (cached[selectedFridaVersion.value] && cached[selectedFridaVersion.value].includes(fridaArch)) {
          success(`Frida ${selectedFridaVersion.value} (${fridaArch}) is already cached`, 'Already Downloaded')
          isDownloading.value = false
          return
        }

        info(`Downloading Frida ${selectedFridaVersion.value} for ${fridaArch}...`, 'Custom Download')
        
        const response = await axios.post(
          `http://localhost:8000/api/devices/${device.serial}/frida/install`,
          { version: selectedFridaVersion.value }
        )
        
        success(`Frida ${selectedFridaVersion.value} (${fridaArch}) downloaded and cached successfully`, 'Custom Download')
      } catch (err) {
        error(err.response?.data?.detail || 'Failed to download Frida version', 'Download Failed')
      } finally {
        isDownloading.value = false
      }
    }

    onMounted(() => {
      // Start auto-reconnect system
      startAutoReconnect()
      
      // Initial checks
      checkConnection().then(connected => {
        if (connected) {
          checkHealth()
          loadFridaVersions()
        }
      })
      
      // Periodic health checks when connected
      setInterval(() => {
        if (isBackendConnected.value) {
          checkHealth()
        }
      }, 10000)
    })

    return {
      adbConnected,
      fridaVersions,
      selectedFridaVersion,
      isRestartingAdb,
      isDownloading,
      isBackendConnected,
      loadFridaVersions,
      restartAdb,
      downloadCustomVersion
    }
  }
}
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
