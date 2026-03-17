<template>
  <div class="card bg-neutral-900/60 backdrop-blur-sm shadow-xl border border-primary/20 hover:border-primary/40 transition-colors">
    <div class="card-body p-4">
      <div class="flex items-start justify-between mb-2">
        <div class="flex-1 min-w-0">
          <h4
            class="text-white font-semibold text-sm truncate"
            :title="discovery.package_id"
          >{{ discovery.package_id }}</h4>
          <p
            class="text-slate-400 text-xs truncate"
            :title="formatFolder(discovery.folder)"
          >{{ formatFolder(discovery.folder) }}</p>
        </div>
        <div class="dropdown dropdown-end">
          <label
            tabindex="0"
            class="btn btn-sm btn-ghost btn-square w-8 h-8 min-h-8 bg-neutral-900/40 border border-primary/30 text-slate-200 hover:bg-neutral-800/70 hover:border-primary/60 hover:text-white"
            title="Discovery actions"
            aria-label="Discovery actions"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
            </svg>
          </label>
          <ul tabindex="0" class="dropdown-content menu p-2 shadow bg-neutral-900 border border-primary/30 rounded-box w-32 z-10">
            <li>
              <a @click="$emit('load', discovery)">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                </svg>
                Load
              </a>
            </li>
            <li>
              <a @click="$emit('delete', discovery)" class="text-error">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Delete
              </a>
            </li>
          </ul>
        </div>
      </div>
      
      <div class="flex items-center justify-between gap-2 text-xs mb-3">
        <div class="flex items-center gap-2 text-slate-500">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
          </svg>
          <span v-if="discovery.has_metadata" class="text-green-400">Metadata available</span>
          <span v-else class="text-yellow-400">No metadata</span>
        </div>
        
        <span 
          v-if="matchStatus"
          class="badge badge-sm"
          :class="matchStatusClass"
          :title="matchStatusTooltip"
        >{{ matchStatus.label }}</span>
        <span 
          v-else-if="checkingMatch"
          class="loading loading-spinner loading-xs text-slate-400"
        ></span>
      </div>
      
      <div class="flex gap-2">
        <button 
          type="button"
          class="btn btn-sm btn-primary flex-1"
          @click="$emit('load', discovery)"
        >
          Load Discovery
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useInstallMarkers } from '../../../composables/useInstallMarkers'

export default {
  name: 'SavedDiscoveryCard',
  props: {
    discovery: {
      type: Object,
      required: true
    },
    deviceSerial: {
      type: String,
      required: true
    },
    savedMetadata: {
      type: Object,
      default: null
    }
  },
  emits: ['load', 'delete'],
  setup(props) {
    const matchStatus = ref(null)
    const checkingMatch = ref(false)
    
    const { checkDiscoveryMatch } = useInstallMarkers(props.deviceSerial)
    
    const matchStatusClass = computed(() => {
      if (!matchStatus.value) return ''
      const colorMap = {
        success: 'badge-success',
        warning: 'badge-warning',
        info: 'badge-info',
        neutral: 'badge-ghost'
      }
      return colorMap[matchStatus.value.color] || 'badge-ghost'
    })
    
    const matchStatusTooltip = computed(() => {
      if (!matchStatus.value) return ''
      const tooltips = {
        exact_match: 'This discovery was made on this exact installation',
        same_version: 'Same app version but different installation (reinstalled or different device)',
        updated: 'The app has been updated since this discovery',
        not_installed: 'This app is not currently installed on this device',
        installed_legacy: 'App is installed (legacy discovery without markers)',
        legacy: 'Legacy discovery without installation markers'
      }
      return tooltips[matchStatus.value.status] || ''
    })
    
    const checkMatch = async () => {
      if (!props.savedMetadata) return
      
      checkingMatch.value = true
      try {
        matchStatus.value = await checkDiscoveryMatch({ metadata: props.savedMetadata })
      } catch (err) {
        console.error('Failed to check discovery match:', err)
      } finally {
        checkingMatch.value = false
      }
    }
    
    onMounted(() => {
      if (props.savedMetadata) {
        checkMatch()
      }
    })
    
    return {
      matchStatus,
      checkingMatch,
      matchStatusClass,
      matchStatusTooltip
    }
  },
  methods: {
    formatFolder(folder) {
      if (!folder) return ''
      const parts = folder.split('_')
      if (parts.length >= 2) {
        const date = parts[0]
        const version = parts.slice(1).join('_')
        if (date.length === 8) {
          const year = date.substring(0, 4)
          const month = date.substring(4, 6)
          const day = date.substring(6, 8)
          return `${year}-${month}-${day} (v${version})`
        }
      }
      return folder
    }
  }
}
</script>
