// Manages polling session registration with the backend
// Ensures only one tab controls the polling interval per device

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
      
      isPrimary.value = response.data.is_primary
      activeIntervalMs.value = response.data.active_interval_ms
      sessionMessage.value = response.data.message
      sessionRegistered.value = true
      
      if (!response.data.is_primary && intervalMs !== response.data.active_interval_ms) {
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

  onMounted(async () => {
    await registerSession(activeIntervalMs.value)
  })

  onUnmounted(async () => {
    await unregisterSession()
  })

  // Handle page unload
  if (typeof window !== 'undefined') {
    window.addEventListener('beforeunload', () => {
      if (sessionRegistered.value) {
        navigator.sendBeacon(
          `http://localhost:8000/api/devices/${deviceSerial}/session/unregister`,
          JSON.stringify({ client_id: clientId.value, interval_ms: activeIntervalMs.value })
        )
      }
    })
  }

  return {
    clientId,
    isPrimary,
    activeIntervalMs,
    sessionMessage,
    sessionRegistered,
    registerSession,
    updateInterval,
    unregisterSession
  }
}

