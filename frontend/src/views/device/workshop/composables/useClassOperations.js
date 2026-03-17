import { ref } from 'vue'
import axios from 'axios'
import { useToast } from '../../../../composables/useToast'

const CRITICAL_ERROR_TYPES = ['SESSION_DEAD', 'SESSION_DETACHED', 'TRANSPORT_ERROR']

export function useClassOperations(deviceSerial, clientId) {
  const toast = useToast()
  const scanning = ref(false)
  const extracting = ref(false)
  const sessionLost = ref(false)
  const sessionLostData = ref(null)
  
  const hasCriticalErrors = (errors) => {
    if (!errors || !Array.isArray(errors)) return false
    return errors.some(e => CRITICAL_ERROR_TYPES.includes(e.error_type))
  }
  
  const scanClassLoader = async (classNames, packageId) => {
    if (!classNames || classNames.length === 0) {
      return { results: [], sessionLost: false }
    }
    
    scanning.value = true
    sessionLost.value = false
    sessionLostData.value = null
    
    try {
      const response = await axios.post(
        `http://localhost:8000/api/devices/${deviceSerial}/workshop/scan-classloader`,
        { 
          class_names: classNames, 
          client_id: clientId.value,
          package_id: packageId
        }
      )
      
      if (response.data.session_lost) {
        sessionLost.value = true
        sessionLostData.value = {
          operation: 'scan_classloader',
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
          toast.error(`${errorCount} critical errors during scan`, 'ClassLoader')
        } else if (errorCount > 0) {
          toast.warning(`Scanned ${response.data.total} classes (${errorCount} errors)`, 'ClassLoader')
        } else {
          toast.success(`Scanned ${response.data.total} classes`, 'ClassLoader')
        }
        return { results: response.data.results, sessionLost: false }
      } else {
        throw new Error('Scan failed')
      }
    } catch (err) {
      console.error('[ClassOperations] Scan ClassLoader failed:', err)
      
      if (err.response?.status === 403) {
        toast.error('Session lost. Another tab has taken control.', 'ClassLoader')
      } else if (err.response?.status === 400) {
        toast.error(err.response.data?.detail || 'No active Frida session', 'ClassLoader')
      } else if (!sessionLost.value) {
        toast.error('Failed to scan ClassLoader', 'ClassLoader')
      }
      throw err
    } finally {
      scanning.value = false
    }
  }
  
  const extractMethods = async (classNames, packageId) => {
    if (!classNames || classNames.length === 0) {
      return { results: [], sessionLost: false }
    }
    
    extracting.value = true
    sessionLost.value = false
    sessionLostData.value = null
    
    try {
      const response = await axios.post(
        `http://localhost:8000/api/devices/${deviceSerial}/workshop/extract-methods`,
        { 
          class_names: classNames, 
          client_id: clientId.value,
          package_id: packageId
        }
      )
      
      if (response.data.session_lost) {
        sessionLost.value = true
        sessionLostData.value = {
          operation: 'extract_methods',
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
          toast.error(`${errorCount} critical errors during extraction`, 'Methods')
        } else if (errorCount > 0) {
          toast.warning(`Extracted methods for ${response.data.total} classes (${errorCount} errors)`, 'Methods')
        } else {
          toast.success(`Extracted methods for ${response.data.total} classes`, 'Methods')
        }
        return { results: response.data.results, sessionLost: false }
      } else {
        throw new Error('Extraction failed')
      }
    } catch (err) {
      console.error('[ClassOperations] Extract methods failed:', err)
      
      if (err.response?.status === 403) {
        toast.error('Session lost. Another tab has taken control.', 'Methods')
      } else if (err.response?.status === 400) {
        toast.error(err.response.data?.detail || 'No active Frida session', 'Methods')
      } else if (!sessionLost.value) {
        toast.error('Failed to extract methods', 'Methods')
      }
      throw err
    } finally {
      extracting.value = false
    }
  }
  
  const cancelOperation = async (operationType) => {
    try {
      await axios.post(
        `http://localhost:8000/api/devices/${deviceSerial}/workshop/cancel-operation`,
        { 
          operation_type: operationType, 
          client_id: clientId.value 
        }
      )
      toast.info(`${operationType} cancelled`, 'Operation')
    } catch (err) {
      console.error('[ClassOperations] Cancel failed:', err)
    }
  }
  
  const clearSessionLost = () => {
    sessionLost.value = false
    sessionLostData.value = null
  }
  
  return {
    scanning,
    extracting,
    sessionLost,
    sessionLostData,
    scanClassLoader,
    extractMethods,
    cancelOperation,
    clearSessionLost
  }
}
