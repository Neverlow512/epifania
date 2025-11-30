import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import { useToast } from '../../../../composables/useToast'

export function useProcesses(deviceSerial, options = {}) {
  const { extraFetchers = [] } = options
  const toast = useToast()
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
    } catch (err) {
      console.error('Failed to fetch processes:', err)
      toast.error('Failed to fetch processes')
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
    refreshTimer = setInterval(refreshAll, refreshInterval.value)
  }

  const stopAutoRefresh = () => {
    if (refreshTimer) {
      clearInterval(refreshTimer)
      refreshTimer = null
    }
  }

  const setRefreshInterval = (newIntervalMs) => {
    refreshInterval.value = newIntervalMs
    if (autoRefresh.value) {
      startAutoRefresh()
    }
  }

  onMounted(async () => {
    await refreshAll()
    if (autoRefresh.value) {
      startAutoRefresh()
    }
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
    updateMemoryHistory
  }
}
