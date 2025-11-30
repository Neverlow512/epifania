import { ref } from 'vue'
import axios from 'axios'
import { useToast } from '../../../../composables/useToast'

const ERROR_KEY_CHURN = 'process-churn'
const ERROR_KEY_HISTORY = 'process-churn-history'

export function useProcessChurn(deviceSerial) {
  const toast = useToast()

  const churnWindowSeconds = ref(60)
  const churn = ref({
    window_seconds: 60,
    spawned_count: 0,
    killed_count: 0,
    net_change: 0,
    recent_spawned: [],
    recent_killed: []
  })

  const churnHistory = ref({
    events: [],
    total_events: 0,
    total_spawned: 0,
    total_killed: 0,
    limited: false
  })
  const loadingHistory = ref(false)

  const fetchProcessChurn = async () => {
    try {
      const baseUrl = `http://localhost:8000/api/devices/${deviceSerial}`
      const response = await axios.get(`${baseUrl}/processes/churn`, {
        params: { window: churnWindowSeconds.value }
      })
      churn.value = response.data || churn.value
      toast.clearError(ERROR_KEY_CHURN)
    } catch (err) {
      console.error('Failed to fetch process churn:', err)
      toast.error('Failed to fetch process churn', ERROR_KEY_CHURN)
    }
  }

  const fetchChurnHistory = async (limit = 500) => {
    try {
      loadingHistory.value = true
      const baseUrl = `http://localhost:8000/api/devices/${deviceSerial}`
      const response = await axios.get(`${baseUrl}/processes/churn/history`, {
        params: { limit }
      })
      churnHistory.value = response.data || churnHistory.value
      toast.clearError(ERROR_KEY_HISTORY)
    } catch (err) {
      console.error('Failed to fetch churn history:', err)
      toast.error('Failed to fetch churn history', ERROR_KEY_HISTORY)
    } finally {
      loadingHistory.value = false
    }
  }

  const setChurnWindow = (seconds) => {
    churnWindowSeconds.value = seconds
  }

  return {
    churn,
    churnWindowSeconds,
    churnHistory,
    loadingHistory,
    fetchProcessChurn,
    fetchChurnHistory,
    setChurnWindow
  }
}


