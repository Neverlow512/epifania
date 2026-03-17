// Process overview state management - fetch and display detailed process info
// Supports auto-refresh with tab synchronization via backend session management
// Secondary tabs read from cache only, controlled by primary tab's interval

import { ref, onMounted, onUnmounted, watch } from 'vue'
import axios from 'axios'
import { useToast } from '../../../../composables/useToast'
import { useOverviewPollingSession } from './useOverviewPollingSession'

const ERROR_KEY_OVERVIEW = 'process-overview'

export function useProcessOverview(deviceSerial) {
  const toast = useToast()
  const {
    isPrimary,
    activeIntervalMs,
    sessionRegistered,
    updateInterval: updateSessionInterval,
    heartbeat
  } = useOverviewPollingSession(deviceSerial)
  
  const expandedPid = ref(null)
  const overviewData = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const lastUpdate = ref(null)
  const isCached = ref(false)
  const cacheAge = ref(0)
  
  const autoRefresh = ref(false)
  const refreshInterval = ref(10000)  // 10 seconds minimum for overview (heavy operation)
  let refreshTimer = null
  let heartbeatTimer = null

  // Sync local refreshInterval with session's activeIntervalMs
  watch(activeIntervalMs, (newInterval) => {
    if (newInterval && newInterval !== refreshInterval.value) {
      refreshInterval.value = newInterval
      if (autoRefresh.value && sessionRegistered.value) {
        startAutoRefresh()
      }
    }
  }, { immediate: true })

  // Restart polling when primary status changes
  watch(isPrimary, (newIsPrimary) => {
    if (autoRefresh.value && sessionRegistered.value && expandedPid.value) {
      if (newIsPrimary) {
        // Just promoted to primary, start polling immediately
        console.log('[Overview] Promoted to primary, starting polling')
        stopHeartbeatTimer()
        startAutoRefresh()
      } else {
        // Demoted to secondary, stop polling
        console.log('[Overview] Demoted to secondary, stopping polling')
        stopAutoRefresh()
      }
    }
  })
  
  // Start auto-refresh once session is registered (only for primary tabs with expanded PID)
  watch(sessionRegistered, (registered) => {
    if (registered && autoRefresh.value && isPrimary.value && expandedPid.value) {
      startAutoRefresh()
    }
  })

  async function fetchOverview(pid, forceRefresh = false) {
    if (!pid) return
    
    loading.value = true
    error.value = null
    
    try {
      const url = `http://localhost:8000/api/devices/${deviceSerial}/processes/${pid}/overview`
      // Secondary tabs should never force refresh - they read from cache only
      const shouldForceRefresh = forceRefresh && isPrimary.value
      const params = shouldForceRefresh ? { force_refresh: true } : {}
      
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
      // Only primary tab can force refresh
      await fetchOverview(expandedPid.value, isPrimary.value)
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
    
    // Only primary tab polls the backend
    // Secondary tabs are read-only and don't make requests
    if (!isPrimary.value) {
      // Secondary tabs send periodic heartbeats to keep session alive
      startHeartbeatTimer()
      return
    }
    
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
    stopHeartbeatTimer()
  }

  function startHeartbeatTimer() {
    stopHeartbeatTimer()
    // Send heartbeat every 5 seconds to keep session alive and detect promotion quickly
    // Session timeout is 15s, so 5s keeps us well within the window
    heartbeatTimer = setInterval(() => {
      heartbeat()
    }, 5000)
  }

  function stopHeartbeatTimer() {
    if (heartbeatTimer) {
      clearInterval(heartbeatTimer)
      heartbeatTimer = null
    }
  }

  async function toggleAutoRefresh() {
    autoRefresh.value = !autoRefresh.value
    
    if (autoRefresh.value) {
      // Only start if session is registered and we have a PID
      // The watcher will start auto-refresh when session becomes ready
      if (sessionRegistered.value && expandedPid.value) {
        startAutoRefresh()
      }
    } else {
      stopAutoRefresh()
    }
  }

  async function setRefreshInterval(newIntervalMs) {
    const result = await updateSessionInterval(newIntervalMs)
    
    if (!result) {
      toast.error('Failed to update overview refresh interval')
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

  watch(expandedPid, (newPid, oldPid) => {
    if (!newPid && oldPid) {
      stopAutoRefresh()
    } else if (newPid && autoRefresh.value) {
      startAutoRefresh()
    }
  })

  onUnmounted(() => {
    stopAutoRefresh()
  })

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
