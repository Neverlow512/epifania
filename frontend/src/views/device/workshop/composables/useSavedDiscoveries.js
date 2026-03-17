// Manages saved discoveries: list, load, save, delete

import { ref } from 'vue'
import axios from 'axios'
import { useToast } from '../../../../composables/useToast'

export function useSavedDiscoveries(deviceSerial, clientId) {
  const toast = useToast()
  
  const savedList = ref([])
  const loading = ref(false)
  const saving = ref(false)
  const selectedDiscovery = ref(null)
  const filterMode = ref('all')
  
  const listSavedDiscoveries = async (packageId) => {
    try {
      loading.value = true
      const response = await axios.get(
        `http://localhost:8000/api/devices/${deviceSerial}/workshop/discoveries/${packageId}`
      )
      savedList.value = response.data.discoveries || []
      return response.data
    } catch (err) {
      console.error('Failed to list saved discoveries:', err)
      toast.error('Failed to load saved discoveries', 'Storage')
      return null
    } finally {
      loading.value = false
    }
  }
  
  const loadDiscoveryMetadata = async (packageId, folder) => {
    try {
      const response = await axios.get(
        `http://localhost:8000/api/devices/${deviceSerial}/workshop/load/${packageId}/${folder}`
      )
      if (response.data && response.data.metadata) {
        const meta = response.data.metadata
        return {
          totalClasses: meta.stats?.java?.classes_included || 0,
          totalMethods: meta.stats?.java?.total_methods || 0,
          totalModules: meta.stats?.native?.modules_included || 0,
          totalExports: meta.stats?.native?.total_exports || 0
        }
      }
      return null
    } catch (err) {
      console.debug(`Failed to load metadata for ${packageId}/${folder}:`, err)
      return null
    }
  }
  
  const listAllDiscoveries = async () => {
    try {
      loading.value = true
      const response = await axios.get(
        `http://localhost:8000/api/devices/workshop/discoveries`
      )
      savedList.value = response.data.packages || []
      return response.data
    } catch (err) {
      console.error('Failed to list all discoveries:', err)
      toast.error('Failed to load discoveries', 'Storage')
      return null
    } finally {
      loading.value = false
    }
  }
  
  const loadDiscovery = async (packageId, folder) => {
    try {
      loading.value = true
      const response = await axios.get(
        `http://localhost:8000/api/devices/${deviceSerial}/workshop/load/${packageId}/${folder}`
      )
      selectedDiscovery.value = response.data
      toast.success('Discovery loaded successfully', 'Storage')
      return response.data
    } catch (err) {
      console.error('Failed to load discovery:', err)
      toast.error('Failed to load discovery', 'Storage')
      return null
    } finally {
      loading.value = false
    }
  }
  
  // TODO: TEMPORARY FALLBACK - checkBackendHasResult can be removed once backend temp persistence is implemented
  const checkBackendHasResult = async () => {
    try {
      const response = await axios.get(
        `http://localhost:8000/api/devices/${deviceSerial}/workshop/discovery/result`
      )
      return response.data ? true : false
    } catch (err) {
      if (err.response?.status === 404) {
        return false
      }
      console.error('Failed to check backend result:', err)
      return false
    }
  }
  
  const saveDiscovery = async (packageId, packageVersion, customName = null, savePath = null) => {
    try {
      saving.value = true
      const response = await axios.post(
        `http://localhost:8000/api/devices/${deviceSerial}/workshop/save`,
        {
          package_id: packageId,
          package_version: packageVersion,
          custom_name: customName,
          save_path: savePath,
          client_id: clientId.value
        }
      )
      
      if (response.data.success) {
        return true
      } else {
        throw new Error(response.data.message || 'Failed to save')
      }
    } catch (err) {
      console.error('Failed to save discovery:', err)
      
      if (err.response?.status === 403) {
        toast.error('Workshop session lost. Another tab has taken control.', 'Storage')
      } else {
        toast.error(err.response?.data?.detail || 'Failed to save discovery', 'Storage')
      }
      
      return false
    } finally {
      saving.value = false
    }
  }
  
  // TODO: TEMPORARY FALLBACK - Remove once backend temp persistence is implemented
  // This saves from frontend cache when backend loses discovery data
  const saveDiscoveryFromFrontend = async (packageId, packageVersion, discoveryData, customName = null, savePath = null) => {
    try {
      saving.value = true
      const response = await axios.post(
        `http://localhost:8000/api/devices/${deviceSerial}/workshop/save`,
        {
          package_id: packageId,
          package_version: packageVersion,
          custom_name: customName,
          save_path: savePath,
          client_id: clientId.value,
          discovery_data: discoveryData,
          is_fallback_save: true
        }
      )
      
      if (response.data.success) {
        toast.warning('Saved from browser cache (backend data was unavailable)', 'Storage')
        return true
      } else {
        throw new Error(response.data.message || 'Failed to save')
      }
    } catch (err) {
      console.error('Failed to save discovery from frontend:', err)
      
      if (err.response?.status === 403) {
        toast.error('Workshop session lost. Another tab has taken control.', 'Storage')
      } else {
        toast.error(err.response?.data?.detail || 'Failed to save discovery', 'Storage')
      }
      
      return false
    } finally {
      saving.value = false
    }
  }
  
  const deleteDiscovery = async (packageId, folder) => {
    try {
      const response = await axios.delete(
        `http://localhost:8000/api/devices/${deviceSerial}/workshop/discoveries/${packageId}/${folder}`
      )
      
      if (response.data.success) {
        toast.success('Discovery deleted successfully', 'Storage')
        return true
      } else {
        throw new Error(response.data.message || 'Failed to delete')
      }
    } catch (err) {
      console.error('Failed to delete discovery:', err)
      toast.error(err.response?.data?.detail || 'Failed to delete discovery', 'Storage')
      return false
    }
  }
  
  return {
    savedList,
    loading,
    saving,
    selectedDiscovery,
    filterMode,
    listSavedDiscoveries,
    listAllDiscoveries,
    loadDiscovery,
    loadDiscoveryMetadata,
    saveDiscovery,
    saveDiscoveryFromFrontend,
    checkBackendHasResult,
    deleteDiscovery
  }
}

