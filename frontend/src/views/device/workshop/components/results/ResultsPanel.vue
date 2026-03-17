<template>
  <div class="card bg-neutral-900/60 backdrop-blur-sm shadow-xl border border-primary/20">
    <div class="card-body p-0">
      <!-- Tabs with Help/Instructions buttons -->
      <div class="relative">
        <div class="tabs tabs-boxed bg-neutral-900/80 p-2 rounded-t-lg border-b border-primary/20">
          <a 
            class="tab"
            :class="{ 'tab-active': activeTab === 'java' }"
            @click="$emit('update:activeTab', 'java')"
          >
            Java Classes
          </a>
          <a 
            class="tab"
            :class="{ 'tab-active': activeTab === 'native' }"
            @click="$emit('update:activeTab', 'native')"
          >
            Native Modules
          </a>
          <a 
            class="tab"
            :class="{ 'tab-active': activeTab === 'saved' }"
            @click="$emit('update:activeTab', 'saved')"
          >
            Saved Discoveries
          </a>
        </div>
        
        <!-- Help and Instructions buttons -->
        <div class="absolute top-2 right-2 flex gap-2">
          <button
            v-if="workshopMode === 'analysis'"
            type="button"
            class="btn btn-xs btn-ghost btn-instructions text-slate-400 hover:text-white"
            @click="showInstructionsModal = true"
            title="Analysis Instructions"
          >
            <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
            Instructions
          </button>
          <button
            v-else
            type="button"
            class="btn btn-xs btn-ghost btn-instructions text-slate-400 hover:text-white"
            @click="showInstrumentationInstructionsModal = true"
            title="Instrumentation Instructions"
          >
            <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
            Instructions
          </button>
          <button
            v-if="workshopMode === 'analysis'"
            type="button"
            class="btn btn-xs btn-accent"
            @click="showHelpModal = true"
            title="Results Help"
          >
            <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Help
          </button>
          <button
            v-else
            type="button"
            class="btn btn-xs btn-accent"
            @click="showInstrumentationHelpModal = true"
            title="Instrumentation Help"
          >
            <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Help
          </button>
        </div>
      </div>
      
      <!-- Discovery Metadata Header -->
      <DiscoveryMetadataHeader
        v-if="discoveryData && (activeTab === 'java' || activeTab === 'native')"
        :metadata="discoveryData.metadata"
        :stats="computedStats"
        :activeTab="activeTab"
        :deviceSerial="deviceSerial"
        @update:classModifierFilters="handleClassModifierFiltersUpdate"
        @update:methodModifierFilters="handleMethodModifierFiltersUpdate"
      />
      
      <!-- Tab Content -->
      <div class="p-4">
        <div v-if="loading" class="flex items-center justify-center py-16">
          <span class="loading loading-spinner loading-lg text-primary"></span>
        </div>
        
        <JavaResultsPanel
          v-else-if="activeTab === 'java'"
          :classes="extractedJavaClasses"
          :selectedClasses="selectedClasses"
          :classStates="classStates"
          :filterMode="filterMode"
          :workshopMode="workshopMode"
          :showSelection="showSelection"
          :selectedScanTypes="selectedScanTypes"
          :classModifierFilters="classModifierFilters"
          :methodModifierFilters="methodModifierFilters"
          :selectedMethods="selectedMethods"
          :methodSelectionEnabled="methodSelectionEnabled"
          @toggle-select="$emit('toggle-select', $event)"
          @select-page="$emit('select-page', $event)"
          @select-all="$emit('select-all', $event)"
          @deselect-all="$emit('deselect-all')"
          @scan-classloader="$emit('scan-classloader')"
          @open-scan-modal="$emit('open-scan-modal')"
          @remove-scan-type="$emit('remove-scan-type', $event)"
          @clear-scan-types="$emit('clear-scan-types')"
          @scan-modifiers="$emit('scan-modifiers')"
          @extract-methods="$emit('extract-methods')"
          @scan-class="$emit('scan-class', $event)"
          @extract-class="$emit('extract-class', $event)"
          @toggle-select-method="$emit('toggle-select-method', $event)"
        />
        
        <NativeResultsPanel
          v-else-if="activeTab === 'native'"
          :modules="extractedNativeModules"
        />
        
        <SavedDiscoveriesPanel
          v-else-if="activeTab === 'saved'"
          @discovery-loaded="$emit('discovery-loaded', $event)"
        />
      </div>
    </div>

    <ResultsPanelHelpModal
      :show="showHelpModal"
      @close="showHelpModal = false"
    />

    <ResultsInstructionsModal
      :show="showInstructionsModal"
      @close="showInstructionsModal = false"
    />

    <InstrumentationHelpModal
      :show="showInstrumentationHelpModal"
      @close="showInstrumentationHelpModal = false"
    />

    <InstrumentationInstructionsModal
      :show="showInstrumentationInstructionsModal"
      @close="showInstrumentationInstructionsModal = false"
    />
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import JavaResultsPanel from './java/JavaResultsPanel.vue'
import NativeResultsPanel from './native/NativeResultsPanel.vue'
import SavedDiscoveriesPanel from './saved/SavedDiscoveriesPanel.vue'
import DiscoveryMetadataHeader from './DiscoveryMetadataHeader.vue'
import ResultsPanelHelpModal from '../modals/ResultsPanelHelpModal.vue'
import ResultsInstructionsModal from '../modals/ResultsInstructionsModal.vue'
import InstrumentationHelpModal from '../instrumentation/modals/InstrumentationHelpModal.vue'
import InstrumentationInstructionsModal from '../instrumentation/modals/InstrumentationInstructionsModal.vue'

