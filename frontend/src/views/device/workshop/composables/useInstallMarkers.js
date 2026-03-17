// Handles fetching and comparing install markers for app identification
import { ref } from 'vue'
import axios from 'axios'

export function useInstallMarkers(deviceSerial) {
  const loading = ref(false)
  const error = ref(null)
  
  const fetchInstallMarkers = async (packageId) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await axios.get(
        `http://localhost:8000/api/devices/${deviceSerial}/workshop/install-markers/${packageId}`
      )
      
      return response.data
    } catch (err) {
      if (err.response?.status === 404) {
        error.value = 'Package not installed'
        return null
      }
      error.value = err.message || 'Failed to fetch install markers'
      console.error('Failed to fetch install markers:', err)
      return null
    } finally {
      loading.value = false
    }
  }
  
  const compareMarkers = (savedMarkers, currentMarkers) => {
    if (!savedMarkers) {
      return { status: 'legacy', label: 'Legacy', color: 'neutral' }
    }
    
    if (!currentMarkers) {
      return { status: 'not_installed', label: 'Not Installed', color: 'neutral' }
    }
    
    if (savedMarkers.first_install_time === currentMarkers.first_install_time &&
        savedMarkers.version_code === currentMarkers.version_code) {
      return { status: 'exact_match', label: 'Same Installation', color: 'success' }
    }
    
    if (savedMarkers.version_code === currentMarkers.version_code) {
      return { status: 'same_version', label: 'Same Version', color: 'warning' }
    }
    
    if (savedMarkers.signing_cert_short && 
        savedMarkers.signing_cert_short === currentMarkers.signing_cert_short) {
      return { status: 'updated', label: 'App Updated', color: 'info' }
    }
    
    return { status: 'not_installed', label: 'Not Installed', color: 'neutral' }
  }
  
  const checkDiscoveryMatch = async (savedDiscovery) => {
    const savedMarkers = savedDiscovery?.metadata?.install_markers
    const packageId = savedDiscovery?.metadata?.package_id
    
    if (!packageId) {
      return { status: 'legacy', label: 'Legacy', color: 'neutral' }
    }
    
    if (!savedMarkers) {
      try {
        const currentMarkers = await fetchInstallMarkers(packageId)
        if (currentMarkers) {
          return { status: 'installed_legacy', label: 'Installed', color: 'success' }
        }
        return { status: 'not_installed', label: 'Not Installed', color: 'neutral' }
      } catch {
        return { status: 'legacy', label: 'Legacy', color: 'neutral' }
      }
    }
    
    const currentMarkers = await fetchInstallMarkers(packageId)
    return compareMarkers(savedMarkers, currentMarkers)
  }
  
  return {
    loading,
    error,
    fetchInstallMarkers,
    compareMarkers,
    checkDiscoveryMatch
  }
}

