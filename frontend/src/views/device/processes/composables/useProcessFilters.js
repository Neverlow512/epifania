import { ref, computed } from 'vue'

export function useProcessFilters(processes) {
  const searchQuery = ref('')
  const filterType = ref('all')
  const sortBy = ref('memory')
  const showKernelThreads = ref(false)
  const currentPage = ref(0)
  const pageSize = ref(50)

  const filteredProcesses = computed(() => {
    let result = processes.value

    if (!showKernelThreads.value) {
      result = result.filter(p => !p.is_kernel_thread)
    }

    if (filterType.value === 'user') {
      result = result.filter(p => !p.user.startsWith('system') && p.user !== 'root')
    } else if (filterType.value === 'system') {
      result = result.filter(p => p.user.startsWith('system') || p.user === 'root')
    }

    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      result = result.filter(p => 
        p.pid.toString().includes(query) ||
        p.name.toLowerCase().includes(query) ||
        p.user.toLowerCase().includes(query) ||
        p.command.toLowerCase().includes(query)
      )
    }

    result = [...result].sort((a, b) => {
      if (sortBy.value === 'pid') return a.pid - b.pid
      if (sortBy.value === 'name') return a.name.localeCompare(b.name)
      if (sortBy.value === 'memory') return b.memory_mb - a.memory_mb
      if (sortBy.value === 'user') return a.user.localeCompare(b.user)
      return 0
    })

    return result
  })

  const paginatedProcesses = computed(() => {
    const start = currentPage.value * pageSize.value
    const end = start + pageSize.value
    return filteredProcesses.value.slice(start, end)
  })

  const startIndex = computed(() => currentPage.value * pageSize.value)
  const endIndex = computed(() => Math.min((currentPage.value + 1) * pageSize.value, filteredProcesses.value.length))

  return {
    searchQuery,
    filterType,
    sortBy,
    showKernelThreads,
    currentPage,
    pageSize,
    filteredProcesses,
    paginatedProcesses,
    startIndex,
    endIndex
  }
}

