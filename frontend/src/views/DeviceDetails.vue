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

    <!-- Device Content -->
    <div v-else>
      <!-- Compact Header -->
      <div class="card bg-neutral-900/60 backdrop-blur-sm shadow-2xl border border-primary/20 mb-4">
        <div class="card-body p-4">
          <div class="flex items-center gap-3 flex-wrap">
            <h2 class="text-xl font-bold text-white">{{ device.name }}</h2>
            <div 
              class="badge badge-sm"
              :class="device.type === 'emulator' ? 'badge-primary' : 'badge-accent'"
            >
              {{ device.type === 'emulator' ? 'Emulator' : 'Physical' }}
            </div>
            <div class="badge badge-sm" :class="getStatusBadge(device.state)">
              {{ device.state }}
            </div>
            <div class="text-slate-400 text-sm">SDK {{ device.sdk_version }}</div>
            <div class="text-sm" :class="device.has_root ? 'text-green-400' : 'text-red-400'">
              {{ device.has_root ? 'Root ✓' : 'No Root' }}
            </div>
          </div>
        </div>
      </div>

      <!-- Tab Navigation -->
      <TabNavigation
        :tabs="tabs"
        :activeTab="activeTab"
        @tab-change="handleTabChange"
      />

      <!-- Tab Content -->
      <div class="mt-6">
        <component 
          :is="currentTabComponent"
          :device="device"
          :adbConnected="adbConnected"
          :reconnecting="reconnecting"
          :refreshing="refreshing"
          :installing="installing"
          :pushing="pushing"
          :starting="starting"
          :stopping="stopping"
          :restarting="restarting"
          :cachedVersions="cachedVersions"
          :selectedCachedVersion="selectedCachedVersion"
          :autoFridaVersion="autoFridaVersion"
          :discovering="discovering"
          :discoveredServers="discoveredServers"
          :cleaning="cleaning"
          :showCleanupModal="showCleanupModal"
          :showDiagnosticsModal="showDiagnosticsModal"
          :showInstallDetailsModal="showInstallDetailsModal"
          :showPushDetailsModal="showPushDetailsModal"
          :showFridaControlsDetailsModal="showFridaControlsDetailsModal"
          :hasSelectedServers="hasSelectedServers"
          :selectedServerPaths="selectedServerPaths"
          :permissionStatus="permissionStatus"
          :fixingPermissions="fixingPermissions"
          :diagnosticResults="diagnosticResults"
          :runningDiagnostics="runningDiagnostics"
          :fridaConnected="fridaConnected"
          :testingConnection="testingConnection"
          :lastConnectionTest="lastConnectionTest"
          @reconnect-device="reconnectDevice"
          @refresh-status="refreshStatus"
          @load-cached-versions="loadCachedVersions"
          @install-frida-auto="installFridaAuto"
          @push-cached-server="pushCachedServer"
          @start-frida="startFrida"
          @stop-frida="stopFrida"
          @restart-frida="restartFrida"
          @discover-servers="discoverServers"
          @show-cleanup-confirmation="showCleanupConfirmation"
          @cleanup-servers="cleanupServers"
          @select-all-servers="selectAllServers"
          @deselect-all-servers="deselectAllServers"
          @fix-permissions="fixPermissions"
          @fix-server-permissions="fixServerPermissions"
          @run-diagnostics="runDiagnostics"
          @update:selectedCachedVersion="selectedCachedVersion = $event"
          @update:showCleanupModal="showCleanupModal = $event"
          @update:showDiagnosticsModal="showDiagnosticsModal = $event"
          @update:showInstallDetailsModal="showInstallDetailsModal = $event"
          @update:showPushDetailsModal="showPushDetailsModal = $event"
          @update:showFridaControlsDetailsModal="showFridaControlsDetailsModal = $event"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import TabNavigation from '../components/TabNavigation.vue'
import DeviceTab from './device/overview/DeviceTab.vue'
import ProcessesTab from './device/processes/ProcessesTab.vue'
import PackagesTab from './device/packages/PackagesTab.vue'
import FilesTab from './device/files/FilesTab.vue'
import WorkshopTab from './device/workshop/WorkshopTab.vue'
import { useToast } from '../composables/useToast'

