import { ref } from 'vue'
import axios from 'axios'
import { useToast } from '../../../../composables/useToast'

export function useProcessActions(deviceSerial, fetchProcesses) {
  const toast = useToast()
  
  const selectedProcess = ref(null)
  const showDetailsModal = ref(false)
  const loadingDetails = ref(false)
  const processDetails = ref(null)
  const processMemoryDetails = ref(null)
  const processNetworkDetails = ref(null)
  
  const processToKill = ref(null)
  const showKillModal = ref(false)
  const killing = ref(false)

  const showProcessDetails = async (process) => {
    selectedProcess.value = process
    showDetailsModal.value = true
    loadingDetails.value = true
    processDetails.value = null
    processMemoryDetails.value = null
    processNetworkDetails.value = null
    
    try {
      const [detailsResponse, memoryResponse, networkResponse] = await Promise.all([
        axios.get(
          `http://localhost:8000/api/devices/${deviceSerial}/processes/${process.pid}`
        ),
        axios.get(
          `http://localhost:8000/api/devices/${deviceSerial}/system/memory`,
          { params: { pid: process.pid } }
        ),
        axios.get(
          `http://localhost:8000/api/devices/${deviceSerial}/system/network`,
          { params: { pid: process.pid } }
        )
      ])

      processDetails.value = detailsResponse.data

      if (memoryResponse.data && memoryResponse.data.focused_process) {
        processMemoryDetails.value = memoryResponse.data.focused_process
      }

      if (networkResponse.data && networkResponse.data.focused_process) {
        processNetworkDetails.value = networkResponse.data.focused_process
      }
    } catch (err) {
      console.error('Failed to fetch process details:', err)
      toast.error('Failed to fetch process details')
    } finally {
      loadingDetails.value = false
    }
  }

  const closeDetailsModal = () => {
    showDetailsModal.value = false
    selectedProcess.value = null
    processDetails.value = null
    processMemoryDetails.value = null
    processNetworkDetails.value = null
  }

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
    selectedProcess,
    showDetailsModal,
    loadingDetails,
    processDetails,
    processMemoryDetails,
    processNetworkDetails,
    processToKill,
    showKillModal,
    killing,
    showProcessDetails,
    closeDetailsModal,
    confirmKill,
    closeKillModal,
    killProcess
  }
}

