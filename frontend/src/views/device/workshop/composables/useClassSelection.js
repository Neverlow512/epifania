// Manages multi-select state for classes in the Workshop tab

import { ref, computed } from 'vue'

export function useClassSelection() {
  const selectedClasses = ref(new Set())
  
  const toggleClass = (className) => {
    const newSet = new Set(selectedClasses.value)
    if (newSet.has(className)) {
      newSet.delete(className)
    } else {
      newSet.add(className)
    }
    selectedClasses.value = newSet
  }
  
  const selectClasses = (classNames) => {
    const newSet = new Set(selectedClasses.value)
    classNames.forEach(name => newSet.add(name))
    selectedClasses.value = newSet
  }
  
  const deselectClasses = (classNames) => {
    const newSet = new Set(selectedClasses.value)
    classNames.forEach(name => newSet.delete(name))
    selectedClasses.value = newSet
  }
  
  const deselectAll = () => {
    selectedClasses.value = new Set()
  }
  
  const selectPage = (classNames) => {
    selectClasses(classNames)
  }
  
  const selectAllVisible = (classNames) => {
    selectClasses(classNames)
  }
  
  const isSelected = (className) => {
    return selectedClasses.value.has(className)
  }
  
  const selectedCount = computed(() => selectedClasses.value.size)
  
  const getSelectedArray = () => Array.from(selectedClasses.value)
  
  const hasSelection = computed(() => selectedClasses.value.size > 0)
  
  return {
    selectedClasses,
    selectedCount,
    hasSelection,
    toggleClass,
    selectClasses,
    deselectClasses,
    deselectAll,
    selectPage,
    selectAllVisible,
    isSelected,
    getSelectedArray
  }
}
