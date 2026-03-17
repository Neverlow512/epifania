<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between flex-wrap gap-2">
      <h3 class="text-lg font-semibold text-white">Saved Discoveries</h3>
      <div class="flex items-center gap-2">
        <div class="flex gap-2 bg-neutral-900/50 p-1 rounded">
          <label class="label cursor-pointer gap-1 px-2">
            <input 
              type="radio" 
              name="discovery-filter" 
              class="radio radio-xs radio-primary" 
              value="all"
              :checked="filterMode === 'all'"
              @change="filterMode = 'all'"
            />
            <span class="label-text text-xs text-white">Universal</span>
          </label>
          <label class="label cursor-pointer gap-1 px-2">
            <input 
              type="radio" 
              name="discovery-filter" 
              class="radio radio-xs radio-primary" 
              value="current_device"
              :checked="filterMode === 'current_device'"
              @change="filterMode = 'current_device'"
            />
            <span class="label-text text-xs text-white">Current Device</span>
          </label>
        </div>
        <button 
          type="button"
          class="btn btn-sm btn-primary"
          @click="loadDiscoveries"
          :disabled="loading"
        >
          <svg v-if="!loading" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <span v-if="loading" class="loading loading-spinner loading-xs"></span>
          {{ loading ? 'Loading...' : 'Refresh' }}
        </button>
      </div>
    </div>
    
    <div v-if="loading && flattenedDiscoveries.length === 0" class="flex items-center justify-center py-16">
      <span class="loading loading-spinner loading-lg text-primary"></span>
    </div>
    
    <div v-else-if="flattenedDiscoveries.length === 0">
      <EmptyState
        title="No Saved Discoveries"
        message="You haven't saved any discoveries yet. Complete a discovery and click the Save button to store results for later analysis."
      />
    </div>
    
    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <SavedDiscoveryCard
        v-for="discovery in filteredDiscoveries"
        :key="`${discovery.package_id}_${discovery.folder}`"
        :discovery="discovery"
        :deviceSerial="deviceSerial"
        :savedMetadata="discovery.metadata"
        @load="handleLoad"
        @delete="handleDelete"
      />
    </div>
  </div>
</template>

<script>
import { onMounted, computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import SavedDiscoveryCard from './SavedDiscoveryCard.vue'
import EmptyState from '../../shared/EmptyState.vue'
import { useSavedDiscoveries } from '../../../composables/useSavedDiscoveries'
import { getWorkshopClientId } from '../../../composables/workshopClientId'

export default {
  name: 'SavedDiscoveriesPanel',
  components: {
    SavedDiscoveryCard,
    EmptyState
  },
  emits: ['discovery-loaded'],
  setup(props, { emit }) {
    const route = useRoute()
    const deviceSerial = route.params.id
    const filterMode = ref('all')
    const clientId = ref(getWorkshopClientId())
    
    const {
      savedList,
      loading,
      listAllDiscoveries,
      loadDiscovery,
      deleteDiscovery,
      loadDiscoveryMetadata
    } = useSavedDiscoveries(deviceSerial, clientId)
    
    const discoveryMetadataCache = ref({})
    
    const flattenedDiscoveries = computed(() => {
      const result = []
      for (const pkg of savedList.value) {
        for (const disc of pkg.discoveries || []) {
          const cacheKey = `${pkg.package_id}_${disc.folder}`
          result.push({
            package_id: pkg.package_id,
            folder: disc.folder,
            path: disc.path,
            has_metadata: disc.has_metadata,
            device_serial: discoveryMetadataCache.value[cacheKey]?.device_serial || null,
            metadata: discoveryMetadataCache.value[cacheKey] || null
          })
        }
      }
      return result
    })
    
    const filteredDiscoveries = computed(() => {
      if (filterMode.value === 'current_device') {
        return flattenedDiscoveries.value.filter(disc => {
          return disc.device_serial === deviceSerial || disc.device_serial === null
        })
      }
      return flattenedDiscoveries.value
    })
    
    const loadDiscoveries = async () => {
      await listAllDiscoveries()
      
      for (const pkg of savedList.value) {
        for (const disc of pkg.discoveries || []) {
          const cacheKey = `${pkg.package_id}_${disc.folder}`
          if (!discoveryMetadataCache.value[cacheKey]) {
            const metadata = await loadDiscoveryMetadata(pkg.package_id, disc.folder)
            if (metadata) {
              discoveryMetadataCache.value[cacheKey] = metadata
            }
          }
        }
      }
    }
    
    const handleLoad = async (discovery) => {
      const result = await loadDiscovery(discovery.package_id, discovery.folder)
      if (result) {
        emit('discovery-loaded', result)
      }
    }
    
    const handleDelete = async (discovery) => {
      if (confirm(`Delete discovery ${discovery.folder}?`)) {
        const success = await deleteDiscovery(discovery.package_id, discovery.folder)
        if (success) {
          await loadDiscoveries()
        }
      }
    }
    
    onMounted(() => {
      loadDiscoveries()
    })
    
    return {
      savedList,
      loading,
      filterMode,
      flattenedDiscoveries,
      filteredDiscoveries,
      loadDiscoveries,
      handleLoad,
      handleDelete,
      deviceSerial
    }
  }
}
</script>

