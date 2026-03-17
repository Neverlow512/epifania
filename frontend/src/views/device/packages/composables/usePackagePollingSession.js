import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import { useToast } from '../../../../composables/useToast'

const ERROR_KEY_SESSION = 'packages-polling-session'
const HEARTBEAT_INTERVAL = 5000

function generateClientId() {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}

export function usePackagePollingSession(deviceSerial) {
  const toast = useToast()
  const clientId = ref(generateClientId())
  const isPrimary = ref(false)
  const activeIntervalMs = ref(5000)
  const sessionMessage = ref('')
  const sessionRegistered = ref(false)
  let heartbeatTimer = null

  const registerSession = async (intervalMs) => {
    try {
      const response = await axios.post(
        `http://localhost:8000/api/devices/${deviceSerial}/packages/session/register`,
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
      
      if (!wasPrimary && !response.data.is_primary && intervalMs !== response.data.active_interval_ms) {
        toast.warning(response.data.message, ERROR_KEY_SESSION)
      }
      
      toast.clearError(ERROR_KEY_SESSION)
      return response.data
      
    } catch (err) {
      console.error('Failed to register packages session:', err)
      toast.error('Failed to register packages polling session', ERROR_KEY_SESSION)
      return null
    }
  }

  const heartbeat = async () => {
    if (!sessionRegistered.value) return
    await registerSession(activeIntervalMs.value)
  }

  const startHeartbeat = () => {
    stopHeartbeat()
    heartbeatTimer = setInterval(heartbeat, HEARTBEAT_INTERVAL)
  }

  const stopHeartbeat = () => {
    if (heartbeatTimer) {
      clearInterval(heartbeatTimer)
      heartbeatTimer = null
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
        `http://localhost:8000/api/devices/${deviceSerial}/packages/session/unregister`,
        { client_id: clientId.value, interval_ms: activeIntervalMs.value }
      )
      sessionRegistered.value = false
    } catch (err) {
      console.error('Failed to unregister packages session:', err)
    }
  }

  const handleBeforeUnload = () => {
    if (sessionRegistered.value) {
      const data = JSON.stringify({ client_id: clientId.value, interval_ms: activeIntervalMs.value })
      const blob = new Blob([data], { type: 'text/plain' })
      navigator.sendBeacon(
        `http://localhost:8000/api/devices/${deviceSerial}/packages/session/unregister`,
        blob
      )
    }
  }

  const handleVisibilityChange = () => {
    if (!document.hidden && sessionRegistered.value) {
      heartbeat()
    }
  }

  onMounted(async () => {
    await registerSession(activeIntervalMs.value)
    startHeartbeat()
    if (typeof window !== 'undefined') {
      window.addEventListener('beforeunload', handleBeforeUnload)
      document.addEventListener('visibilitychange', handleVisibilityChange)
    }
  })

  onUnmounted(async () => {
    stopHeartbeat()
    if (typeof window !== 'undefined') {
      window.removeEventListener('beforeunload', handleBeforeUnload)
      document.removeEventListener('visibilitychange', handleVisibilityChange)
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
