import { ref, computed, watch } from 'vue'
import axios from 'axios'
import { getWorkshopClientId } from './workshopClientId'

const API_BASE = 'http://localhost:8000/api/devices'

export function useTempStateRetention(deviceSerial, packageId) {
  const retentionLimit = ref(10)
  const unsavedTempCount = ref(0)
  const loading = ref(false)
  const saving = ref(false)
  const error = ref(null)
  
  const effectiveLimit = computed(() => Math.max(retentionLimit.value, unsavedTempCount.value))
  
  const minLimit = computed(() => Math.max(1, unsavedTempCount.value))
  
  let saveTimeout = null
  
  async function loadRetentionConfig() {
    if (!packageId.value) return
    
    loading.value = true
    error.value = null
    
    try {
      const response = await axios.get(
        `${API_BASE}/${deviceSerial}/workshop/config/retention/${encodeURIComponent(packageId.value)}`
      )
      
      retentionLimit.value = response.data.retention_limit
      unsavedTempCount.value = response.data.unsaved_temp_count
    } catch (e) {
      error.value = e.message
      console.error('[Retention] Failed to load config:', e)
    } finally {
      loading.value = false
    }
  }
  
  async function saveRetentionConfig(newLimit) {
    if (!packageId.value) return false
    
    saving.value = true
    error.value = null
    
    try {
      const clientId = getWorkshopClientId()
      
      const response = await axios.put(
        `${API_BASE}/${deviceSerial}/workshop/config/retention/${encodeURIComponent(packageId.value)}`,
        {
          retention_limit: newLimit,
          client_id: clientId
        }
      )
      
      retentionLimit.value = response.data.retention_limit
      unsavedTempCount.value = response.data.unsaved_temp_count
      return true
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
      console.error('[Retention] Failed to save config:', e)
      return false
    } finally {
      saving.value = false
    }
  }
  
  function debouncedSave(newLimit) {
    if (saveTimeout) {
      clearTimeout(saveTimeout)
    }
    
    saveTimeout = setTimeout(() => {
      saveRetentionConfig(newLimit)
    }, 1000)
  }
  
  function increment() {
    const newValue = retentionLimit.value + 1
    retentionLimit.value = newValue
    debouncedSave(newValue)
  }
  
  function decrement() {
    const newValue = Math.max(minLimit.value, retentionLimit.value - 1)
    if (newValue !== retentionLimit.value) {
      retentionLimit.value = newValue
      debouncedSave(newValue)
    }
  }
  
  function updateValue(newValue) {
    const validValue = Math.max(minLimit.value, parseInt(newValue) || minLimit.value)
    if (validValue !== retentionLimit.value) {
      retentionLimit.value = validValue
      debouncedSave(validValue)
    }
  }
  
  watch(packageId, (newPackageId) => {
    if (newPackageId) {
      loadRetentionConfig()
    }
  }, { immediate: true })
  
  return {
    retentionLimit,
    unsavedTempCount,
    effectiveLimit,
    minLimit,
    loading,
    saving,
    error,
    loadRetentionConfig,
    saveRetentionConfig,
    increment,
    decrement,
    updateValue
  }
}
