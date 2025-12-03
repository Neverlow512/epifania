// Process actions - kill process functionality

import { ref } from 'vue'
import axios from 'axios'
import { useToast } from '../../../../composables/useToast'

export function useProcessActions(deviceSerial, fetchProcesses) {
  const toast = useToast()
  
  const processToKill = ref(null)
  const showKillModal = ref(false)
  const killing = ref(false)

  const confirmKill = (process) => {
    processToKill.value = process
    showKillModal.value = true
  }

  const closeKillModal = () => {
    showKillModal.value = false
    processToKill.value = null
  }

  const killProcess = async () => {
    if (!processToKill.value) return
    
    try {
      killing.value = true
      await axios.post(
        `http://localhost:8000/api/devices/${deviceSerial}/processes/${processToKill.value.pid}/kill`
      )
      toast.success(`Process ${processToKill.value.pid} terminated`)
      closeKillModal()
      await fetchProcesses()
    } catch (err) {
      console.error('Failed to kill process:', err)
      toast.error(err.response?.data?.detail || 'Failed to kill process')
    } finally {
      killing.value = false
    }
  }

  return {
    processToKill,
    showKillModal,
    killing,
    confirmKill,
    closeKillModal,
    killProcess
  }
}
