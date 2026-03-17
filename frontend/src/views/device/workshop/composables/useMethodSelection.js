import { ref, computed } from 'vue'

export function useMethodSelection() {
  const selectedMethods = ref(new Map())
  
  const generateMethodId = (className, methodName, signature) => {
    return `${className}::${methodName}::${signature || ''}`
  }
  
  const toggleMethod = (className, method) => {
    const methodId = generateMethodId(className, method.name, method.signature)
    const newMap = new Map(selectedMethods.value)
    
    if (newMap.has(methodId)) {
      newMap.delete(methodId)
    } else {
      newMap.set(methodId, {
        class_name: className,
        method_name: method.name,
        signature: method.signature,
        return_type: method.return_type,
        parameters: method.parameters || [],
        type: 'java'
      })
    }
    
    selectedMethods.value = newMap
  }
  
  const isMethodSelected = (className, methodName, signature) => {
    const methodId = generateMethodId(className, methodName, signature)
    return selectedMethods.value.has(methodId)
  }
  
  const deselectAll = () => {
    selectedMethods.value = new Map()
  }
  
  const selectedCount = computed(() => selectedMethods.value.size)
  
  const hasSelection = computed(() => selectedMethods.value.size > 0)
  
  const getSelectedHooks = () => {
    return Array.from(selectedMethods.value.values())
  }
  
  return {
    selectedMethods,
    selectedCount,
    hasSelection,
    toggleMethod,
    isMethodSelected,
    deselectAll,
    getSelectedHooks
  }
}