export default {
  name: 'DeviceDetails',
  components: {
    TabNavigation,
    DeviceTab,
    ProcessesTab,
    PackagesTab,
    FilesTab,
    WorkshopTab
  },
  props: {
    selectedFridaVersion: {
      type: String,
      default: ''
    }
  },
  setup(props) {
    const route = useRoute()
    const router = useRouter()
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
    const autoFridaVersion = ref('')
    const autoFridaArch = ref('')
    
    const discovering = ref(false)
    const discoveredServers = ref([])
    const cleaning = ref(false)
    const showCleanupModal = ref(false)
    const showDiagnosticsModal = ref(false)
    const showInstallDetailsModal = ref(false)
    const showPushDetailsModal = ref(false)
    const showFridaControlsDetailsModal = ref(false)
    
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

    const tabs = [
      { name: 'device', label: 'Device' },
      { name: 'processes', label: 'Processes' },
      { name: 'packages', label: 'Packages' },
      { name: 'files', label: 'Files' },
      { name: 'workshop', label: 'Workshop' }
    ]

    const activeTab = ref(route.query.tab || 'device')
    
    const currentTabComponent = computed(() => {
      const componentMap = {
        device: DeviceTab,
        processes: ProcessesTab,
        packages: PackagesTab,
        files: FilesTab,
        workshop: WorkshopTab
      }
      return componentMap[activeTab.value] || DeviceTab
    })

    const handleTabChange = (tabName) => {
      activeTab.value = tabName
      router.push({ query: { ...route.query, tab: tabName } })
    }

    watch(() => route.query.tab, (newTab) => {
      if (newTab && newTab !== activeTab.value) {
        activeTab.value = newTab
      }
    })

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
        toast[response.data.connected ? 'success' : 'error'](response.data.message)
        await loadDeviceDetails(false)
      } catch (err) {
        toast.error('Failed to reconnect device')
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
        toast.success(response.data.message, 'Frida Installation')
        await loadDeviceDetails(false)
      } catch (err) {
        const errorMsg = err.response?.data?.detail || 'Failed to install Frida server'
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
          toast.error(`No cached binary for architecture ${fridaArch}`)
          return
        }

        const response = await axios.post(
          `http://localhost:8000/api/devices/${deviceId.value}/frida/push`,
          { 
            version: selectedCachedVersion.value,
            architecture: fridaArch
          }
        )
        toast.success(response.data.message)
        await loadDeviceDetails(false)
      } catch (err) {
        toast.error(err.response?.data?.detail || 'Failed to push Frida server')
      } finally {
        pushing.value = false
      }
    }

    const startFrida = async () => {
      try {
        starting.value = true
        toast.info('Starting Frida server...', 'Frida Server')
        const response = await axios.post(`http://localhost:8000/api/devices/${deviceId.value}/frida/start`)
        toast.success(response.data.message, 'Frida Server')
        await loadDeviceDetails(false)
      } catch (err) {
        const errorMsg = err.response?.data?.detail || 'Failed to start Frida server'
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
        toast.success(response.data.message, 'Frida Server')
        await loadDeviceDetails(false)
      } catch (err) {
        const errorMsg = err.response?.data?.detail || 'Failed to stop Frida server'
        toast.error(errorMsg, 'Stop Failed')
      } finally {
        stopping.value = false
      }
    }

    const restartFrida = async () => {
      try {
        restarting.value = true
        const response = await axios.post(`http://localhost:8000/api/devices/${deviceId.value}/frida/restart`)
        toast.success(response.data.message)
        await loadDeviceDetails(false)
      } catch (err) {
        toast.error(err.response?.data?.detail || 'Failed to restart Frida server')
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

    const getStatusBadge = (state) => {
      if (state === 'online') return 'badge-success'
      if (state === 'error') return 'badge-error'
      return 'badge-warning'
    }

    const discoverServers = async () => {
      try {
        discovering.value = true
        const response = await axios.get(`http://localhost:8000/api/devices/${deviceId.value}/frida/discover`)
        discoveredServers.value = response.data.servers.map(s => ({ ...s, selected: false }))
        
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
      }, 15000)
      
      connectionCheckInterval = setInterval(async () => {
        if (device.value?.frida_server_running) {
          await testFridaConnection()
        } else {
          fridaConnected.value = false
        }
      }, 30000)
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
      autoFridaVersion,
      discovering,
      discoveredServers,
      cleaning,
      showCleanupModal,
      showDiagnosticsModal,
      showInstallDetailsModal,
      showPushDetailsModal,
      showFridaControlsDetailsModal,
      hasSelectedServers,
      selectedServerPaths,
      permissionStatus,
      fixingPermissions,
      diagnosticResults,
      runningDiagnostics,
      fridaConnected,
      testingConnection,
      lastConnectionTest,
      tabs,
      activeTab,
      currentTabComponent,
      handleTabChange,
      refreshStatus,
      reconnectDevice,
      loadCachedVersions,
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
      fixServerPermissions,
      getStatusBadge
    }
  }
}
</script>
