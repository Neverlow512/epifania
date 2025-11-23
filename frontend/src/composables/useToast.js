import { ref } from 'vue'

const toasts = ref([])
let nextId = 0

export function useToast() {
  const addToast = (message, type = 'info', title = '', duration = 5000) => {
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
      if (!toast.pinned) {
        removeToast(id)
      }
    }, duration)
    
    return id
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

  const pinToast = (id) => {
    const toast = toasts.value.find(t => t.id === id)
    if (toast) {
      toast.pinned = true
      if (toast.timeoutId) {
        clearTimeout(toast.timeoutId)
        toast.timeoutId = null
      }
    }
  }

  const unpinToast = (id) => {
    const toast = toasts.value.find(t => t.id === id)
    if (toast) {
      toast.pinned = false
      toast.timeoutId = setTimeout(() => {
        removeToast(id)
      }, toast.duration)
    }
  }

  const success = (message, title = '') => {
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

