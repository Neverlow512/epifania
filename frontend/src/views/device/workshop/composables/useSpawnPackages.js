import { ref } from 'vue'
import axios from 'axios'
import { useToast } from '../../../../composables/useToast'

export function useSpawnPackages(deviceSerial) {
  const toast = useToast()
  
  const packages = ref([])
  const loading = ref(false)
  
  const fetchPackages = async (includeSystemPackages = false) => {
    try {
      loading.value = true
      const filter = includeSystemPackages ? 'all' : 'user'
      const response = await axios.get(
        `http://localhost:8000/api/devices/${deviceSerial}/workshop/packages`,
        { params: { filter } }
      )
      
      packages.value = response.data.packages || []
    } catch (err) {
      console.error('Failed to fetch packages for spawn:', err)
      toast.error(
        err.response?.data?.detail || 'Failed to fetch packages',
        'Spawn Packages'
      )
    } finally {
      loading.value = false
    }
  }
  
  return {
    packages,
    loading,
    fetchPackages
  }
}
