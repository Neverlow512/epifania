// Fetches running processes for process selector

import { ref } from 'vue'
import axios from 'axios'
import { useToast } from '../../../../composables/useToast'

const isAppProcess = (process) => {
  const name = process.name || ''
  const hasPackageFormat = name.includes('.') && !name.startsWith('[')
  const isUserProcess = process.user && process.user.startsWith('u0_')
  return hasPackageFormat && isUserProcess
}

const enrichProcess = (process) => {
  const isApp = isAppProcess(process)
  return {
    ...process,
    package_id: isApp ? process.name : null,
    processType: isApp ? 'app' : 'system'
  }
}

export function useRunningProcesses(deviceSerial) {
  const toast = useToast()
  
  const processes = ref([])
  const loading = ref(false)
  
  const fetchProcesses = async () => {
    try {
      loading.value = true
      const response = await axios.get(
        `http://localhost:8000/api/devices/${deviceSerial}/processes`
      )
      
      const rawProcesses = response.data.processes || []
      processes.value = rawProcesses.map(enrichProcess)
      return response.data
    } catch (err) {
      console.error('Failed to fetch processes:', err)
      toast.error('Failed to load processes', 'Processes')
      return null
    } finally {
      loading.value = false
    }
  }
  
  return {
    processes,
    loading,
    fetchProcesses
  }
}

