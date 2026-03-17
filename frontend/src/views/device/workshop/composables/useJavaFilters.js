// Java classes and methods filtering with pagination

import { ref, computed, watch, onUnmounted } from 'vue'

export function useJavaFilters(classes, classModifierFilters = ref([]), methodModifierFilters = ref([]), classStates = ref(new Map())) {
  const searchQuery = ref('')
  const debouncedSearch = ref('')
  const categoryFilter = ref('all')
  const sourceFilter = ref('all')
  const expandedClasses = ref(new Set())
  
  const currentPage = ref(1)
  const itemsPerPage = ref(25)
  
  let searchDebounceTimer = null
  
  watch([categoryFilter, sourceFilter, itemsPerPage, classModifierFilters, methodModifierFilters], () => {
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
  
  const filteredClasses = computed(() => {
    let result = classes.value || []
    
    // DND: Capture the Map reference at the start of the computed to establish proper Vue reactivity tracking.
    // When classStates.value = newMap happens (in updateClassStatesFromScan), Vue needs to detect the Map 
    // reference change and re-trigger this computed. Accessing .value inline during .get() calls doesn't 
    // establish the dependency properly due to the computed wrapper from JavaResultsPanel.
    // This ensures modifier filters work correctly when scanning classes in real-time.
    const currentClassStates = classStates.value
    
    if (sourceFilter.value !== 'all') {
      result = result.filter(c => c.source === sourceFilter.value)
    }
    
    if (categoryFilter.value !== 'all') {
      result = result.filter(c => {
        const hasClassCategory = c.class_category === categoryFilter.value
        const hasMethodCategory = c.method_category_summary?.[categoryFilter.value] > 0
        return hasClassCategory || hasMethodCategory
      })
    }
    
    if (classModifierFilters.value && classModifierFilters.value.length > 0) {
      result = result.filter(c => {
        const state = currentClassStates?.get(c.name)
        return classModifierFilters.value.every(modifierId => {
          return (state && state[modifierId] === true) || c[modifierId] === true
        })
      })
    }
    
    if (methodModifierFilters.value && methodModifierFilters.value.length > 0) {
      result = result.filter(c => {
        const state = currentClassStates?.get(c.name)
        const methods = state?.methods || c.methods || []
        return methods.some(method => {
          return methodModifierFilters.value.every(modifierId => method[modifierId] === true)
        })
      })
    }
    
    if (debouncedSearch.value) {
      const query = debouncedSearch.value.toLowerCase()
      result = result.filter(c => {
        const matchesClassName = c.name.toLowerCase().includes(query)
        const matchesMethod = c.methods?.some(m => 
          m.name.toLowerCase().includes(query)
        )
        return matchesClassName || matchesMethod
      })
    }
    
    return result
  })
  
  const paginatedClasses = computed(() => {
    const start = (currentPage.value - 1) * itemsPerPage.value
    const end = start + itemsPerPage.value
    return filteredClasses.value.slice(start, end)
  })
  
  const totalPages = computed(() => 
    Math.ceil(filteredClasses.value.length / itemsPerPage.value)
  )
  
  const toggleClassExpansion = (className) => {
    if (expandedClasses.value.has(className)) {
      expandedClasses.value.delete(className)
    } else {
      expandedClasses.value.add(className)
    }
  }
  
  const isClassExpanded = (className) => {
    return expandedClasses.value.has(className)
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
    expandedClasses,
    currentPage,
    itemsPerPage,
    filteredClasses,
    paginatedClasses,
    totalPages,
    updateSearch,
    toggleClassExpansion,
    isClassExpanded,
    nextPage,
    prevPage
  }
}

