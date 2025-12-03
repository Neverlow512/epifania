// Process overview state management - fetch and display detailed process info
// Supports auto-refresh with tab synchronization via backend session management

import { ref, onMounted, onUnmounted, watch } from 'vue'
import axios from 'axios'
import { useToast } from '../../../../composables/useToast'

const ERROR_KEY_OVERVIEW = 'process-overview'
const ERROR_KEY_SESSION = 'overview-session'

function generateClientId() {
  return `overview-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}

export function useProcessOverview(deviceSerial) {
  const toast = useToast()
  
  const expandedPid = ref(null)
  const overviewData = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const lastUpdate = ref(null)
  const isCached = ref(false)
  const cacheAge = ref(0)
  
  const autoRefresh = ref(false)
  const refreshInterval = ref(5000)
  let refreshTimer = null
  
  const clientId = ref(generateClientId())
  const isPrimary = ref(false)
  const sessionRegistered = ref(false)

  async function registerSession(intervalMs) {
    try {
      const response = await axios.post(
        `http://localhost:8000/api/devices/${deviceSerial}/overview/session/register`,
        {
          client_id: clientId.value,
          interval_ms: intervalMs
        }
      )
      
      isPrimary.value = response.data.is_primary
      refreshInterval.value = response.data.active_interval_ms
      sessionRegistered.value = true
      
      if (!response.data.is_primary && intervalMs !== response.data.active_interval_ms) {
        toast.warning(response.data.message, ERROR_KEY_SESSION)
      }
      
      toast.clearError(ERROR_KEY_SESSION)
      return response.data
      
    } catch (err) {
      console.error('Failed to register overview session:', err)
      return null
    }
  }

  async function unregisterSession() {
    if (!sessionRegistered.value) return
    
    try {
      await axios.post(
        `http://localhost:8000/api/devices/${deviceSerial}/overview/session/unregister`,
        { client_id: clientId.value, interval_ms: refreshInterval.value }
      )
      sessionRegistered.value = false
    } catch (err) {
      console.error('Failed to unregister overview session:', err)
    }
  }

  async function fetchOverview(pid, forceRefresh = false) {
    if (!pid) return
    
    loading.value = true
    error.value = null
    
    try {
      const url = `http://localhost:8000/api/devices/${deviceSerial}/processes/${pid}/overview`
      const params = forceRefresh ? { force_refresh: true } : {}
      
      const response = await axios.get(url, { params })
      overviewData.value = response.data
      lastUpdate.value = new Date()
      
      if (response.data._cache) {
        isCached.value = response.data._cache.is_cached
        cacheAge.value = response.data._cache.age_seconds
      } else {
        isCached.value = false
        cacheAge.value = 0
      }
      
      toast.clearError(ERROR_KEY_OVERVIEW)
    } catch (err) {
      console.error('Failed to fetch process overview:', err)
      error.value = err.response?.data?.detail || 'Failed to fetch process overview'
      overviewData.value = null
      toast.error(error.value, ERROR_KEY_OVERVIEW)
    } finally {
      loading.value = false
    }
  }

  async function refreshOverview() {
    if (expandedPid.value) {
      await fetchOverview(expandedPid.value, false)
    }
  }

  async function forceRefreshOverview() {
    if (expandedPid.value) {
      await fetchOverview(expandedPid.value, true)
    }
  }

  async function toggleOverview(pid) {
    if (expandedPid.value === pid) {
      closeOverview()
      return
    }
    
    expandedPid.value = pid
    await fetchOverview(pid, true)
  }

  function closeOverview() {
    stopAutoRefresh()
    expandedPid.value = null
    overviewData.value = null
    error.value = null
    lastUpdate.value = null
    isCached.value = false
    cacheAge.value = 0
  }

  async function inspectProcess(pid) {
    expandedPid.value = pid
    await fetchOverview(pid, true)
  }

  function startAutoRefresh() {
    stopAutoRefresh()
    if (!autoRefresh.value || !expandedPid.value) return
    
    refreshTimer = setInterval(() => {
      if (expandedPid.value) {
        refreshOverview()
      }
    }, refreshInterval.value)
  }

  function stopAutoRefresh() {
    if (refreshTimer) {
      clearInterval(refreshTimer)
      refreshTimer = null
    }
  }

  async function toggleAutoRefresh() {
    autoRefresh.value = !autoRefresh.value
    
    if (autoRefresh.value) {
      if (!sessionRegistered.value) {
        await registerSession(refreshInterval.value)
      }
      startAutoRefresh()
    } else {
      stopAutoRefresh()
    }
  }

  async function setRefreshInterval(newIntervalMs) {
    const result = await registerSession(newIntervalMs)
    
    if (!result) {
      toast.error('Failed to update overview refresh interval')
      return false
    }
    
    if (!result.is_primary && newIntervalMs !== result.active_interval_ms) {
      toast.warning(result.message)
      refreshInterval.value = result.active_interval_ms
    } else {
      refreshInterval.value = result.active_interval_ms
    }
    
    if (autoRefresh.value) {
      startAutoRefresh()
    }
    
    return result.is_primary
  }

  watch(expandedPid, (newPid, oldPid) => {
    if (!newPid && oldPid) {
      stopAutoRefresh()
    } else if (newPid && autoRefresh.value) {
      startAutoRefresh()
    }
  })

  onMounted(async () => {
    if (autoRefresh.value) {
      await registerSession(refreshInterval.value)
    }
  })

  onUnmounted(async () => {
    stopAutoRefresh()
    await unregisterSession()
  })

  if (typeof window !== 'undefined') {
    window.addEventListener('beforeunload', () => {
      if (sessionRegistered.value) {
        navigator.sendBeacon(
          `http://localhost:8000/api/devices/${deviceSerial}/overview/session/unregister`,
          JSON.stringify({ client_id: clientId.value, interval_ms: refreshInterval.value })
        )
      }
    })
  }

  return {
    expandedPid,
    overviewData,
    loading,
    error,
    lastUpdate,
    isCached,
    cacheAge,
    autoRefresh,
    refreshInterval,
    isPrimary,
    sessionRegistered,
    toggleOverview,
    closeOverview,
    inspectProcess,
    refreshOverview,
    forceRefreshOverview,
    toggleAutoRefresh,
    setRefreshInterval
  }
}
