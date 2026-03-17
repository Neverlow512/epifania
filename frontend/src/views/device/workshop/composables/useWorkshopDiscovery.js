// Manages Workshop discovery lifecycle with WebSocket progress tracking

import { ref, onUnmounted } from 'vue'
import axios from 'axios'
import { useToast } from '../../../../composables/useToast'

const PHASE_LABELS = {
  'attaching': 'Attaching to process',
  'attached': 'Attached to process',
  'java_enum': 'Enumerating Java classes',
  'java_methods': 'Discovering Java methods',
  'java_categorize': 'Categorizing Java classes',
  'java_complete': 'Java discovery complete',
  'native_enum': 'Enumerating native modules',
  'native_exports': 'Discovering native exports',
  'native_categorize': 'Categorizing native modules',
  'native_complete': 'Native discovery complete',
  'finalizing': 'Finalizing results',
  'complete': 'Discovery complete',
  'error': 'Discovery failed',
  'idle': 'Ready'
}

export function useWorkshopDiscovery(deviceSerial, clientId) {
  const toast = useToast()
  
  const discoveryState = ref('idle')
  const discoveryProgress = ref(0)
  const discoveryPhase = ref('')
  const discoveryMessage = ref('')
  const discoveryId = ref(null)
  const discoveryResult = ref(null)
  
  let websocket = null
  let reconnectAttempts = 0
  const MAX_RECONNECT_ATTEMPTS = 3
  
  const getPhaseLabel = (phase) => {
    return PHASE_LABELS[phase] || phase
  }
  
  const connectWebSocket = () => {
    if (websocket && websocket.readyState === WebSocket.OPEN) {
      return
    }
    
    const wsUrl = `ws://localhost:8000/ws/devices/${deviceSerial}/workshop/discovery`
    console.log('[Workshop] Connecting WebSocket:', wsUrl)
    
    websocket = new WebSocket(wsUrl)
    
    websocket.onopen = () => {
      console.log('[Workshop] WebSocket connected')
      reconnectAttempts = 0
    }
    
    websocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        console.log('[Workshop] Progress update:', data)
        
        discoveryProgress.value = data.progress || 0
        discoveryPhase.value = getPhaseLabel(data.phase || '')
        discoveryMessage.value = data.message || ''
        
        const state = data.state || 'running'
        
        if (state === 'complete') {
          discoveryProgress.value = 100
          discoveryState.value = 'complete'
          fetchDiscoveryResult()
          closeWebSocket()
        } else if (state === 'error') {
          toast.error(data.message || 'Discovery failed', 'Discovery')
          discoveryState.value = 'error'
          closeWebSocket()
        } else if (state === 'cancelled') {
          if (discoveryState.value === 'running') {
            toast.info('Discovery cancelled', 'Discovery')
          }
          discoveryState.value = 'cancelled'
          closeWebSocket()
        } else if (state === 'running') {
          discoveryState.value = 'running'
        } else if (state === 'idle') {
          console.log('[Workshop] Waiting for discovery to start...')
        }
      } catch (err) {
        console.error('[Workshop] Failed to parse WebSocket message:', err)
      }
    }
    
    websocket.onerror = (error) => {
      console.error('[Workshop] WebSocket error:', error)
      
      if (discoveryState.value === 'running' && reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
        reconnectAttempts++
        console.log(`[Workshop] Attempting reconnect ${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS}`)
        setTimeout(() => connectWebSocket(), 500)
      } else if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
        toast.error('Lost connection to discovery progress', 'Discovery')
        // Fall back to polling
        pollDiscoveryStatus()
      }
    }
    
    websocket.onclose = (event) => {
      console.log('[Workshop] WebSocket closed:', event.code, event.reason)
    }
  }
  
  const closeWebSocket = () => {
    return new Promise((resolve) => {
      if (websocket) {
        if (websocket.readyState === WebSocket.OPEN || websocket.readyState === WebSocket.CONNECTING) {
          websocket.onclose = () => {
            websocket = null
            resolve()
          }
          websocket.close()
        } else {
          websocket = null
          resolve()
        }
      } else {
        resolve()
      }
    })
  }
  
  const pollDiscoveryStatus = async () => {
    console.log('[Workshop] Falling back to polling for status')
    
    const pollInterval = setInterval(async () => {
      try {
        const status = await getDiscoveryStatus()
        
        if (!status) {
          clearInterval(pollInterval)
          return
        }
        
        discoveryProgress.value = status.progress || 0
        discoveryPhase.value = getPhaseLabel(status.phase || '')
        discoveryMessage.value = status.message || ''
        
        if (status.state === 'complete') {
          discoveryState.value = 'complete'
          clearInterval(pollInterval)
          fetchDiscoveryResult()
        } else if (status.state === 'error' || status.state === 'cancelled') {
          discoveryState.value = status.state
          clearInterval(pollInterval)
        }
      } catch (err) {
        console.error('[Workshop] Poll error:', err)
        clearInterval(pollInterval)
      }
    }, 500)
  }
  
  const startDiscovery = async (params) => {
    try {
      if (discoveryState.value === 'running') {
        console.warn('[Workshop] Discovery already running, ignoring start request')
        return
      }

      if (websocket && websocket.readyState !== WebSocket.CLOSED) {
        console.log('[Workshop] Waiting for previous WebSocket to close...')
        await closeWebSocket()
        await new Promise(resolve => setTimeout(resolve, 100))
      }

      discoveryState.value = 'running'
      discoveryProgress.value = 0
      discoveryPhase.value = 'Starting...'
      discoveryMessage.value = ''
      discoveryResult.value = null
      reconnectAttempts = 0
      
      connectWebSocket()
      
      await new Promise(resolve => setTimeout(resolve, 100))
      
      const response = await axios.post(
        `http://localhost:8000/api/devices/${deviceSerial}/workshop/discover`,
        {
          ...params,
          client_id: clientId.value
        }
      )
      
      if (response.data.success) {
        discoveryId.value = response.data.discovery_id
        toast.info('Discovery started', 'Discovery')
      } else {
        throw new Error(response.data.message || 'Failed to start discovery')
      }
    } catch (err) {
      console.error('[Workshop] Failed to start discovery:', err)
      
      if (err.response?.status === 403) {
        toast.error('Workshop session lost. Another tab has taken control.', 'Discovery')
      } else {
        toast.error(err.response?.data?.detail || 'Failed to start discovery', 'Discovery')
      }
      
      discoveryState.value = 'error'
      await closeWebSocket()
    }
  }
  
  const cancelDiscovery = async () => {
    try {
      await axios.post(
        `http://localhost:8000/api/devices/${deviceSerial}/workshop/discover/cancel`,
        { client_id: clientId.value }
      )
      
      await new Promise(resolve => setTimeout(resolve, 200))
      
      discoveryState.value = 'cancelled'
      await closeWebSocket()
    } catch (err) {
      console.error('[Workshop] Failed to cancel discovery:', err)
      
      if (err.response?.status === 403) {
        toast.error('Workshop session lost. Another tab has taken control.', 'Discovery')
      } else {
        toast.error('Failed to cancel discovery', 'Discovery')
      }
    }
  }
  
  const fetchDiscoveryResult = async () => {
    try {
      const response = await axios.get(
        `http://localhost:8000/api/devices/${deviceSerial}/workshop/discovery/result`
      )
      discoveryResult.value = response.data
      discoveryState.value = 'complete'
      toast.success('Discovery completed successfully', 'Discovery')
    } catch (err) {
      console.error('[Workshop] Failed to fetch discovery result:', err)
      toast.error('Failed to fetch discovery result', 'Discovery')
      discoveryState.value = 'error'
    }
  }
  
  const getDiscoveryStatus = async () => {
    try {
      const response = await axios.get(
        `http://localhost:8000/api/devices/${deviceSerial}/workshop/discovery/status`
      )
      return response.data
    } catch (err) {
      console.error('[Workshop] Failed to get discovery status:', err)
      return null
    }
  }
  
  const clearDiscovery = async () => {
    try {
      await axios.post(
        `http://localhost:8000/api/devices/${deviceSerial}/workshop/discovery/clear`,
        { client_id: clientId.value }
      )
      discoveryState.value = 'idle'
      discoveryProgress.value = 0
      discoveryPhase.value = ''
      discoveryMessage.value = ''
      discoveryId.value = null
      discoveryResult.value = null
      return true
    } catch (err) {
      console.error('[Workshop] Failed to clear discovery:', err)
      return false
    }
  }
  
  onUnmounted(() => {
    closeWebSocket()
  })
  
  return {
    discoveryState,
    discoveryProgress,
    discoveryPhase,
    discoveryMessage,
    discoveryId,
    discoveryResult,
    startDiscovery,
    cancelDiscovery,
    clearDiscovery,
    getDiscoveryStatus
  }
}
