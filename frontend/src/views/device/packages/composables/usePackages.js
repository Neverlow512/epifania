// Package list management - fetch and cache package list

import { ref } from 'vue'
import axios from 'axios'
import { useToast } from '../../../../composables/useToast'

const ERROR_KEY_PACKAGES = 'packages-fetch'

export function usePackages(deviceSerial) {
  const toast = useToast()

  const packages = ref([])
  const stats = ref({ user: 0, system: 0, running: 0 })
  const loading = ref(false)
  const lastUpdate = ref('Never')
  const activeFilter = ref('user')

  const fetchPackages = async (filter = null) => {
    const filterToUse = filter !== null ? filter : activeFilter.value
    
    try {
      loading.value = true
      const response = await axios.get(
        `http://localhost:8000/api/devices/${deviceSerial}/packages`,
        { params: { filter: filterToUse } }
      )
      
      packages.value = response.data.packages || []
      stats.value = response.data.stats || { user: 0, system: 0, running: 0 }
      lastUpdate.value = new Date().toLocaleTimeString()
      activeFilter.value = filterToUse
      
      toast.clearError(ERROR_KEY_PACKAGES)
    } catch (err) {
      console.error('Failed to fetch packages:', err)
      toast.error(
        err.response?.data?.detail || 'Failed to fetch packages',
        ERROR_KEY_PACKAGES
      )
    } finally {
      loading.value = false
    }
  }

  const refreshPackages = async () => {
    await fetchPackages(activeFilter.value)
  }

  const setFilter = async (filter) => {
    if (filter !== activeFilter.value) {
      await fetchPackages(filter)
    }
  }

  return {
    packages,
    stats,
    loading,
    lastUpdate,
    activeFilter,
    fetchPackages,
    refreshPackages,
    setFilter
  }
}

