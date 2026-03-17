import { ref, computed, onUnmounted } from 'vue'

export function useObserverStats(deviceSerial) {
  const isConnected = ref(false)
  const sessionStatus = ref(null)
  const hooks = ref([])
  const sortBy = ref('top_activity')
  const filterBy = ref('all')
  const maxCallRate = ref(10)
  
  let websocket = null
  let reconnectAttempts = 0
  const MAX_RECONNECT_ATTEMPTS = 3

  let lastUpdateMs = 0
  let prevTotalCalls = 0
  const prevHookCounts = new Map()
  const rateEma = new Map()
  const EMA_ALPHA = 0.35

  const round2 = (n) => Math.round((n + Number.EPSILON) * 100) / 100

  const updateMaxCallRate = (updatedHooks) => {
    const rates = updatedHooks.map(h => h.call_rate || 0)
    const observedMax = rates.length ? Math.max(...rates) : 0

    // Add headroom so the top hook doesn't constantly peg 100%.
    // Keep it stable (avoid snapping) so the gauge doesn't jump.
    const target = Math.max(round2(observedMax * 1.35), 5)
    const current = maxCallRate.value || 10

    // Raise reasonably fast, decay slowly.
    const alpha = target > current ? 0.25 : 0.06
    maxCallRate.value = round2(current + (target - current) * alpha)
  }
  
  const sortedHooks = computed(() => {
    let filtered = [...hooks.value]
    
    if (filterBy.value === 'active_only') {
      filtered = filtered.filter(h => h.call_count > 0)
    } else if (filterBy.value === 'with_errors') {
      filtered = filtered.filter(h => h.error_count > 0)
    }
    
    filtered.sort((a, b) => {
      switch (sortBy.value) {
        case 'top_activity':
          return (b.call_rate || 0) - (a.call_rate || 0)
        case 'most_calls':
          return (b.call_count || 0) - (a.call_count || 0)
        case 'most_errors':
          return (b.error_count || 0) - (a.error_count || 0)
        case 'alphabetical':
          return (a.method_name || '').localeCompare(b.method_name || '')
        default:
          return 0
      }
    })
    
    return filtered
  })
  
  const connectWebSocket = () => {
    if (websocket && websocket.readyState === WebSocket.OPEN) {
      return
    }
    
    const wsUrl = `ws://localhost:8000/ws/devices/${deviceSerial}/instrumentation/observer`
    
    try {
      websocket = new WebSocket(wsUrl)
      
      websocket.onopen = () => {
        isConnected.value = true
        reconnectAttempts = 0
      }
      
      websocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          
          if (data.type === 'status_update') {
            const now = Date.now()
            const dt = lastUpdateMs ? (now - lastUpdateMs) / 1000 : 0
            lastUpdateMs = now

            const status = data.status || null
            if (status) {
              const totalCalls = status.total_calls || 0
              if (dt > 0) {
                const cps = (totalCalls - prevTotalCalls) / dt
                status.calls_per_second = round2(Math.max(cps, 0))
              }
              prevTotalCalls = totalCalls
            }
            sessionStatus.value = status

            if (data.top_hooks && Array.isArray(data.top_hooks)) {
              const updated = data.top_hooks.map(h => {
                const id = h.hook_id
                const callCount = h.call_count || 0
                const prev = prevHookCounts.has(id) ? prevHookCounts.get(id) : callCount
                const delta = callCount - prev
                prevHookCounts.set(id, callCount)

                let rate = h.call_rate || 0
                if (dt > 0) {
                  rate = Math.max(delta / dt, 0)
                }

                const prevEma = rateEma.has(id) ? rateEma.get(id) : rate
                const ema = EMA_ALPHA * rate + (1 - EMA_ALPHA) * prevEma
                rateEma.set(id, ema)

                return {
                  ...h,
                  call_rate: round2(ema)
                }
              })
              hooks.value = updated
              updateMaxCallRate(updated)
            }
          } else if (data.type === 'session_ended') {
            setTimeout(() => {
              disconnectWebSocket()
            }, 3000)
          }
        } catch (err) {
          // swallow parse errors
        }
      }
      
      websocket.onerror = () => {
        isConnected.value = false
      }
      
      websocket.onclose = () => {
        isConnected.value = false
        
        if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
          const delay = Math.pow(2, reconnectAttempts) * 1000
          reconnectAttempts++
          setTimeout(connectWebSocket, delay)
        }
      }
    } catch (err) {
      isConnected.value = false
    }
  }
  
  const disconnectWebSocket = () => {
    if (websocket) {
      websocket.close()
      websocket = null
    }
    isConnected.value = false
    sessionStatus.value = null
    hooks.value = []

    lastUpdateMs = 0
    prevTotalCalls = 0
    prevHookCounts.clear()
    rateEma.clear()
    maxCallRate.value = 10
  }
  
  const setSortBy = (value) => {
    sortBy.value = value
  }
  
  const setFilterBy = (value) => {
    filterBy.value = value
  }
  
  onUnmounted(() => {
    disconnectWebSocket()
  })
  
  return {
    isConnected,
    sessionStatus,
    hooks,
    sortBy,
    filterBy,
    sortedHooks,
    maxCallRate,
    connectWebSocket,
    disconnectWebSocket,
    setSortBy,
    setFilterBy
  }
}
