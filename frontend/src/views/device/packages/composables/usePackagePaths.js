// Path management for install/extract operations with localStorage persistence

import { ref, computed } from 'vue'

const STORAGE_KEY = 'epifania_packages_settings'
const MAX_RECENT_PATHS = 10
const DEFAULT_DEVICE_TEMP_PATH = '/data/local/tmp/epifania_install.apk'
const DEFAULT_EXTRACT_BASE = 'tmp/extracted_apks'

function loadSettings() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      return JSON.parse(stored)
    }
  } catch (err) {
    console.error('Failed to load package settings:', err)
  }
  return getDefaultSettings()
}

function getDefaultSettings() {
  return {
    paths: {
      deviceTempPath: DEFAULT_DEVICE_TEMP_PATH,
      extractBaseDir: DEFAULT_EXTRACT_BASE
    },
    behavior: {
      autoRefreshAfterAction: true,
      confirmUninstall: true,
      confirmClearData: true
    },
    recentPaths: {
      install: [],
      extract: []
    }
  }
}

export function usePackagePaths() {
  const settings = ref(loadSettings())

  const deviceTempPath = computed({
    get: () => settings.value.paths.deviceTempPath,
    set: (val) => {
      settings.value.paths.deviceTempPath = val
      saveSettings()
    }
  })

  const extractBaseDir = computed({
    get: () => settings.value.paths.extractBaseDir,
    set: (val) => {
      settings.value.paths.extractBaseDir = val
      saveSettings()
    }
  })

  const recentInstallPaths = computed(() => settings.value.recentPaths.install)
  const recentExtractPaths = computed(() => settings.value.recentPaths.extract)

  const confirmUninstall = computed({
    get: () => settings.value.behavior.confirmUninstall,
    set: (val) => {
      settings.value.behavior.confirmUninstall = val
      saveSettings()
    }
  })

  const confirmClearData = computed({
    get: () => settings.value.behavior.confirmClearData,
    set: (val) => {
      settings.value.behavior.confirmClearData = val
      saveSettings()
    }
  })

  const saveSettings = () => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(settings.value))
    } catch (err) {
      console.error('Failed to save package settings:', err)
    }
  }

  const getExtractPath = (packageId) => {
    const base = settings.value.paths.extractBaseDir
    return `${base}/${packageId}.apk`
  }

  const addRecentInstallPath = (path) => {
    const paths = settings.value.recentPaths.install
    const index = paths.indexOf(path)
    if (index > -1) {
      paths.splice(index, 1)
    }
    paths.unshift(path)
    if (paths.length > MAX_RECENT_PATHS) {
      paths.pop()
    }
    saveSettings()
  }

  const addRecentExtractPath = (path) => {
    const paths = settings.value.recentPaths.extract
    const index = paths.indexOf(path)
    if (index > -1) {
      paths.splice(index, 1)
    }
    paths.unshift(path)
    if (paths.length > MAX_RECENT_PATHS) {
      paths.pop()
    }
    saveSettings()
  }

  const clearRecentPaths = () => {
    settings.value.recentPaths.install = []
    settings.value.recentPaths.extract = []
    saveSettings()
  }

  const resetToDefaults = () => {
    settings.value = getDefaultSettings()
    saveSettings()
  }

  const validatePath = (path) => {
    if (!path || typeof path !== 'string') {
      return { valid: false, error: 'Path is required' }
    }
    if (path.includes('..')) {
      return { valid: false, error: 'Path cannot contain ..' }
    }
    return { valid: true, error: null }
  }

  return {
    settings,
    deviceTempPath,
    extractBaseDir,
    recentInstallPaths,
    recentExtractPaths,
    confirmUninstall,
    confirmClearData,
    getExtractPath,
    addRecentInstallPath,
    addRecentExtractPath,
    clearRecentPaths,
    resetToDefaults,
    validatePath,
    saveSettings
  }
}

