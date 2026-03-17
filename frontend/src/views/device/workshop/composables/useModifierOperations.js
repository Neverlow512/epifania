import { ref } from 'vue'
import axios from 'axios'
import { useToast } from '../../../../composables/useToast'

const CRITICAL_ERROR_TYPES = ['SESSION_DEAD', 'SESSION_DETACHED', 'TRANSPORT_ERROR']

export function useModifierOperations(deviceSerial, clientId) {
  const toast = useToast()
  const scanning = ref(false)
  const sessionLost = ref(false)
  const sessionLostData = ref(null)
  
  const hasCriticalErrors = (errors) => {
    if (!errors || !Array.isArray(errors)) return false
    return errors.some(e => CRITICAL_ERROR_TYPES.includes(e.error_type))
  }
  
  const scanModifiers = async (classNames, scanTypes, packageId) => {
    if (!classNames || classNames.length === 0) {
      return { results: [], sessionLost: false }
    }
    
    if (!scanTypes || scanTypes.length === 0) {
      toast.warning('No scan types selected', 'Modifiers')
      return { results: [], sessionLost: false }
    }
    
    scanning.value = true
    sessionLost.value = false
    sessionLostData.value = null
    
    try {
      const response = await axios.post(
        `http://localhost:8000/api/devices/${deviceSerial}/workshop/scan-modifiers`,
        { 
          class_names: classNames, 
          scan_types: scanTypes,
          client_id: clientId.value,
          package_id: packageId
        }
      )
      
      if (response.data.session_lost) {
        sessionLost.value = true
        sessionLostData.value = {
          operation: 'scan_modifiers',
          processed: response.data.results?.length || 0,
          total: classNames.length,
          errors: response.data.errors || []
        }
        toast.error('Frida agent crashed during operation', 'Session Lost')
        return { 
          results: response.data.results || [], 
          sessionLost: true, 
          sessionLostData: sessionLostData.value 
        }
      }
      
      if (response.data.success) {
        const errorCount = response.data.error_count || 0
        if (hasCriticalErrors(response.data.errors)) {
          toast.error(`${errorCount} critical errors during scan`, 'Modifiers')
        } else if (errorCount > 0) {
          toast.warning(`Scanned ${response.data.total} classes (${errorCount} errors)`, 'Modifiers')
        } else {
          toast.success(`Scanned ${response.data.total} classes for modifiers`, 'Modifiers')
        }
        return { results: response.data.results, sessionLost: false }
      } else {
        throw new Error('Scan failed')
      }
    } catch (err) {
      console.error('[ModifierOperations] Scan modifiers failed:', err)
      
      if (err.response?.status === 403) {
        toast.error('Session lost. Another tab has taken control.', 'Modifiers')
      } else if (err.response?.status === 400) {
        toast.error(err.response.data?.detail || 'No active Frida session', 'Modifiers')
      } else if (!sessionLost.value) {
        toast.error('Failed to scan modifiers', 'Modifiers')
      }
      throw err
    } finally {
      scanning.value = false
    }
  }
  
  const clearSessionLost = () => {
    sessionLost.value = false
    sessionLostData.value = null
  }
  
  return {
    scanning,
    sessionLost,
    sessionLostData,
    scanModifiers,
    clearSessionLost
  }
}
