// Auto-save temp state management for Phase 3 persistence
import { ref } from 'vue'
import axios from 'axios'

export function useTempState(deviceSerial, clientId, packageId) {
  const syncing = ref(false)
  const lastSyncTime = ref(null)
  const syncInterval = 30000 // 30 seconds
  let intervalId = null
  
  const serializeClassStates = (classStatesMap) => {
    // Convert Map to plain object for JSON
    if (!classStatesMap || typeof classStatesMap.forEach !== 'function') {
      return {}
    }
    
    const obj = {}
    classStatesMap.forEach((state, className) => {
      obj[className] = state
    })
    return obj
  }
  
  const syncTempState = async (classStates, fullData = null) => {
    if (syncing.value) return // Skip if already syncing
    if (!packageId.value) return // No package selected
    
    try {
      syncing.value = true
      
      const serializedStates = serializeClassStates(classStates.value)
      
      // Only sync if there are states to save
      if (Object.keys(serializedStates).length === 0) {
        console.log('[TempState] No states to sync, skipping')
        return
      }
      
      await axios.post(
        `http://localhost:8000/api/devices/${deviceSerial}/workshop/sync-temp-state`,
        {
          package_id: packageId.value,
          client_id: clientId.value,
          class_states: serializedStates,
          full_data: fullData
        }
      )
      
      lastSyncTime.value = Date.now()
      console.log('[TempState] Auto-saved to temp:', Object.keys(serializedStates).length, 'class states')
    } catch (err) {
      console.error('[TempState] Auto-save failed:', err)
      // Non-fatal - temp save failure doesn't break workflow
    } finally {
      syncing.value = false
    }
  }
  
  const startAutoSave = (classStates) => {
    if (intervalId) {
      console.log('[TempState] Auto-save already running')
      return
    }
    
    console.log('[TempState] Starting auto-save interval (30s)')
    
    // Auto-save at intervals
    intervalId = setInterval(() => {
      if (packageId.value) {
        syncTempState(classStates)
      }
    }, syncInterval)
  }
  
  const stopAutoSave = () => {
    if (intervalId) {
      clearInterval(intervalId)
      intervalId = null
      console.log('[TempState] Stopped auto-save interval')
    }
  }
  
  const triggerManualSync = (classStates, fullData = null) => {
    // Trigger immediate sync (after operations)
    console.log('[TempState] Manual sync triggered')
    syncTempState(classStates, fullData)
  }
  
  const checkRecovery = async () => {
    if (!packageId.value) return null
    
    try {
      const response = await axios.get(
        `http://localhost:8000/api/devices/${deviceSerial}/workshop/recovery-check/${packageId.value}`
      )
      return response.data
    } catch (error) {
      console.error('[TempState] Recovery check failed:', error)
      return null
    }
  }
  
  const recoverTempState = async () => {
    if (!packageId.value) return null
    
    try {
      const response = await axios.post(
        `http://localhost:8000/api/devices/${deviceSerial}/workshop/recover-temp-state`,
        {
          package_id: packageId.value,
          client_id: clientId.value
        }
      )
      console.log('[TempState] Recovery successful')
      return response.data
    } catch (error) {
      console.error('[TempState] Recovery failed:', error)
      return null
    }
  }
  
  const clearTempState = async () => {
    if (!packageId.value) return false
    
    try {
      await axios.post(
        `http://localhost:8000/api/devices/${deviceSerial}/workshop/clear-temp-state`,
        {
          package_id: packageId.value,
          client_id: clientId.value
        }
      )
      console.log('[TempState] Temp state cleared')
      return true
    } catch (error) {
      console.error('[TempState] Clear failed:', error)
      return false
    }
  }
  
  return {
    syncing,
    lastSyncTime,
    syncTempState,
    startAutoSave,
    stopAutoSave,
    triggerManualSync,
    checkRecovery,
    recoverTempState,
    clearTempState
  }
}
