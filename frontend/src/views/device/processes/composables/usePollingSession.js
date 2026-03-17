// Manages polling session registration with the backend
// Ensures only one tab controls the polling interval per device
// Sends heartbeats on each poll to maintain session

import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import { useToast } from '../../../../composables/useToast'

const ERROR_KEY_SESSION = 'polling-session'

function generateClientId() {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}

export function usePollingSession(deviceSerial) {
  const toast = useToast()
  const clientId = ref(generateClientId())
  const isPrimary = ref(false)
  const activeIntervalMs = ref(2000)
  const sessionMessage = ref('')
  const sessionRegistered = ref(false)

  const registerSession = async (intervalMs) => {
    try {
      const response = await axios.post(
        `http://localhost:8000/api/devices/${deviceSerial}/session/register`,
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
      console.error('Failed to register session:', err)
      toast.error('Failed to register polling session', ERROR_KEY_SESSION)
      return null
    }
  }

  // Heartbeat: re-register with current interval to keep session alive
  const heartbeat = async () => {
    if (!sessionRegistered.value) return
    await registerSession(activeIntervalMs.value)
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
        `http://localhost:8000/api/devices/${deviceSerial}/session/unregister`,
        { client_id: clientId.value, interval_ms: activeIntervalMs.value }
      )
      sessionRegistered.value = false
    } catch (err) {
      console.error('Failed to unregister session:', err)
    }
  }

  const handleBeforeUnload = () => {
    if (sessionRegistered.value) {
      const data = JSON.stringify({ client_id: clientId.value, interval_ms: activeIntervalMs.value })
      // Use text/plain MIME type - application/json is not CORS-safelisted and may fail silently
      const blob = new Blob([data], { type: 'text/plain' })
      navigator.sendBeacon(
        `http://localhost:8000/api/devices/${deviceSerial}/session/unregister`,
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

