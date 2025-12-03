import { ref, onMounted, onUnmounted, watch } from 'vue'
import axios from 'axios'
import { useToast } from '../../../../composables/useToast'
import { usePollingSession } from './usePollingSession'

const ERROR_KEY_PROCESSES = 'processes-fetch'

export function useProcesses(deviceSerial, options = {}) {
  const { extraFetchers = [] } = options
  const toast = useToast()
  const {
    isPrimary,
    activeIntervalMs,
    sessionRegistered,
    updateInterval: updateSessionInterval,
    heartbeat
  } = usePollingSession(deviceSerial)
  
  const processes = ref([])
  const stats = ref({})
  const loading = ref(false)
  const lastUpdate = ref('Never')
  const autoRefresh = ref(true)
  const refreshInterval = ref(2000)
  const processHistory = ref([])
  const memoryHistory = ref([])
  let refreshTimer = null
  const maxHistoryPoints = 60

  // Sync local refreshInterval with session's activeIntervalMs
  watch(activeIntervalMs, (newInterval) => {
    if (newInterval && newInterval !== refreshInterval.value) {
      refreshInterval.value = newInterval
      if (autoRefresh.value && sessionRegistered.value) {
        startAutoRefresh()
      }
    }
  }, { immediate: true })

  // Restart polling when primary status changes (to adjust interval for secondary tabs)
  watch(isPrimary, () => {
    if (autoRefresh.value && sessionRegistered.value) {
      startAutoRefresh()
    }
  })
  
  // Start auto-refresh once session is registered
  watch(sessionRegistered, (registered) => {
    if (registered && autoRefresh.value) {
      startAutoRefresh()
    }
  })

  const fetchProcesses = async () => {
    try {
      loading.value = true
      const response = await axios.get(`http://localhost:8000/api/devices/${deviceSerial}/processes`)
      processes.value = response.data.processes
      stats.value = response.data.stats
      lastUpdate.value = new Date().toLocaleTimeString()

      const total = response.data.stats?.total ?? 0
      const user = response.data.stats?.user ?? 0
      const system = response.data.stats?.system ?? 0
      const timestamp = new Date().toISOString()

      processHistory.value.push({
        timestamp,
        total,
        user,
        system
      })

      if (processHistory.value.length > maxHistoryPoints) {
        processHistory.value.splice(0, processHistory.value.length - maxHistoryPoints)
      }

      toast.clearError(ERROR_KEY_PROCESSES)
    } catch (err) {
      console.error('Failed to fetch processes:', err)
      toast.error('Failed to fetch processes', ERROR_KEY_PROCESSES)
    } finally {
      loading.value = false
    }
  }

  const updateMemoryHistory = (usedMb) => {
    const timestamp = new Date().toISOString()
    memoryHistory.value.push({
      timestamp,
      memoryMb: usedMb
    })
    if (memoryHistory.value.length > maxHistoryPoints) {
      memoryHistory.value.splice(0, memoryHistory.value.length - maxHistoryPoints)
    }
  }

  const refreshAll = async () => {
    // Send heartbeat to keep session alive and sync primary/interval status
    await heartbeat()
    
    await fetchProcesses()

    if (Array.isArray(extraFetchers) && extraFetchers.length > 0) {
      try {
        await Promise.all(extraFetchers.map(fn => (typeof fn === 'function' ? fn() : null)))
      } catch (err) {
        console.error('Failed to refresh auxiliary metrics:', err)
        toast.error('Failed to refresh metrics')
      }
    }
  }

  const toggleAutoRefresh = () => {
    autoRefresh.value = !autoRefresh.value
    if (autoRefresh.value) {
      startAutoRefresh()
    } else {
      stopAutoRefresh()
    }
  }

  const startAutoRefresh = () => {
    stopAutoRefresh()
    // Secondary tabs poll at 3x the interval to reduce load
    // They'll still get fresh data from cache populated by primary
    const effectiveInterval = isPrimary.value ? refreshInterval.value : refreshInterval.value * 3
    refreshTimer = setInterval(refreshAll, effectiveInterval)
  }

  const stopAutoRefresh = () => {
    if (refreshTimer) {
      clearInterval(refreshTimer)
      refreshTimer = null
    }
  }

  const setRefreshInterval = async (newIntervalMs) => {
    const result = await updateSessionInterval(newIntervalMs)
    
    if (!result) {
      toast.error('Failed to update refresh interval')
      return false
    }
    
    if (!result.success) {
      // Secondary tab tried to change interval - show warning and use active interval
      toast.warning(result.message)
      refreshInterval.value = result.activeInterval
      if (autoRefresh.value) {
        startAutoRefresh()
      }
      return false
    }
    
    refreshInterval.value = result.activeInterval
    if (autoRefresh.value) {
      startAutoRefresh()
    }
    return true
  }

  onMounted(async () => {
    // Initial fetch - session registration happens in usePollingSession's onMounted
    // Auto-refresh will start via the sessionRegistered watcher once registration completes
    await refreshAll()
  })

  onUnmounted(() => {
    stopAutoRefresh()
  })

  return {
    processes,
    stats,
    loading,
    lastUpdate,
    autoRefresh,
    refreshInterval,
    processHistory,
    memoryHistory,
    fetchProcesses,
    refreshAll,
    toggleAutoRefresh,
    setRefreshInterval,
    updateMemoryHistory,
    isPrimary,
    sessionRegistered
  }
}
