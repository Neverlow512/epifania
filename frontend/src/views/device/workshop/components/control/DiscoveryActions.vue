<template>
  <div class="space-y-3">
    <button 
      type="button"
      class="btn btn-primary btn-block"
      @click="$emit('start-discovery')"
      :disabled="!canStartDiscovery"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
      Start Discovery
    </button>
    
    <button 
      v-if="discoveryState === 'running'"
      type="button"
      class="btn btn-warning btn-block"
      @click="$emit('cancel-discovery')"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
      </svg>
      Cancel Discovery
    </button>
    
    <div v-if="hasResults" class="flex gap-2">
      <button 
        type="button"
        class="btn btn-success flex-1"
        @click="$emit('save-discovery')"
        :disabled="!hasResults"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
        </svg>
        Save
      </button>
      <button 
        type="button"
        class="btn btn-ghost flex-1"
        @click="$emit('clear-results')"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
        </svg>
        Clear
      </button>
    </div>
    
    <!-- View Logs Button -->
    <button 
      v-if="hasResults || discoveryState === 'running'"
      type="button"
      class="btn btn-ghost btn-sm btn-block"
      @click="$emit('view-logs')"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      View Discovery Logs
      <span v-if="discoveryState === 'running'" class="badge badge-xs badge-success ml-1">Live</span>
    </button>
  </div>
</template>

<script>
export default {
  name: 'DiscoveryActions',
  props: {
    hasLock: {
      type: Boolean,
      required: true
    },
    selectedProcess: {
      type: Object,
      default: null
    },
    discoveryState: {
      type: String,
      default: 'idle'
    },
    hasResults: {
      type: Boolean,
      default: false
    },
    spawnModeEnabled: {
      type: Boolean,
      default: false
    },
    selectedSpawnPackage: {
      type: String,
      default: ''
    }
  },
  emits: ['start-discovery', 'cancel-discovery', 'save-discovery', 'clear-results', 'view-logs'],
  computed: {
    canStartDiscovery() {
      if (!this.hasLock || this.discoveryState === 'running') {
        return false
      }
      
      if (this.spawnModeEnabled) {
        return !!this.selectedSpawnPackage
      } else {
        return !!this.selectedProcess
      }
    }
  }
}
</script>
