// Package filtering, searching, and sorting - client-side logic

import { ref, computed, watch } from 'vue'

export function usePackageFilters(packages) {
  const searchQuery = ref('')
  const sortBy = ref('name')
  const showRunningOnly = ref(false)
  const currentPage = ref(0)
  const pageSize = ref(25)

  let searchDebounceTimer = null

  const filteredPackages = computed(() => {
    let result = [...packages.value]

    if (showRunningOnly.value) {
      result = result.filter(pkg => pkg.is_running)
    }

    if (searchQuery.value.trim()) {
      const query = searchQuery.value.toLowerCase().trim()
      result = result.filter(pkg =>
        pkg.package_id.toLowerCase().includes(query) ||
        (pkg.name && pkg.name.toLowerCase().includes(query))
      )
    }

    result.sort((a, b) => {
      switch (sortBy.value) {
        case 'name':
          return (a.name || a.package_id).localeCompare(b.name || b.package_id)
        case 'package_id':
          return a.package_id.localeCompare(b.package_id)
        case 'status':
          if (a.is_running === b.is_running) {
            return (a.name || a.package_id).localeCompare(b.name || b.package_id)
          }
          return a.is_running ? -1 : 1
        default:
          return 0
      }
    })

    return result
  })

  const paginatedPackages = computed(() => {
    const start = currentPage.value * pageSize.value
    return filteredPackages.value.slice(start, start + pageSize.value)
  })

  const startIndex = computed(() => currentPage.value * pageSize.value)
  
  const endIndex = computed(() => 
    Math.min(startIndex.value + pageSize.value, filteredPackages.value.length)
  )

  const totalPages = computed(() => 
    Math.ceil(filteredPackages.value.length / pageSize.value)
  )

  watch([searchQuery, sortBy, showRunningOnly], () => {
    currentPage.value = 0
  })

  const setSearch = (query) => {
    if (searchDebounceTimer) {
      clearTimeout(searchDebounceTimer)
    }
    searchDebounceTimer = setTimeout(() => {
      searchQuery.value = query
    }, 300)
  }

  const setSearchImmediate = (query) => {
    if (searchDebounceTimer) {
      clearTimeout(searchDebounceTimer)
    }
    searchQuery.value = query
  }

  const setSort = (field) => {
    sortBy.value = field
  }

  const toggleRunningOnly = () => {
    showRunningOnly.value = !showRunningOnly.value
  }

  const clearFilters = () => {
    searchQuery.value = ''
    showRunningOnly.value = false
    sortBy.value = 'name'
    currentPage.value = 0
  }

  const hasActiveFilters = computed(() => 
    searchQuery.value.trim() !== '' || showRunningOnly.value
  )

  return {
    searchQuery,
    sortBy,
    showRunningOnly,
    currentPage,
    pageSize,
    filteredPackages,
    paginatedPackages,
    startIndex,
    endIndex,
    totalPages,
    hasActiveFilters,
    setSearch,
    setSearchImmediate,
    setSort,
    toggleRunningOnly,
    clearFilters
  }
}

