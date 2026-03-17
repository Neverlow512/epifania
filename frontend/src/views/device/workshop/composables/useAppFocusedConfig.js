// App Focused filter configuration management
import { ref, computed } from 'vue'

// TODO: Replace hardcoded URL with centralized config or Vite proxy
const API_BASE = 'http://localhost:8000/api/devices'

export function useAppFocusedConfig() {
  const config = ref(null)
  const templates = ref([])
  const loading = ref(false)
  const saving = ref(false)
  const error = ref(null)
  
  const patterns = computed({
    get: () => config.value?.patterns || [],
    set: (value) => {
      if (config.value) {
        config.value.patterns = value
      }
    }
  })
  
  const patternsText = computed({
    get: () => patterns.value.join('\n'),
    set: (value) => {
      patterns.value = value.split('\n').filter(p => p.trim())
    }
  })
  
  async function loadConfig(packageId) {
    if (!packageId) return
    
    loading.value = true
    error.value = null
    
    try {
      const response = await fetch(`${API_BASE}/workshop/config/app-focused/${encodeURIComponent(packageId)}`)
      if (!response.ok) throw new Error('Failed to load config')
      config.value = await response.json()
    } catch (e) {
      error.value = e.message
      config.value = {
        package_id: packageId,
        patterns: [`${packageId}.*`]
      }
    } finally {
      loading.value = false
    }
  }
  
  async function saveConfig(packageId) {
    if (!packageId || !config.value) return false
    
    saving.value = true
    error.value = null
    
    try {
      const response = await fetch(`${API_BASE}/workshop/config/app-focused/${encodeURIComponent(packageId)}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patterns: patterns.value })
      })
      if (!response.ok) throw new Error('Failed to save config')
      return true
    } catch (e) {
      error.value = e.message
      return false
    } finally {
      saving.value = false
    }
  }
  
  async function resetConfig(packageId) {
    if (!packageId) return
    
    loading.value = true
    error.value = null
    
    try {
      const response = await fetch(`${API_BASE}/workshop/config/app-focused/${encodeURIComponent(packageId)}/reset`, {
        method: 'POST'
      })
      if (!response.ok) throw new Error('Failed to reset config')
      const data = await response.json()
      config.value = data.config
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }
  
  async function loadTemplates(packageId) {
    if (!packageId) return
    
    try {
      const response = await fetch(`${API_BASE}/workshop/config/app-focused/${encodeURIComponent(packageId)}/templates`)
      if (!response.ok) throw new Error('Failed to load templates')
      const data = await response.json()
      templates.value = data.templates || []
    } catch (e) {
      templates.value = []
    }
  }
  
  async function loadTemplate(packageId, templateName) {
    if (!packageId || !templateName) return false
    
    loading.value = true
    error.value = null
    
    try {
      const response = await fetch(`${API_BASE}/workshop/config/app-focused/${encodeURIComponent(packageId)}/templates/${encodeURIComponent(templateName)}`)
      if (!response.ok) throw new Error('Template not found')
      const template = await response.json()
      config.value = {
        ...config.value,
        patterns: template.patterns
      }
      return true
    } catch (e) {
      error.value = e.message
      return false
    } finally {
      loading.value = false
    }
  }
  
  async function saveTemplate(packageId, templateName) {
    if (!packageId || !templateName || !config.value) return false
    
    saving.value = true
    error.value = null
    
    try {
      const response = await fetch(`${API_BASE}/workshop/config/app-focused/${encodeURIComponent(packageId)}/templates`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: templateName,
          patterns: patterns.value
        })
      })
      if (!response.ok) throw new Error('Failed to save template')
      await loadTemplates(packageId)
      return true
    } catch (e) {
      error.value = e.message
      return false
    } finally {
      saving.value = false
    }
  }
  
  async function deleteTemplate(packageId, templateName) {
    if (!packageId || !templateName) return false
    
    try {
      const response = await fetch(`${API_BASE}/workshop/config/app-focused/${encodeURIComponent(packageId)}/templates/${encodeURIComponent(templateName)}`, {
        method: 'DELETE'
      })
      if (!response.ok) throw new Error('Failed to delete template')
      await loadTemplates(packageId)
      return true
    } catch (e) {
      error.value = e.message
      return false
    }
  }
  
  function addStandardObfuscationPatterns() {
    const obfPatterns = ['a.*', 'b.*', 'c.*', 'd.*', 'e.*', 'f.*']
    const current = new Set(patterns.value)
    obfPatterns.forEach(p => current.add(p))
    patterns.value = Array.from(current)
  }
  
  function addSingleLetterPatterns() {
    const singleLetterPatterns = [
      'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
      'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
      'a0.*', 'a1.*', 'b0.*', 'b1.*', 'c0.*', 'c1.*'
    ]
    const current = new Set(patterns.value)
    singleLetterPatterns.forEach(p => current.add(p))
    patterns.value = Array.from(current)
  }
  
  return {
    config,
    patterns,
    patternsText,
    templates,
    loading,
    saving,
    error,
    loadConfig,
    saveConfig,
    resetConfig,
    loadTemplates,
    loadTemplate,
    saveTemplate,
    deleteTemplate,
    addStandardObfuscationPatterns,
    addSingleLetterPatterns
  }
}

