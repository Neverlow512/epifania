// Package details - lazy loading with caching

import { ref } from 'vue'
import axios from 'axios'
import { useToast } from '../../../../composables/useToast'

export function usePackageDetails(deviceSerial) {
  const toast = useToast()

  const detailsCache = ref(new Map())
  const loading = ref(false)
  const currentPackage = ref(null)
  const error = ref(null)

  const fetchDetails = async (packageId) => {
    if (detailsCache.value.has(packageId)) {
      currentPackage.value = detailsCache.value.get(packageId)
      return currentPackage.value
    }

    try {
      loading.value = true
      error.value = null

      const response = await axios.get(
        `http://localhost:8000/api/devices/${deviceSerial}/packages/${packageId}`
      )

      const details = response.data
      detailsCache.value.set(packageId, details)
      currentPackage.value = details

      return details
    } catch (err) {
      console.error('Failed to fetch package details:', err)
      error.value = err.response?.data?.detail || 'Failed to fetch package details'
      toast.error(error.value)
      return null
    } finally {
      loading.value = false
    }
  }

  const clearDetails = (packageId) => {
    if (packageId) {
      detailsCache.value.delete(packageId)
      if (currentPackage.value?.package_id === packageId) {
        currentPackage.value = null
      }
    }
  }

  const clearAllDetails = () => {
    detailsCache.value.clear()
    currentPackage.value = null
  }

  const getCached = (packageId) => {
    return detailsCache.value.get(packageId) || null
  }

  const closeDetails = () => {
    currentPackage.value = null
    error.value = null
  }

  return {
    detailsCache,
    loading,
    currentPackage,
    error,
    fetchDetails,
    clearDetails,
    clearAllDetails,
    getCached,
    closeDetails
  }
}

