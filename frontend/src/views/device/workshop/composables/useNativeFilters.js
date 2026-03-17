// Native modules and exports filtering with pagination

import { ref, computed, watch, onUnmounted } from 'vue'

export function useNativeFilters(modules) {
  const searchQuery = ref('')
  const debouncedSearch = ref('')
  const categoryFilter = ref('all')
  const sourceFilter = ref('all')
  const expandedModules = ref(new Set())
  
  const currentPage = ref(1)
  const itemsPerPage = ref(25)
  
  let searchDebounceTimer = null
  
  watch([categoryFilter, sourceFilter, itemsPerPage], () => {
    currentPage.value = 1
  })
  
  const updateSearch = (query) => {
    searchQuery.value = query
    if (searchDebounceTimer) {
      clearTimeout(searchDebounceTimer)
    }
    searchDebounceTimer = setTimeout(() => {
      debouncedSearch.value = query
      currentPage.value = 1
    }, 300)
  }
  
  onUnmounted(() => {
    if (searchDebounceTimer) {
      clearTimeout(searchDebounceTimer)
    }
  })
  
  const filteredModules = computed(() => {
    let result = modules.value || []
    
    if (sourceFilter.value !== 'all') {
      result = result.filter(m => m.source === sourceFilter.value)
    }
    
    if (categoryFilter.value !== 'all') {
      result = result.filter(m => {
        const hasModuleCategory = m.module_category === categoryFilter.value
        const hasExportCategory = m.export_category_summary?.[categoryFilter.value] > 0
        return hasModuleCategory || hasExportCategory
      })
    }
    
    if (debouncedSearch.value) {
      const query = debouncedSearch.value.toLowerCase()
      result = result.filter(m => {
        const matchesModuleName = m.name.toLowerCase().includes(query)
        const matchesPath = m.path?.toLowerCase().includes(query)
        const matchesExport = m.exports?.some(e => 
          e.name.toLowerCase().includes(query)
        )
        return matchesModuleName || matchesPath || matchesExport
      })
    }
    
    return result
  })
  
  const paginatedModules = computed(() => {
    const start = (currentPage.value - 1) * itemsPerPage.value
    const end = start + itemsPerPage.value
    return filteredModules.value.slice(start, end)
  })
  
  const totalPages = computed(() => 
    Math.ceil(filteredModules.value.length / itemsPerPage.value)
  )
  
  const toggleModuleExpansion = (moduleName) => {
    if (expandedModules.value.has(moduleName)) {
      expandedModules.value.delete(moduleName)
    } else {
      expandedModules.value.add(moduleName)
    }
  }
  
  const isModuleExpanded = (moduleName) => {
    return expandedModules.value.has(moduleName)
  }
  
  const nextPage = () => {
    if (currentPage.value < totalPages.value) {
      currentPage.value++
    }
  }
  
  const prevPage = () => {
    if (currentPage.value > 1) {
      currentPage.value--
    }
  }
  
  return {
    searchQuery,
    categoryFilter,
    sourceFilter,
    expandedModules,
    currentPage,
    itemsPerPage,
    filteredModules,
    paginatedModules,
    totalPages,
    updateSearch,
    toggleModuleExpansion,
    isModuleExpanded,
    nextPage,
    prevPage
  }
}

