import { ref } from 'vue'
import axios from 'axios'
import { useToast } from '../../../../composables/useToast'

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

  const fetchProcessChurn = async () => {
    try {
      const baseUrl = `http://localhost:8000/api/devices/${deviceSerial}`
      const response = await axios.get(`${baseUrl}/processes/churn`, {
        params: { window: churnWindowSeconds.value }
      })
      churn.value = response.data || churn.value
    } catch (err) {
      console.error('Failed to fetch process churn:', err)
      toast.error('Failed to fetch process churn')
    }
  }

  const setChurnWindow = (seconds) => {
    churnWindowSeconds.value = seconds
  }

  return {
    churn,
    churnWindowSeconds,
    fetchProcessChurn,
    setChurnWindow
  }
}


