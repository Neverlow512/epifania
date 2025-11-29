import { ref } from 'vue'

const toasts = ref([])
let nextId = 0

export function useToast() {
  const findGroup = (type, title, message) => {
    return toasts.value.find(
      t => t.type === type && t.title === title && t.message === message
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

  const addToast = (message, type = 'info', title = '', duration = 5000) => {
    if (type === 'error') {
      const existing = findGroup(type, title, message)
      if (existing) {
        existing.count = 1
        existing.lastUpdated = Date.now()
        return existing.id
      }

      const id = nextId++
      const toast = {
        id,
        message,
        type,
        title,
        duration,
        count: 1,
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
      title,
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
    if (toast && toast.type !== 'error') {
      toast.pinned = true
      if (toast.timeoutId) {
        clearTimeout(toast.timeoutId)
        toast.timeoutId = null
      }
    }
  }

  const unpinToast = (id) => {
    const toast = toasts.value.find(t => t.id === id)
    if (toast && toast.type !== 'error') {
      toast.pinned = false
      toast.timeoutId = setTimeout(() => {
        removeToast(id)
      }, toast.duration)
    }
  }

  const clearErrorsByTitle = (title) => {
    if (!title) return
    toasts.value = toasts.value.filter(
      t => !(t.type === 'error' && t.title === title)
    )
  }

  const success = (message, title = '') => {
    clearErrorsByTitle(title)
    return addToast(message, 'success', title)
  }

  const error = (message, title = '') => {
    return addToast(message, 'error', title, 7000)
  }

  const warning = (message, title = '') => {
    return addToast(message, 'warning', title, 6000)
  }

  const info = (message, title = '') => {
    return addToast(message, 'info', title)
  }

  return {
    toasts,
    addToast,
    removeToast,
    pinToast,
    unpinToast,
    success,
    error,
    warning,
    info
  }
}

