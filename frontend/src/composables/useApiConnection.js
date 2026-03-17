import { ref, computed } from 'vue'
import axios from 'axios'

const isBackendConnected = ref(false)
const isChecking = ref(false)
const lastCheckTime = ref(null)
const consecutiveFailures = ref(0)
const maxRetries = 5

const backoffDelays = [1000, 2000, 5000, 10000, 30000]

export function useApiConnection() {
  const connectionStatus = computed(() => {
    if (isBackendConnected.value) return 'connected'
    if (isChecking.value) return 'checking'
    return 'disconnected'
  })

  const checkConnection = async (silent = false) => {
    if (isChecking.value) return isBackendConnected.value

    isChecking.value = true
    
    try {
      const response = await axios.get('http://localhost:8000/health', {
        timeout: 3000
      })
      
      if (response.data.status === 'healthy') {
        isBackendConnected.value = true
        consecutiveFailures.value = 0
        lastCheckTime.value = Date.now()
        return true
      }
      
      isBackendConnected.value = false
      return false
      
    } catch (error) {
      isBackendConnected.value = false
      consecutiveFailures.value++
      
      if (!silent) {
        console.warn('Backend connection check failed:', error.message)
      }
      
      return false
    } finally {
      isChecking.value = false
      lastCheckTime.value = Date.now()
    }
  }

  const startAutoReconnect = () => {
    let reconnectAttempt = 0
    
    const attemptReconnect = async () => {
      if (isBackendConnected.value) {
        reconnectAttempt = 0
        return
      }

      if (reconnectAttempt >= maxRetries) {
        console.error('Max reconnection attempts reached')
        setTimeout(() => {
          reconnectAttempt = 0
          attemptReconnect()
        }, backoffDelays[backoffDelays.length - 1])
        return
      }

      const delay = backoffDelays[Math.min(reconnectAttempt, backoffDelays.length - 1)]
      console.log(`Attempting to reconnect to backend (attempt ${reconnectAttempt + 1}/${maxRetries})...`)
      
      const connected = await checkConnection(true)
      
      if (connected) {
        console.log('Backend connection restored')
        reconnectAttempt = 0
      } else {
        reconnectAttempt++
        setTimeout(attemptReconnect, delay)
      }
    }

    // Initial check
    checkConnection(false).then(connected => {
      if (!connected) {
        attemptReconnect()
      }
    })

    // Periodic health checks
    setInterval(async () => {
      const wasConnected = isBackendConnected.value
      await checkConnection(true)
      
      if (wasConnected && !isBackendConnected.value) {
        console.warn('Backend connection lost, starting reconnection...')
        attemptReconnect()
      }
    }, 10000)
  }

  const waitForConnection = async (timeoutMs = 30000) => {
    const startTime = Date.now()
    
    while (Date.now() - startTime < timeoutMs) {
      if (await checkConnection(true)) {
        return true
      }
      await new Promise(resolve => setTimeout(resolve, 1000))
    }
    
    return false
  }

  return {
    isBackendConnected,
    isChecking,
    connectionStatus,
    consecutiveFailures,
    checkConnection,
    startAutoReconnect,
    waitForConnection
  }
}

