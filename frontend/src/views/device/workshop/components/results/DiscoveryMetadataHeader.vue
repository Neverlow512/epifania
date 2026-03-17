<template>
  <div v-if="metadata" class="space-y-2">
    <div 
      v-if="metadata.package_id"
      class="alert py-2 px-3 text-xs min-w-0 break-words"
      :class="alertClass"
    >
      <span v-if="checking" class="loading loading-spinner loading-xs"></span>
      <svg 
        v-else
        xmlns="http://www.w3.org/2000/svg" 
        class="h-4 w-4 flex-shrink-0" 
        fill="none" 
        viewBox="0 0 24 24" 
        stroke="currentColor"
      >
        <path 
          v-if="matchStatus && matchStatus.color === 'success'" 
          stroke-linecap="round" 
          stroke-linejoin="round" 
          stroke-width="2" 
          d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" 
        />
        <path 
          v-else-if="matchStatus && matchStatus.color === 'warning'"
          stroke-linecap="round" 
          stroke-linejoin="round" 
          stroke-width="2" 
          d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" 
        />
        <path 
          v-else
          stroke-linecap="round" 
          stroke-linejoin="round" 
          stroke-width="2" 
          d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" 
        />
      </svg>
      <span>{{ alertMessage }}</span>
    </div>
    
    <div class="bg-neutral-900/40 border-b border-primary/20 px-4 py-3">
      <div class="flex items-center justify-between flex-wrap gap-2">
        <div class="flex items-center gap-3 min-w-0">
          <div class="min-w-0">
            <h4
              class="text-white font-semibold text-sm truncate"
              :title="metadata.package_id || 'Unknown Package'"
            >{{ metadata.package_id || 'Unknown Package' }}</h4>
            <p class="text-slate-400 text-xs">
              Version {{ metadata.package_version || 'unknown' }}
              <span v-if="metadata.timestamp" class="ml-2">
                • {{ formatTimestamp(metadata.timestamp) }}
              </span>
            </p>
          </div>
        </div>
        
        <div v-if="activeTab === 'java'" class="flex flex-col items-end gap-2">
          <div class="flex items-center gap-4 text-xs">
            <div class="flex items-center gap-1">
              <span class="text-slate-400">Classes:</span>
              <span class="text-white font-semibold">{{ formatNumber(stats.totalClasses) }}</span>
            </div>
            <div class="flex items-center gap-1">
              <span class="text-slate-400">Methods:</span>
              <span class="text-white font-semibold">{{ formatNumber(stats.totalMethods) }}</span>
            </div>
          </div>
          
          <div class="collapse collapse-arrow bg-neutral-900/50 border border-primary/20 rounded-lg" style="width: 320px;">
            <input type="checkbox" />
            <div class="collapse-title text-xs font-medium text-white px-3 py-2 min-h-0 flex items-center gap-1.5">
              <span>Access Modifiers</span>
              <QuestionTooltip text="Click on modifiers to filter classes or methods. Multiple selections use AND logic (shows items matching ALL selected modifiers). Cannot filter classes and methods simultaneously." />
            </div>
            <div class="collapse-content px-3 pb-3 pt-0">
              <div class="grid grid-cols-2 gap-4 text-xs">
                <div>
                  <div class="font-semibold text-white mb-2 text-xs border-b border-primary/20 pb-1">Class Modifiers</div>
                  <div class="space-y-1">
                    <div 
                      v-for="modifier in CLASS_MODIFIERS" 
                      :key="modifier.id" 
                      class="flex items-center justify-between group"
                    >
                      <span 
                        class="text-slate-300 cursor-pointer hover:text-white transition-colors"
                        :style="getModifierStyle(modifier, isClassModifierSelected(modifier.id))"
                        @click="toggleClassModifier(modifier.id)"
                      >
                        {{ modifier.label }}
                      </span>
                      <span class="text-white font-semibold">{{ stats.classModifiers?.[modifier.id] || 0 }}</span>
                    </div>
                  </div>
                </div>
                <div>
                  <div class="font-semibold text-white mb-2 text-xs border-b border-primary/20 pb-1">Method Modifiers</div>
                  <div class="space-y-1">
                    <div 
                      v-for="modifier in METHOD_MODIFIERS" 
                      :key="modifier.id" 
                      class="flex items-center justify-between group"
                    >
                      <span 
                        class="text-slate-300 cursor-pointer hover:text-white transition-colors"
                        :style="getModifierStyle(modifier, isMethodModifierSelected(modifier.id))"
                        @click="toggleMethodModifier(modifier.id)"
                      >
                        {{ modifier.label }}
                      </span>
                      <span class="text-white font-semibold">{{ stats.methodModifiers?.[modifier.id] || 0 }}</span>
                    </div>
                  </div>
                </div>
              </div>
              <div v-if="filterError" class="mt-3 text-xs text-red-400 bg-red-900/20 border border-red-500/30 rounded px-2 py-1.5">
                {{ filterError }}
              </div>
            </div>
          </div>
        </div>
        
        <div v-else-if="activeTab === 'native'" class="flex items-center gap-4 text-xs">
          <div class="flex items-center gap-1">
            <span class="text-slate-400">Modules:</span>
            <span class="text-white font-semibold">{{ formatNumber(stats.totalModules) }}</span>
          </div>
          <div class="flex items-center gap-1">
            <span class="text-slate-400">Exports:</span>
            <span class="text-white font-semibold">{{ formatNumber(stats.totalExports) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue'
import { useInstallMarkers } from '../../composables/useInstallMarkers'
import QuestionTooltip from '../shared/QuestionTooltip.vue'

const CLASS_MODIFIERS = [
  { id: 'is_public', label: 'Public', color: '#10b981' },
  { id: 'is_private', label: 'Private', color: '#ef4444' },
  { id: 'is_protected', label: 'Protected', color: '#eab308' },
  { id: 'is_static', label: 'Static', color: '#a855f7' },
  { id: 'is_final', label: 'Final', color: '#f97316' },
  { id: 'is_interface', label: 'Interface', color: '#06b6d4' },
  { id: 'is_abstract', label: 'Abstract', color: '#ec4899' }
]

const METHOD_MODIFIERS = [
  { id: 'is_public', label: 'Public', color: '#10b981' },
  { id: 'is_private', label: 'Private', color: '#ef4444' },
  { id: 'is_protected', label: 'Protected', color: '#eab308' },
  { id: 'is_static', label: 'Static', color: '#a855f7' },
  { id: 'is_final', label: 'Final', color: '#f97316' },
  { id: 'is_native', label: 'Native', color: '#3b82f6' },
  { id: 'is_synchronized', label: 'Synchronized', color: '#06b6d4' },
  { id: 'is_abstract', label: 'Abstract', color: '#ec4899' }
]

export default {
  name: 'DiscoveryMetadataHeader',
  components: {
    QuestionTooltip
  },
  props: {
    metadata: {
      type: Object,
      default: null
    },
    stats: {
      type: Object,
      default: () => ({
        totalClasses: 0,
        totalMethods: 0,
        totalModules: 0,
        totalExports: 0
      })
    },
    activeTab: {
      type: String,
      required: true
    },
    deviceSerial: {
      type: String,
      required: true
    }
  },
  emits: ['update:classModifierFilters', 'update:methodModifierFilters'],
  setup(props, { emit }) {
    const matchStatus = ref(null)
    const checking = ref(false)
    const selectedClassModifiers = ref([])
    const selectedMethodModifiers = ref([])
    const filterError = ref('')
    
    const { checkDiscoveryMatch } = useInstallMarkers(props.deviceSerial)
    
    const alertClass = computed(() => {
      if (!matchStatus.value) return 'alert-info'
      const colorMap = {
        success: 'alert-success',
        warning: 'alert-warning',
        info: 'alert-info',
        neutral: 'alert-info'
      }
      return colorMap[matchStatus.value.color] || 'alert-info'
    })
    
    const alertMessage = computed(() => {
      if (!props.metadata?.package_id) return ''
      if (!matchStatus.value) return `Checking ${props.metadata.package_id}...`
      
      const pkg = props.metadata.package_id
      
      switch (matchStatus.value.status) {
        case 'exact_match':
          return `Installed: This is the exact app installation used in this discovery`
        case 'same_version':
          return `Installed: Same version (${props.metadata.package_version || 'unknown'}) but app was reinstalled since discovery`
        case 'updated':
          return `Installed: App was updated since this discovery was made`
        case 'installed_legacy':
          return `Installed: ${pkg} is on this device (discovery has no install markers to compare)`
        case 'not_installed':
          return `Not installed: ${pkg} is not present on this device`
        case 'legacy':
          return `Unknown: Cannot verify installation (legacy discovery without markers)`
        default:
          return `${pkg}`
      }
    })
    
    const isClassModifierSelected = (modifierId) => {
      return selectedClassModifiers.value.includes(modifierId)
    }
    
    const isMethodModifierSelected = (modifierId) => {
      return selectedMethodModifiers.value.includes(modifierId)
    }
    
    const getModifierStyle = (modifier, isSelected) => {
      if (!isSelected) return {}
      return {
        backgroundColor: modifier.color,
        color: '#ffffff',
        fontWeight: '600',
        padding: '2px 6px',
        borderRadius: '4px'
      }
    }
    
    const toggleClassModifier = (modifierId) => {
      if (selectedMethodModifiers.value.length > 0) {
        filterError.value = 'Cannot filter classes and methods simultaneously. Clear method filters first.'
        return
      }
      
      filterError.value = ''
      // DND: Do not mutate this array in-place (push/splice). We replace it to ensure
      // Vue's non-deep watch() triggers reliably and the filters propagate to ResultsPanel.
      const current = selectedClassModifiers.value
      const next = current.includes(modifierId)
        ? current.filter(id => id !== modifierId)
        : [...current, modifierId]
      selectedClassModifiers.value = next
    }
    
    const toggleMethodModifier = (modifierId) => {
      if (selectedClassModifiers.value.length > 0) {
        filterError.value = 'Cannot filter classes and methods simultaneously. Clear class filters first.'
        return
      }
      
      filterError.value = ''
      // DND: Do not mutate this array in-place (push/splice). We replace it to ensure
      // Vue's non-deep watch() triggers reliably and the filters propagate to ResultsPanel.
      const current = selectedMethodModifiers.value
      const next = current.includes(modifierId)
        ? current.filter(id => id !== modifierId)
        : [...current, modifierId]
      selectedMethodModifiers.value = next
    }
    
    watch(selectedClassModifiers, (newFilters) => {
      emit('update:classModifierFilters', newFilters)
    })
    
    watch(selectedMethodModifiers, (newFilters) => {
      emit('update:methodModifierFilters', newFilters)
    })
    
    const checkMatch = async () => {
      if (!props.metadata?.package_id) return
      
      checking.value = true
      try {
        matchStatus.value = await checkDiscoveryMatch({ metadata: props.metadata })
      } catch (err) {
        console.error('Failed to check discovery match:', err)
        matchStatus.value = { status: 'legacy', label: 'Unknown', color: 'neutral' }
      } finally {
        checking.value = false
      }
    }
    
    watch(() => props.metadata, () => {
      if (props.metadata) {
        checkMatch()
      }
    }, { immediate: true })
    
    return {
      matchStatus,
      checking,
      alertClass,
      alertMessage,
      selectedClassModifiers,
      selectedMethodModifiers,
      filterError,
      isClassModifierSelected,
      isMethodModifierSelected,
      getModifierStyle,
      toggleClassModifier,
      toggleMethodModifier,
      CLASS_MODIFIERS,
      METHOD_MODIFIERS
    }
  },
  methods: {
    formatNumber(num) {
      return num?.toLocaleString() || '0'
    },
    formatTimestamp(timestamp) {
      try {
        const date = new Date(timestamp)
        return date.toLocaleString('en-US', {
          month: 'short',
          day: 'numeric',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        })
      } catch (e) {
        return timestamp
      }
    }
  }
}
</script>

