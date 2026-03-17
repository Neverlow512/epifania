import { ref } from 'vue'

const toasts = ref([])
let nextId = 0

export function useToast() {
  const findGroup = (type, key, message) => {
    return toasts.value.find(
      t => t.type === type && t.key === key && t.message === message
    )
  }

  const removeToast = (id) => {
    const index = toasts.value.findIndex(t => t.id === id)
    if (index !== -1) {
      const toast = toasts.value[index]
      if (toast.timeoutId) {
        clearTimeout(toast.timeoutId)
      }
      toasts.value.splice(index, 1)
    }
  }

  const addToast = (message, type = 'info', key = '', duration = 5000) => {
    if (type === 'error' || type === 'guidance') {
      const existing = findGroup(type, key, message)
      if (existing) {
        if (type === 'error') {
          existing.count = 1
          existing.lastUpdated = Date.now()
        }
        return existing.id
      }

      const id = nextId++
      const toast = {
        id,
        message,
        type,
        key,
        duration,
        count: type === 'error' ? 1 : undefined,
        expanded: false,
        pinned: false,
        timeoutId: null
      }

      toasts.value.push(toast)
      return id
    }

    const id = nextId++
    const toast = {
      id,
      message,
      type,
      key,
      duration,
      pinned: false,
      timeoutId: null
    }

    toasts.value.push(toast)

    toast.timeoutId = setTimeout(() => {
      removeToast(id)
    }, duration)

    return id
  }

  const pinToast = (id) => {
    const toast = toasts.value.find(t => t.id === id)
    if (toast && toast.type !== 'error' && toast.type !== 'guidance') {
      toast.pinned = true
      if (toast.timeoutId) {
        clearTimeout(toast.timeoutId)
        toast.timeoutId = null
      }
    }
  }

  const unpinToast = (id) => {
    const toast = toasts.value.find(t => t.id === id)
    if (toast && toast.type !== 'error' && toast.type !== 'guidance') {
      toast.pinned = false
      toast.timeoutId = setTimeout(() => {
        removeToast(id)
      }, toast.duration)
    }
  }

  const clearError = (key) => {
    if (!key) return
    toasts.value = toasts.value.filter(
      t => !(t.type === 'error' && t.key === key)
    )
  }

  const success = (message, key = '') => {
    clearError(key)
    return addToast(message, 'success', key)
  }

  const error = (message, key = '') => {
    return addToast(message, 'error', key, 7000)
  }

  const warning = (message, key = '') => {
    return addToast(message, 'warning', key, 6000)
  }

  const info = (message, key = '') => {
    return addToast(message, 'info', key)
  }

  const guidance = (message, key = '') => {
    return addToast(message, 'guidance', key)
  }

  return {
    toasts,
    addToast,
    removeToast,
    pinToast,
    unpinToast,
    clearError,
    success,
    error,
    warning,
    info,
    guidance
  }
}

