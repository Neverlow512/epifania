// Parses and holds discovery data with computed statistics
// Supports lazy discovery: class states stored in Map for efficient updates

import { ref, computed } from 'vue'

export function useDiscoveryResults() {
  const discoveryData = ref(null)
  const classStates = ref(new Map())
  
  const metadata = computed(() => {
    return discoveryData.value?.metadata || null
  })
  
  const javaClasses = computed(() => {
    const classes = discoveryData.value?.java_classes
    if (Array.isArray(classes)) return classes
    if (classes?.classes && Array.isArray(classes.classes)) return classes.classes
    return []
  })
  
  const javaClassesWithState = computed(() => {
    return javaClasses.value.map(cls => {
      const state = classStates.value.get(cls.name)
      if (state) {
        return { ...cls, ...state }
      }
      return cls
    })
  })
  
  const classesFromApk = computed(() => {
    return javaClassesWithState.value.filter(cls => cls.scanned && cls.is_from_apk)
  })
  
  const scannedClassCount = computed(() => {
    let count = 0
    classStates.value.forEach(state => {
      if (state.scanned) count++
    })
    return count
  })
  
  const extractedClassCount = computed(() => {
    let count = 0
    classStates.value.forEach(state => {
      if (state.extracted) count++
    })
    return count
  })
  
  const attemptedClassCount = computed(() => {
    let count = 0
    classStates.value.forEach(state => {
      if (state.attempted) count++
    })
    return count
  })
  
  const nativeModules = computed(() => {
    const modules = discoveryData.value?.native_modules
    if (Array.isArray(modules)) return modules
    if (modules?.modules && Array.isArray(modules.modules)) return modules.modules
    return []
  })
  
  const stats = computed(() => {
    if (!discoveryData.value || !metadata.value) {
      return {
        totalClasses: 0,
        totalMethods: 0,
        totalModules: 0,
        totalExports: 0,
        javaCategories: {},
        nativeCategories: {},
        sourceBreakdown: {},
        scannedClasses: scannedClassCount.value,
        extractedClasses: extractedClassCount.value,
        apkClasses: classesFromApk.value.length,
        classModifiers: classModifierStats.value,
        methodModifiers: methodModifierStats.value
      }
    }
    
    return {
      totalClasses: metadata.value.stats?.java?.classes_included || javaClasses.value.length,
      totalMethods: metadata.value.stats?.java?.total_methods || 0,
      totalModules: metadata.value.stats?.native?.modules_included || 0,
      totalExports: metadata.value.stats?.native?.total_exports || 0,
      javaCategories: metadata.value.stats?.java?.classes_by_category || {},
      nativeCategories: metadata.value.stats?.native?.modules_by_category || {},
      sourceBreakdown: metadata.value.stats?.filtering?.source_breakdown || {},
      scannedClasses: scannedClassCount.value,
      extractedClasses: extractedClassCount.value,
      apkClasses: classesFromApk.value.length,
      classModifiers: classModifierStats.value,
      methodModifiers: methodModifierStats.value
    }
  })
  
  const verification = computed(() => {
    return discoveryData.value?.metadata?.verification || null
  })
  
  const classModifierStats = computed(() => {
    const stats = {
      is_public: 0,
      is_private: 0,
      is_protected: 0,
      is_static: 0,
      is_final: 0,
      is_interface: 0,
      is_abstract: 0
    }
    
    javaClassesWithState.value.forEach(cls => {
      if (cls.is_public) stats.is_public++
      if (cls.is_private) stats.is_private++
      if (cls.is_protected) stats.is_protected++
      if (cls.is_static) stats.is_static++
      if (cls.is_final) stats.is_final++
      if (cls.is_interface) stats.is_interface++
      if (cls.is_abstract) stats.is_abstract++
    })
    
    return stats
  })
  
  const methodModifierStats = computed(() => {
    const stats = {
      is_public: 0,
      is_private: 0,
      is_protected: 0,
      is_static: 0,
      is_final: 0,
      is_native: 0,
      is_synchronized: 0,
      is_abstract: 0
    }
    
    javaClassesWithState.value.forEach(cls => {
      const methods = cls.methods || []
      methods.forEach(method => {
        if (method.is_public) stats.is_public++
        if (method.is_private) stats.is_private++
        if (method.is_protected) stats.is_protected++
        if (method.is_static) stats.is_static++
        if (method.is_final) stats.is_final++
        if (method.is_native) stats.is_native++
        if (method.is_synchronized) stats.is_synchronized++
        if (method.is_abstract) stats.is_abstract++
      })
    })
    
    return stats
  })
  
  const updateClassState = (className, updates) => {
    const current = classStates.value.get(className) || {
      name: className,
      scanned: false,
      is_from_apk: false,
      loader_type: null,
      extracted: false,
      attempted: false,
      methods: null
    }
    const newState = { ...current, ...updates }
    const newMap = new Map(classStates.value)
    newMap.set(className, newState)
    classStates.value = newMap
  }
  
  const getClassBadge = (className) => {
    const state = classStates.value.get(className)
    
    if (state?.extracted && state.method_count > 0) {
      return {
        type: 'extracted',
        label: `${state.method_count} methods`,
        color: 'green'
      }
    }
    
    if (state?.attempted) {
      return {
        type: 'attempted',
        label: 'Attempted (crashed)',
        color: 'orange'
      }
    }
    
    return null
  }
  
  const updateClassStatesFromScan = (scanResults) => {
    const newMap = new Map(classStates.value)
    
    scanResults.forEach(result => {
      if (result.success) {
        const current = newMap.get(result.name) || {
          name: result.name,
          scanned: false,
          is_from_apk: false,
          loader_type: null,
          extracted: false,
          methods: null
        }
        newMap.set(result.name, {
          ...current,
          scanned: true,
          is_from_apk: result.is_from_apk,
          loader_type: result.loader_type,
          is_public: current.is_public || result.is_public,
          is_private: current.is_private || result.is_private,
          is_protected: current.is_protected || result.is_protected,
          is_static: current.is_static || result.is_static,
          is_final: current.is_final || result.is_final,
          is_interface: current.is_interface || result.is_interface,
          is_abstract: current.is_abstract || result.is_abstract
        })
      }
    })
    
    classStates.value = newMap
  }
  
  const updateClassStatesFromExtract = (extractResults) => {
    const newMap = new Map(classStates.value)
    
    extractResults.forEach(result => {
      const current = newMap.get(result.name) || {
        name: result.name,
        scanned: false,
        is_from_apk: false,
        loader_type: null,
        extracted: false,
        methods: null
      }
      newMap.set(result.name, {
        ...current,
        extracted: true,
        methods: result.methods || [],
        method_count: result.method_count || 0
      })
    })
    
    classStates.value = newMap
  }
  
  const getClassState = (className) => {
    return classStates.value.get(className) || null
  }
  
  const isClassScanned = (className) => {
    const state = classStates.value.get(className)
    return state?.scanned || false
  }
  
  const isClassExtracted = (className) => {
    const state = classStates.value.get(className)
    return state?.extracted || false
  }
  
  const loadDiscoveryData = (data) => {
    discoveryData.value = data
    classStates.value = new Map()
    
    const classes = data?.java_classes?.classes || data?.java_classes || []
    if (Array.isArray(classes)) {
      const newMap = new Map()
      classes.forEach(cls => {
        newMap.set(cls.name, {
          name: cls.name,
          scanned: cls.scanned || false,
          is_from_apk: cls.is_from_apk || false,
          loader_type: cls.loader_type || cls.source || null,
          extracted: (cls.methods && cls.methods.length > 0) || cls.extracted || false,
          methods: cls.methods || null,
          method_count: cls.method_count || (cls.methods?.length || 0),
          is_public: cls.is_public,
          is_private: cls.is_private,
          is_protected: cls.is_protected,
          is_static: cls.is_static,
          is_final: cls.is_final,
          is_interface: cls.is_interface,
          is_abstract: cls.is_abstract
        })
      })
      classStates.value = newMap
    }
  }
  
  const clearDiscoveryData = () => {
    discoveryData.value = null
    classStates.value = new Map()
  }
  
  return {
    discoveryData,
    metadata,
    javaClasses,
    javaClassesWithState,
    classesFromApk,
    nativeModules,
    stats,
    verification,
    classStates,
    scannedClassCount,
    extractedClassCount,
    attemptedClassCount,
    classModifierStats,
    methodModifierStats,
    loadDiscoveryData,
    clearDiscoveryData,
    updateClassState,
    updateClassStatesFromScan,
    updateClassStatesFromExtract,
    getClassState,
    getClassBadge,
    isClassScanned,
    isClassExtracted
  }
}
