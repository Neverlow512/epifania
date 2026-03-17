<template>
  <div v-if="show" class="modal modal-open">
    <div class="modal-box bg-neutral-900 border border-warning/30 max-w-lg">
      <h3 class="font-bold text-lg text-white mb-4 flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-warning" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        Backend Data Unavailable
      </h3>
      
      <p class="text-slate-300 mb-4">
        The backend lost the discovery data, possibly due to a restart or crash. 
        You can save the cached data from your browser instead.
      </p>
      
      <div class="bg-black/30 p-3 rounded-lg border border-warning/20 mb-4">
        <div class="text-sm text-slate-400">
          <div class="flex justify-between mb-1">
            <span>Package:</span>
            <span class="text-white font-mono text-xs">{{ packageId || 'Unknown' }}</span>
          </div>
          <div class="flex justify-between mb-1">
            <span>Classes:</span>
            <span class="text-white">{{ stats.totalClasses }}</span>
          </div>
          <div class="flex justify-between mb-1">
            <span>Methods:</span>
            <span class="text-white">{{ stats.totalMethods }}</span>
          </div>
          <div class="flex justify-between mb-1">
            <span>Native Modules:</span>
            <span class="text-white">{{ stats.totalModules }}</span>
          </div>
        </div>
      </div>
      
      <div class="alert alert-warning mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-5 w-5" fill="none" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span class="text-sm">This data is from your browser cache. If the discovery didn't fully complete, some data may be missing.</span>
      </div>
      
      <div class="modal-action">
        <button 
          type="button"
          class="btn btn-ghost" 
          @click="$emit('cancel')"
          :disabled="saving"
        >
          Cancel
        </button>
        <button 
          type="button"
          class="btn btn-warning" 
          @click="$emit('confirm')"
          :disabled="saving"
        >
          <span v-if="saving" class="loading loading-spinner loading-xs"></span>
          {{ saving ? 'Saving...' : 'Save from Cache' }}
        </button>
      </div>
    </div>
    <div class="modal-backdrop bg-black/50" @click="$emit('cancel')"></div>
  </div>
</template>

<script>
// TODO: TEMPORARY FALLBACK - Remove this component once backend temp persistence is implemented
export default {
  name: 'FallbackSaveModal',
  props: {
    show: {
      type: Boolean,
      required: true
    },
    packageId: {
      type: String,
      default: null
    },
    stats: {
      type: Object,
      default: () => ({
        totalClasses: 0,
        totalMethods: 0,
        totalModules: 0
      })
    },
    saving: {
      type: Boolean,
      default: false
    }
  },
  emits: ['cancel', 'confirm']
}
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: -1;
}
</style>

