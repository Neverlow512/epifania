// Primary tab detection using localStorage-based coordination
// Only one tab can be primary at a time across all browser windows/tabs
// Tracks visibility and navigation to ensure proper handoff

import { ref, onMounted, onUnmounted } from 'vue'

function generateClientId() {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}

const STORAGE_KEY = 'packages_primary_tab'
const HEARTBEAT_INTERVAL = 2000
const STALE_THRESHOLD = 5000

export function usePrimaryTab() {
  const clientId = ref(generateClientId())
  const isPrimary = ref(false)
  const isPackagesVisible = ref(true)
  let heartbeatTimer = null
  let checkTimer = null

  const claimPrimary = () => {
    const data = {
      clientId: clientId.value,
      timestamp: Date.now()
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
    isPrimary.value = true
  }

  const releasePrimary = () => {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      try {
        const data = JSON.parse(stored)
        if (data.clientId === clientId.value) {
          localStorage.removeItem(STORAGE_KEY)
          isPrimary.value = false
        }
      } catch (e) {
        // Ignore
      }
    } else {
      isPrimary.value = false
    }
  }

  const checkPrimaryStatus = () => {
    const stored = localStorage.getItem(STORAGE_KEY)
    
    // If no primary exists and we're visible, claim it
    if (!stored) {
      if (isPackagesVisible.value) {
        claimPrimary()
      }
      return
    }

    try {
      const data = JSON.parse(stored)
      const isStale = Date.now() - data.timestamp > STALE_THRESHOLD
      
      // If this is our client ID, maintain primary status
      if (data.clientId === clientId.value) {
        if (isPackagesVisible.value) {
          // Update timestamp to keep primary
          data.timestamp = Date.now()
          localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
          isPrimary.value = true
        } else {
          // We navigated away, release primary
          releasePrimary()
        }
      } else if (isStale && isPackagesVisible.value) {
        // Previous primary is stale and we're visible, claim it
        claimPrimary()
      } else {
        // Another tab is primary
        isPrimary.value = false
      }
    } catch (e) {
      if (isPackagesVisible.value) {
        claimPrimary()
      }
    }
  }

  const handleStorageChange = (event) => {
    if (event.key === STORAGE_KEY) {
      checkPrimaryStatus()
    }
  }

  const handleVisibilityChange = () => {
    // Only try to claim if we become visible and no one is primary
    if (!document.hidden) {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (!stored) {
        checkPrimaryStatus()
      } else {
        // Check if current primary is stale
        try {
          const data = JSON.parse(stored)
          const isStale = Date.now() - data.timestamp > STALE_THRESHOLD
          if (isStale) {
            checkPrimaryStatus()
          }
        } catch (e) {
          checkPrimaryStatus()
        }
      }
    }
  }

  onMounted(() => {
    isPackagesVisible.value = true
    checkPrimaryStatus()
    
    heartbeatTimer = setInterval(() => {
      if (isPrimary.value && isPackagesVisible.value) {
        const data = {
          clientId: clientId.value,
          timestamp: Date.now()
        }
        localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
      } else if (isPrimary.value && !isPackagesVisible.value) {
        // Release if we're primary but not visible
        releasePrimary()
      }
    }, HEARTBEAT_INTERVAL)

    checkTimer = setInterval(checkPrimaryStatus, HEARTBEAT_INTERVAL)

    window.addEventListener('storage', handleStorageChange)
    document.addEventListener('visibilitychange', handleVisibilityChange)
  })

  onUnmounted(() => {
    if (heartbeatTimer) clearInterval(heartbeatTimer)
    if (checkTimer) clearInterval(checkTimer)
    window.removeEventListener('storage', handleStorageChange)
    document.removeEventListener('visibilitychange', handleVisibilityChange)
    releasePrimary()
  })

  return { isPrimary, setVisible: (visible) => { isPackagesVisible.value = visible } }
}
