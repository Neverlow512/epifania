<template>
  <div v-if="show" class="modal modal-open">
    <div class="modal-box bg-neutral-900 border border-warning/30 max-w-md">
      <h3 class="font-bold text-lg text-white mb-4 flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-warning" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        Unsaved Discovery
      </h3>
      
      <p class="text-slate-300 mb-4">
        You have discovery results that haven't been saved. Clearing will permanently delete this data.
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
          <div class="flex justify-between">
            <span>Methods:</span>
            <span class="text-white">{{ stats.totalMethods }}</span>
          </div>
        </div>
      </div>
      
      <label class="label cursor-pointer justify-start gap-2 mb-4">
        <input 
          type="checkbox" 
          class="checkbox checkbox-sm checkbox-warning" 
          v-model="dontShowAgain"
        />
        <span class="label-text text-slate-400 text-sm">Don't show this warning again</span>
      </label>
      
      <div class="modal-action">
        <button 
          type="button"
          class="btn btn-ghost" 
          @click="$emit('cancel')"
        >
          Cancel
        </button>
        <button 
          type="button"
          class="btn btn-warning" 
          @click="handleConfirm"
        >
          Clear Anyway
        </button>
      </div>
    </div>
    <div class="modal-backdrop bg-black/50" @click="$emit('cancel')"></div>
  </div>
</template>

<script>
import { ref } from 'vue'

const STORAGE_KEY = 'workshop-skip-clear-warning'

export default {
  name: 'ClearDiscoveryModal',
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
        totalMethods: 0
      })
    }
  },
  emits: ['cancel', 'confirm'],
  setup(props, { emit }) {
    const dontShowAgain = ref(false)
    
    const handleConfirm = () => {
      if (dontShowAgain.value) {
        localStorage.setItem(STORAGE_KEY, 'true')
      }
      emit('confirm')
    }
    
    return {
      dontShowAgain,
      handleConfirm
    }
  }
}

export function shouldShowClearWarning() {
  return localStorage.getItem(STORAGE_KEY) !== 'true'
}

export function resetClearWarning() {
  localStorage.removeItem(STORAGE_KEY)
}
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: -1;
}
</style>

