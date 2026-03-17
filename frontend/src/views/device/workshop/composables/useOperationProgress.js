// Tracks progress of batch operations via WebSocket

import { ref, computed, onUnmounted } from 'vue'
import axios from 'axios'

export function useOperationProgress(deviceSerial, operationType, clientId) {
  const inProgress = ref(false)
  const current = ref(0)
  const total = ref(0)
  const currentItem = ref('')
  const cancelled = ref(false)
  const completed = ref(false)
  
  let websocket = null
  let pollInterval = null
  
  const progress = computed(() => {
    if (total.value === 0) return 0
    return Math.round((current.value / total.value) * 100)
  })
  
  const startTracking = () => {
    inProgress.value = true
    cancelled.value = false
    completed.value = false
    current.value = 0
    total.value = 0
    currentItem.value = ''
    
    const wsUrl = `ws://localhost:8000/ws/devices/${deviceSerial}/workshop/operation/${operationType}`
    
    try {
      websocket = new WebSocket(wsUrl)
      
      websocket.onopen = () => {
        console.log(`[Operation] WebSocket connected for ${operationType}`)
      }
      
      websocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          
          if (data.active === false) {
            return
          }
          
          current.value = data.current || 0
          total.value = data.total || 0
          currentItem.value = data.current_item || ''
          
          if (data.completed) {
            completed.value = true
            stopTracking()
          }
          
          if (data.cancelled) {
            cancelled.value = true
            stopTracking()
          }
        } catch (err) {
          console.error('[Operation] Failed to parse WebSocket message:', err)
        }
      }
      
      websocket.onerror = (error) => {
        console.error('[Operation] WebSocket error:', error)
        fallbackToPolling()
      }
      
      websocket.onclose = () => {
        console.log(`[Operation] WebSocket closed for ${operationType}`)
      }
    } catch (err) {
      console.error('[Operation] Failed to connect WebSocket:', err)
      fallbackToPolling()
    }
  }
  
  const fallbackToPolling = () => {
    if (pollInterval) return
    
    console.log('[Operation] Falling back to polling')
    pollInterval = setInterval(async () => {
      try {
        const response = await axios.get(
          `http://localhost:8000/api/devices/${deviceSerial}/workshop/operation/${operationType}/progress`
        )
        
        const data = response.data
        
        if (!data.active) {
          stopTracking()
          return
        }
        
        current.value = data.current || 0
        total.value = data.total || 0
        currentItem.value = data.current_item || ''
        
        if (data.completed || data.cancelled) {
          completed.value = data.completed || false
          cancelled.value = data.cancelled || false
          stopTracking()
        }
      } catch (err) {
        console.error('[Operation] Poll error:', err)
      }
    }, 300)
  }
  
  const stopTracking = () => {
    if (websocket) {
      websocket.close()
      websocket = null
    }
    
    if (pollInterval) {
      clearInterval(pollInterval)
      pollInterval = null
    }
    
    inProgress.value = false
  }
  
  const cancelOperation = async () => {
    try {
      await axios.post(
        `http://localhost:8000/api/devices/${deviceSerial}/workshop/cancel-operation`,
        { operation_type: operationType, client_id: clientId.value }
      )
      cancelled.value = true
    } catch (err) {
      console.error('[Operation] Failed to cancel:', err)
    }
  }
  
  const reset = () => {
    stopTracking()
    current.value = 0
    total.value = 0
    currentItem.value = ''
    cancelled.value = false
    completed.value = false
  }
  
  onUnmounted(() => {
    stopTracking()
  })
  
  return {
    inProgress,
    current,
    total,
    currentItem,
    progress,
    cancelled,
    completed,
    startTracking,
    stopTracking,
    cancelOperation,
    reset
  }
}
