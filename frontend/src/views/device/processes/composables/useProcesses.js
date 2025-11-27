import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import { useToast } from '../../../../composables/useToast'

export function useProcesses(deviceSerial) {
  const toast = useToast()
  const processes = ref([])
  const stats = ref({})
  const loading = ref(false)
  const lastUpdate = ref('Never')
  const autoRefresh = ref(true)
  const refreshInterval = ref(2000)
  let refreshTimer = null

  const fetchProcesses = async () => {
    try {
      loading.value = true
      const response = await axios.get(`http://localhost:8000/api/devices/${deviceSerial}/processes`)
      processes.value = response.data.processes
      stats.value = response.data.stats
      lastUpdate.value = new Date().toLocaleTimeString()
    } catch (err) {
      console.error('Failed to fetch processes:', err)
      toast.error('Failed to fetch processes')
    } finally {
      loading.value = false
    }
  }

  const toggleAutoRefresh = () => {
    if (autoRefresh.value) {
      startAutoRefresh()
    } else {
      stopAutoRefresh()
    }
  }

  const startAutoRefresh = () => {
    stopAutoRefresh()
    refreshTimer = setInterval(fetchProcesses, refreshInterval.value)
  }

  const stopAutoRefresh = () => {
    if (refreshTimer) {
      clearInterval(refreshTimer)
      refreshTimer = null
    }
  }

  onMounted(async () => {
    await fetchProcesses()
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
    fetchProcesses,
    toggleAutoRefresh
  }
}

