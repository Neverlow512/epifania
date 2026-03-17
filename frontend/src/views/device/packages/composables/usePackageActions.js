// Package actions - install, uninstall, launch, stop, clear cache/data, pull

import { ref } from 'vue'
import axios from 'axios'
import { useToast } from '../../../../composables/useToast'

export function usePackageActions(deviceSerial, refreshPackages, clearDetails, isPrimary) {
  const toast = useToast()

  const actionInProgress = ref(false)
  const actionType = ref(null)
  const lastError = ref(null)

  const executeAction = async (action, endpoint, method, body = null, successMsg) => {
    if (!isPrimary.value) {
      toast.warning('Only the primary tab can perform actions. Switch to this tab to control actions.')
      return { success: false, error: 'Not primary tab' }
    }

    try {
      actionInProgress.value = true
      actionType.value = action
      lastError.value = null

      const config = { method, url: endpoint }
      if (body) {
        config.data = body
      }

      const response = await axios(config)
      toast.success(response.data.message || successMsg)

      if (refreshPackages) {
        await refreshPackages()
      }

      return { success: true, data: response.data }
    } catch (err) {
      console.error(`Failed to ${action}:`, err)
      lastError.value = err.response?.data?.detail || `Failed to ${action}`
      toast.error(lastError.value)
      return { success: false, error: lastError.value }
    } finally {
      actionInProgress.value = false
      actionType.value = null
    }
  }

  const launchPackage = async (packageId) => {
    return executeAction(
      'launch',
      `http://localhost:8000/api/devices/${deviceSerial}/packages/${packageId}/launch`,
      'POST',
      null,
      `Package ${packageId} launched`
    )
  }

  const stopPackage = async (packageId) => {
    const result = await executeAction(
      'stop',
      `http://localhost:8000/api/devices/${deviceSerial}/packages/${packageId}/stop`,
      'POST',
      null,
      `Package ${packageId} stopped`
    )
    if (result.success && clearDetails) {
      clearDetails(packageId)
    }
    return result
  }

  const installPackage = async (apkSource, isLocalFile = true, deviceTempPath = null) => {
    const body = {
      apk_source: apkSource,
      is_local_file: isLocalFile
    }
    if (deviceTempPath) {
      body.device_temp_path = deviceTempPath
    }

    return executeAction(
      'install',
      `http://localhost:8000/api/devices/${deviceSerial}/packages/install`,
      'POST',
      body,
      'Package installed successfully'
    )
  }

  const uninstallPackage = async (packageId, keepData = false) => {
    const result = await executeAction(
      'uninstall',
      `http://localhost:8000/api/devices/${deviceSerial}/packages/${packageId}?keep_data=${keepData}`,
      'DELETE',
      null,
      `Package ${packageId} uninstalled`
    )
    if (result.success && clearDetails) {
      clearDetails(packageId)
    }
    return result
  }

  const pullPackage = async (packageId, destinationPath) => {
    return executeAction(
      'pull',
      `http://localhost:8000/api/devices/${deviceSerial}/packages/${packageId}/pull`,
      'POST',
      { destination_path: destinationPath },
      `APK extracted to ${destinationPath}`
    )
  }

  const clearCache = async (packageId) => {
    const result = await executeAction(
      'clear-cache',
      `http://localhost:8000/api/devices/${deviceSerial}/packages/${packageId}/clear-cache`,
      'POST',
      null,
      `Cache cleared for ${packageId}`
    )
    if (result.success && clearDetails) {
      clearDetails(packageId)
    }
    return result
  }

  const clearData = async (packageId) => {
    const result = await executeAction(
      'clear-data',
      `http://localhost:8000/api/devices/${deviceSerial}/packages/${packageId}/clear-data`,
      'POST',
      null,
      `Data cleared for ${packageId}`
    )
    if (result.success && clearDetails) {
      clearDetails(packageId)
    }
    return result
  }

  return {
    actionInProgress,
    actionType,
    lastError,
    launchPackage,
    stopPackage,
    installPackage,
    uninstallPackage,
    pullPackage,
    clearCache,
    clearData
  }
}

