import { ref, computed } from 'vue'
import axios from 'axios'
import { useToast } from '../../../../composables/useToast'

export function useObserver(deviceSerial, clientId) {
  const toast = useToast()
  
  const observerState = ref('idle')
  const sessionName = ref('')
  const sessionPath = ref('')
  const timeLimit = ref(null)
  const currentSessionNumber = ref(null)
  const observedMethods = ref(new Map())
  
  const isObserving = computed(() => observerState.value === 'observing')
  
  const generateDefaultSessionName = () => {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('T').join('_').substring(0, 19)
    return `session_${timestamp}`
  }
  
  const startObservation = async (hooks, packageId) => {
    if (!hooks || hooks.length === 0) {
      toast.warning('No methods selected for observation', 'Observer')
      return { success: false }
    }
    
    observerState.value = 'observing'
    
    try {
      const payload = {
        client_id: clientId.value,
        app_package: packageId,
        hooks: hooks
      }
      
      if (timeLimit.value && timeLimit.value > 0) {
        payload.time_limit = timeLimit.value
      }
      
      const response = await axios.post(
        `http://localhost:8000/api/devices/${deviceSerial}/observer/start`,
        payload
      )
      
      if (response.data.success) {
        const backendSessionName = response.data.session_name
        sessionName.value = backendSessionName
        sessionPath.value = response.data.session_path || ''
        
        hooks.forEach(hook => {
          const methodKey = `${hook.class_name}::${hook.method_name}::${hook.signature || ''}`
          const existingHistory = observedMethods.value.get(methodKey) || []
          
          const newEntry = {
            session_name: backendSessionName,
            timestamp: new Date().toISOString(),
            session_path: response.data.session_path || ''
          }
          
          observedMethods.value.set(methodKey, [...existingHistory, newEntry])
        })
        
        toast.success(`Observer started: ${backendSessionName}`, 'Observer')
        return { success: true, sessionName: backendSessionName, observedMethods: observedMethods.value }
      } else {
        throw new Error(response.data.message || 'Failed to start observer')
      }
    } catch (err) {
      console.error('[Observer] Start failed:', err)
      observerState.value = 'idle'
      
      if (err.response?.status === 403) {
        toast.error('Session not owned by this client', 'Observer')
      } else if (err.response?.status === 400) {
        toast.error(err.response.data?.detail || 'No active Frida session', 'Observer')
      } else {
        toast.error(err.response?.data?.message || 'Failed to start observer', 'Observer')
      }
      
      return { success: false }
    }
  }
  
  const stopObservation = async () => {
    try {
      const response = await axios.post(
        `http://localhost:8000/api/devices/${deviceSerial}/observer/stop`,
        { client_id: clientId.value }
      )
      
      if (response.data.success) {
        observerState.value = 'stopped'
        toast.info('Observer stopped', 'Observer')
        return { success: true }
      } else {
        throw new Error(response.data.message || 'Failed to stop observer')
      }
    } catch (err) {
      console.error('[Observer] Stop failed:', err)
      
      if (err.response?.status === 403) {
        toast.error('Session not owned by this client', 'Observer')
      } else {
        toast.error(err.response?.data?.message || 'Failed to stop observer', 'Observer')
      }
      
      return { success: false }
    }
  }
  
  const resetState = () => {
    observerState.value = 'idle'
    sessionName.value = ''
    sessionPath.value = ''
  }
  
  const getMethodObservationHistory = (className, methodName, signature) => {
    const methodKey = `${className}::${methodName}::${signature || ''}`
    return observedMethods.value.get(methodKey) || []
  }
  
  return {
    observerState,
    sessionName,
    sessionPath,
    timeLimit,
    isObserving,
    observedMethods,
    startObservation,
    stopObservation,
    resetState,
    getMethodObservationHistory
  }
}