export default {
  name: 'ResultsPanel',
  components: {
    JavaResultsPanel,
    NativeResultsPanel,
    SavedDiscoveriesPanel,
    DiscoveryMetadataHeader,
    ResultsPanelHelpModal,
    ResultsInstructionsModal,
    InstrumentationHelpModal,
    InstrumentationInstructionsModal
  },
  props: {
    activeTab: {
      type: String,
      required: true
    },
    discoveryData: {
      type: Object,
      default: null
    },
    loading: {
      type: Boolean,
      default: false
    },
    deviceSerial: {
      type: String,
      required: true
    },
    selectedClasses: {
      type: Set,
      default: () => new Set()
    },
    classStates: {
      type: Map,
      default: () => new Map()
    },
    filterMode: {
      type: String,
      default: 'focused'
    },
    workshopMode: {
      type: String,
      default: 'analysis'
    },
    showSelection: {
      type: Boolean,
      default: true
    },
    appFocusedPatterns: {
      type: Array,
      default: () => []
    },
    packageId: {
      type: String,
      default: ''
    },
    selectedScanTypes: {
      type: Array,
      default: () => []
    },
    stats: {
      type: Object,
      default: () => ({
        totalClasses: 0,
        totalMethods: 0,
        totalModules: 0,
        totalExports: 0,
        classModifiers: {},
        methodModifiers: {}
      })
    },
    selectedMethods: {
      type: Map,
      default: () => new Map()
    },
    methodSelectionEnabled: {
      type: Boolean,
      default: false
    }
  },
  emits: [
    'update:activeTab',
    'discovery-loaded',
    'toggle-select',
    'select-page',
    'select-all',
    'deselect-all',
    'scan-classloader',
    'open-scan-modal',
    'remove-scan-type',
    'clear-scan-types',
    'scan-modifiers',
    'extract-methods',
    'scan-class',
    'extract-class',
    'toggle-select-method'
  ],
  setup(props) {
    const showHelpModal = ref(false)
    const showInstructionsModal = ref(false)
    const showInstrumentationHelpModal = ref(false)
    const showInstrumentationInstructionsModal = ref(false)
    
    const computedStats = computed(() => {
      if (!props.discoveryData || !props.discoveryData.metadata) {
        return {
          totalClasses: 0,
          totalMethods: 0,
          totalModules: 0,
          totalExports: 0,
          classModifiers: props.stats?.classModifiers || {},
          methodModifiers: props.stats?.methodModifiers || {}
        }
      }
      
      const visibleClasses = extractedJavaClasses.value
      const totalClasses = visibleClasses.length
      
      let totalMethods = 0
      visibleClasses.forEach(cls => {
        const state = props.classStates.get(cls.name)
        if (state?.extracted && state.methods) {
          totalMethods += state.methods.length
        } else if (cls.methods && Array.isArray(cls.methods)) {
          totalMethods += cls.methods.length
        } else if (cls.method_count && cls.method_count > 0) {
          totalMethods += cls.method_count
        }
      })
      
      const meta = props.discoveryData.metadata
      return {
        totalClasses: totalClasses,
        totalMethods: totalMethods,
        totalModules: meta.stats?.native?.modules_included || 0,
        totalExports: meta.stats?.native?.total_exports || 0,
        classModifiers: props.stats?.classModifiers || {},
        methodModifiers: props.stats?.methodModifiers || {}
      }
    })
    
    const rawJavaClasses = computed(() => {
      const classes = props.discoveryData?.java_classes
      if (!classes) return []
      if (Array.isArray(classes)) return classes
      if (classes.classes && Array.isArray(classes.classes)) return classes.classes
      return []
    })
    
    // Compile patterns for focused mode filtering
    const compiledPatterns = computed(() => {
      const patterns = props.appFocusedPatterns
      if (!patterns || patterns.length === 0) {
        // Default: match package ID prefix
        if (props.packageId) {
          return [new RegExp(`^${props.packageId.replace(/\./g, '\\.')}(\\..*)?$`)]
        }
        return []
      }
      
      return patterns.map(pattern => {
        if (!pattern) return null
        try {
          // Convert glob-like patterns to regex
          if (pattern.endsWith('.*')) {
            // pattern.* matches pattern. followed by anything
            return new RegExp(`^${pattern.slice(0, -2).replace(/\./g, '\\.')}\\.`)
          } else if (pattern.endsWith('*')) {
            // pattern* matches anything starting with pattern
            return new RegExp(`^${pattern.slice(0, -1).replace(/\./g, '\\.')}`)
          } else {
            // Exact match or single-letter class match
            return new RegExp(`^${pattern.replace(/\./g, '\\.')}($|\\.)`)
          }
        } catch (e) {
          return null
        }
      }).filter(Boolean)
    })
    
    const matchesFocusedPatterns = (className) => {
      const patterns = compiledPatterns.value
      if (patterns.length === 0) {
        // Default: match package ID prefix
        return props.packageId && className.startsWith(props.packageId)
      }
      return patterns.some(regex => regex.test(className))
    }
    
    // Apply filter mode to classes for real-time filtering
    const extractedJavaClasses = computed(() => {
      const classes = rawJavaClasses.value
      
      // Package mode: show only scanned classes that are from APK
      if (props.filterMode === 'package') {
        return classes.filter(cls => {
          const state = props.classStates.get(cls.name)
          // Must be scanned and from APK
          return (state?.scanned || cls.scanned) && (state?.is_from_apk || cls.is_from_apk)
        })
      }
      
      // Focused mode: filter by app focused patterns
      if (props.filterMode === 'focused') {
        return classes.filter(cls => matchesFocusedPatterns(cls.name))
      }
      
      // All mode: show all classes
      return classes
    })
    
    const extractedNativeModules = computed(() => {
      const modules = props.discoveryData?.native_modules
      if (!modules) return []
      if (Array.isArray(modules)) return modules
      if (modules.modules && Array.isArray(modules.modules)) return modules.modules
      return []
    })
    
    const classModifierFilters = ref([])
    const methodModifierFilters = ref([])
    
    const handleClassModifierFiltersUpdate = (filters) => {
      classModifierFilters.value = filters
    }
    
    const handleMethodModifierFiltersUpdate = (filters) => {
      methodModifierFilters.value = filters
    }
    
    return {
      showHelpModal,
      showInstructionsModal,
      showInstrumentationHelpModal,
      showInstrumentationInstructionsModal,
      computedStats,
      extractedJavaClasses,
      extractedNativeModules,
      classModifierFilters,
      methodModifierFilters,
      handleClassModifierFiltersUpdate,
      handleMethodModifierFiltersUpdate
    }
  }
}
</script>
