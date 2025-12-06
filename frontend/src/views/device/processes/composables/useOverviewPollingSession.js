// Manages overview polling session registration with the backend
// Ensures only one tab controls the overview polling interval per device
// Sends heartbeats to maintain session and detect primary promotion

import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import { useToast } from '../../../../composables/useToast'

const ERROR_KEY_SESSION = 'overview-polling-session'

function generateClientId() {
  return `overview-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}

export function useOverviewPollingSession(deviceSerial) {
  const toast = useToast()
  const clientId = ref(generateClientId())
  const isPrimary = ref(false)
  const activeIntervalMs = ref(10000)  // 10 seconds for overview (heavy operation)
  const sessionMessage = ref('')
  const sessionRegistered = ref(false)

  const registerSession = async (intervalMs) => {
    try {
      const response = await axios.post(
        `http://localhost:8000/api/devices/${deviceSerial}/overview/session/register`,
        {
          client_id: clientId.value,
          interval_ms: intervalMs
        }
      )
      
      const wasPrimary = isPrimary.value
      isPrimary.value = response.data.is_primary
      activeIntervalMs.value = response.data.active_interval_ms
      sessionMessage.value = response.data.message
      sessionRegistered.value = true
      
      // Only show warning on initial registration or status change, not on heartbeats
      if (!wasPrimary && !response.data.is_primary && intervalMs !== response.data.active_interval_ms) {
        toast.warning(response.data.message, ERROR_KEY_SESSION)
      }
      
      toast.clearError(ERROR_KEY_SESSION)
      return response.data
      
    } catch (err) {
      console.error('Failed to register overview session:', err)
      toast.error('Failed to register overview polling session', ERROR_KEY_SESSION)
      return null
    }
  }

  // Heartbeat: lightweight session keep-alive using dedicated endpoint
  const heartbeat = async () => {
    if (!sessionRegistered.value) return
    
    try {
      const response = await axios.post(
        `http://localhost:8000/api/devices/${deviceSerial}/overview/session/heartbeat`,
        {
          client_id: clientId.value,
          interval_ms: activeIntervalMs.value
        }
      )
      
      const wasPrimary = isPrimary.value
      isPrimary.value = response.data.is_primary
      
      // Log promotion detection for debugging
      if (!wasPrimary && response.data.is_primary) {
        console.log(`[Overview] Client ${clientId.value} promoted to primary`)
      }
      
      return response.data
    } catch (err) {
      // Heartbeat failures are expected if session expired
      if (err.response?.status === 404) {
        console.warn('[Overview] Session expired, need to re-register')
        sessionRegistered.value = false
      } else {
        console.error('Failed to send overview heartbeat:', err)
      }
      return null
    }
  }

  const updateInterval = async (intervalMs) => {
    if (!sessionRegistered.value) {
      return registerSession(intervalMs)
    }
    
    const result = await registerSession(intervalMs)
    
    if (result && !result.is_primary && intervalMs !== result.active_interval_ms) {
      return {
        success: false,
        message: result.message,
        activeInterval: result.active_interval_ms
      }
    }
    
    return {
      success: true,
      activeInterval: result?.active_interval_ms || intervalMs
    }
  }

  const unregisterSession = async () => {
    if (!sessionRegistered.value) return
    
    try {
      await axios.post(
        `http://localhost:8000/api/devices/${deviceSerial}/overview/session/unregister`,
        { client_id: clientId.value, interval_ms: activeIntervalMs.value }
      )
      sessionRegistered.value = false
    } catch (err) {
      console.error('Failed to unregister overview session:', err)
    }
  }

  const handleBeforeUnload = () => {
    if (sessionRegistered.value) {
      const data = JSON.stringify({ 
        client_id: clientId.value, 
        interval_ms: activeIntervalMs.value 
      })
      // Use text/plain MIME type - application/json is not CORS-safelisted and may fail silently
      const blob = new Blob([data], { type: 'text/plain' })
      navigator.sendBeacon(
        `http://localhost:8000/api/devices/${deviceSerial}/overview/session/unregister`,
        blob
      )
    }
  }

  onMounted(async () => {
    await registerSession(activeIntervalMs.value)
    if (typeof window !== 'undefined') {
      window.addEventListener('beforeunload', handleBeforeUnload)
    }
  })

  onUnmounted(async () => {
    if (typeof window !== 'undefined') {
      window.removeEventListener('beforeunload', handleBeforeUnload)
    }
    await unregisterSession()
  })

  return {
    clientId,
    isPrimary,
    activeIntervalMs,
    sessionMessage,
    sessionRegistered,
    registerSession,
    updateInterval,
    unregisterSession,
    heartbeat
  }
}

