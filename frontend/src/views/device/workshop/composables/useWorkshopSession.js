// Manages exclusive Workshop session lock per device
// Ensures only one browser tab can perform discoveries at a time
// 30s timeout, 10s heartbeat

import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import { useToast } from '../../../../composables/useToast'
import { getWorkshopClientId } from './workshopClientId'

const ERROR_KEY_SESSION = 'workshop-session'
const HEARTBEAT_INTERVAL = 10000
const RETRY_INTERVAL = 5000

export function useWorkshopSession(deviceSerial) {
  const toast = useToast()
  const clientId = ref(getWorkshopClientId())
  const hasLock = ref(false)
  const lockOwner = ref(null)
  const expiresIn = ref(0)
  const sessionMessage = ref('')
  const sessionRegistered = ref(false)
  let heartbeatTimer = null
  let retryTimer = null

  const acquireLock = async () => {
    stopRetry()
    
    try {
      console.log('[Workshop Session] Acquiring lock with client_id:', clientId.value)
      const response = await axios.post(
        `http://localhost:8000/api/devices/${deviceSerial}/workshop/session/acquire`,
        { client_id: clientId.value }
      )
      
      console.log('[Workshop Session] Acquire response:', response.data)
      
      hasLock.value = response.data.success
      sessionRegistered.value = response.data.success
      
      if (response.data.success) {
        expiresIn.value = response.data.expires_in || 30
        sessionMessage.value = 'Workshop session acquired'
        lockOwner.value = null
        toast.clearError(ERROR_KEY_SESSION)
        startHeartbeat()
        console.log('[Workshop Session] Lock acquired successfully')
      } else {
        lockOwner.value = response.data.lock_owner
        expiresIn.value = response.data.expires_in || 0
        sessionMessage.value = response.data.message
        console.log('[Workshop Session] Lock denied, owner:', response.data.lock_owner, 'expires in:', expiresIn.value)
        startRetry()
      }
      
      return response.data
    } catch (err) {
      console.error('Failed to acquire workshop session:', err)
      toast.error('Failed to acquire workshop session', ERROR_KEY_SESSION)
      startRetry()
      return { success: false, message: 'Connection error' }
    }
  }
  
  const startRetry = () => {
    stopRetry()
    retryTimer = setTimeout(async () => {
      if (!hasLock.value) {
        console.log('Retrying session acquisition...')
        await acquireLock()
      }
    }, RETRY_INTERVAL)
  }
  
  const stopRetry = () => {
    if (retryTimer) {
      clearTimeout(retryTimer)
      retryTimer = null
    }
  }

  const heartbeat = async () => {
    if (!sessionRegistered.value || !hasLock.value) return
    
    try {
      const response = await axios.post(
        `http://localhost:8000/api/devices/${deviceSerial}/workshop/session/heartbeat`,
        { client_id: clientId.value }
      )
      
      if (!response.data.success) {
        hasLock.value = false
        sessionRegistered.value = false
        stopHeartbeat()
        toast.warning('Workshop session lost, retrying...', ERROR_KEY_SESSION)
        startRetry()
      }
    } catch (err) {
      console.error('Heartbeat failed:', err)
      hasLock.value = false
      sessionRegistered.value = false
      stopHeartbeat()
      startRetry()
    }
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

  const releaseLock = async () => {
    if (!sessionRegistered.value || !hasLock.value) return
    
    try {
      await axios.post(
        `http://localhost:8000/api/devices/${deviceSerial}/workshop/session/release`,
        { client_id: clientId.value }
      )
      hasLock.value = false
      sessionRegistered.value = false
    } catch (err) {
      console.error('Failed to release workshop session:', err)
    }
  }

  const getSessionInfo = async () => {
    try {
      const response = await axios.get(
        `http://localhost:8000/api/devices/${deviceSerial}/workshop/session/info`
      )
      return response.data
    } catch (err) {
      console.error('Failed to get session info:', err)
      return null
    }
  }

  const handleBeforeUnload = () => {
    if (sessionRegistered.value && hasLock.value) {
      const data = JSON.stringify({ client_id: clientId.value })
      const blob = new Blob([data], { type: 'application/json' })
      navigator.sendBeacon(
        `http://localhost:8000/api/devices/${deviceSerial}/workshop/session/release`,
        blob
      )
    }
  }

  const handleVisibilityChange = () => {
    if (!document.hidden && sessionRegistered.value && hasLock.value) {
      heartbeat()
    }
  }

  onMounted(async () => {
    await acquireLock()
    
    if (typeof window !== 'undefined') {
      window.addEventListener('beforeunload', handleBeforeUnload)
      document.addEventListener('visibilitychange', handleVisibilityChange)
    }
  })

  onUnmounted(async () => {
    stopHeartbeat()
    stopRetry()
    if (typeof window !== 'undefined') {
      window.removeEventListener('beforeunload', handleBeforeUnload)
      document.removeEventListener('visibilitychange', handleVisibilityChange)
    }
    await releaseLock()
  })

  return {
    clientId,
    hasLock,
    lockOwner,
    expiresIn,
    sessionMessage,
    sessionRegistered,
    acquireLock,
    releaseLock,
    getSessionInfo,
    heartbeat
  }
}

