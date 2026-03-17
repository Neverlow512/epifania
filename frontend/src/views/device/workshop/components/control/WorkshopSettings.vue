<template>
  <div class="card bg-neutral-900/60 backdrop-blur-sm shadow-xl border border-primary/20">
    <div class="card-body p-4">
      <div 
        class="flex items-center justify-between cursor-pointer hover:bg-neutral-800/30 -m-4 p-4 rounded-lg transition-colors"
        @click="expanded = !expanded"
      >
        <h4 class="text-white text-sm font-medium">Settings</h4>
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          class="h-4 w-4 text-slate-400 transition-transform duration-200"
          :class="{ 'rotate-180': expanded }"
          fill="none" 
          viewBox="0 0 24 24" 
          stroke="currentColor"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </div>
      
      <div 
        class="transition-all duration-300"
        :class="expanded ? 'overflow-visible' : 'overflow-hidden'"
        :style="{ maxHeight: expanded ? '500px' : '0px' }"
      >
        <div class="pt-4 space-y-3">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="text-slate-300 text-sm">Temp State Retention</span>
              <div class="tooltip tooltip-right z-[9999]" data-tip="Automatically keeps the N most recent saved temp states per package. Older saved temps are deleted on backend startup. Unsaved temp states (active work) are never auto-deleted.">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-blue-400 hover:text-primary cursor-help drop-shadow-[0_0_2px_rgba(96,165,250,0.5)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>
          
          <div class="flex items-center gap-2">
            <button
              class="btn btn-xs bg-violet-600 hover:bg-violet-500 border-none text-white"
              :disabled="!selectedProcess || localValue <= minLimit"
              @click="decrementLocal"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4" />
              </svg>
            </button>
            
            <input
              type="number"
              class="input input-xs input-bordered bg-neutral-800 text-white w-16 text-center"
              v-model.number="localValue"
              :min="minLimit"
              :disabled="!selectedProcess"
            />
            
            <button
              class="btn btn-xs bg-violet-600 hover:bg-violet-500 border-none text-white"
              :disabled="!selectedProcess"
              @click="incrementLocal"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
            </button>
            
            <button
              v-if="selectedProcess && expanded"
              class="btn btn-xs ml-2"
              :class="hasChanges ? 'btn-success' : 'btn-disabled'"
              :disabled="!hasChanges || saving"
              @click="saveChanges"
            >
              <svg v-if="!saving" xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <span v-if="saving" class="loading loading-spinner loading-xs"></span>
              <span class="ml-1">{{ saving ? 'Saving...' : 'Save' }}</span>
            </button>
          </div>
          
          <div class="text-xs leading-relaxed">
            <div v-if="selectedProcess">
              <!-- Current status -->
              <div class="text-slate-300 mb-2">
                <span class="font-medium">Current setting:</span> 
                Keep {{ retentionLimit }} most recent {{ retentionLimit === 1 ? 'temp state' : 'temp states' }} per package
              </div>
              
              <!-- Pending changes -->
              <div v-if="hasChanges" class="text-amber-400 mb-2">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 inline mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <span class="font-medium">Unsaved changes:</span> Will keep {{ localValue }} {{ localValue === 1 ? 'temp state' : 'temp states' }} (click Save to apply)
              </div>
              
              <!-- Protection notice -->
              <div v-if="unsavedTempCount > 0" class="text-orange-400 mb-2">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 inline mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
                <span class="font-medium">Protected:</span> {{ unsavedTempCount }} unsaved temp {{ unsavedTempCount === 1 ? 'state' : 'states' }} across devices (minimum retention enforced)
              </div>
              
              <!-- Save button status -->
              <div v-if="!hasChanges" class="text-slate-500">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 inline mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Save button disabled: No changes to save
              </div>
              
              <!-- Cleanup timing info -->
              <div class="text-slate-500 mt-2 pt-2 border-t border-slate-700">
                <span class="text-xs">Cleanup runs automatically at backend startup. Old saved temp states are deleted based on modification time.</span>
              </div>
            </div>
            
            <div v-else class="text-slate-500">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 inline mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Select a process to configure retention settings
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { useTempStateRetention } from '../../composables/useTempStateRetention'

export default {
  name: 'WorkshopSettings',
  props: {
    device: {
      type: Object,
      required: true
    },
    selectedProcess: {
      type: Object,
      default: null
    }
  },
  setup(props) {
    const expanded = ref(false)
    const localValue = ref(10)
    
    const packageId = computed(() => props.selectedProcess?.package_id || null)
    
    const {
      retentionLimit,
      unsavedTempCount,
      effectiveLimit,
      minLimit,
      loading,
      saving,
      saveRetentionConfig
    } = useTempStateRetention(props.device.serial, packageId)
    
    // Sync local value with loaded retention limit
    watch(retentionLimit, (newValue) => {
      localValue.value = newValue
    }, { immediate: true })
    
    const hasChanges = computed(() => {
      return localValue.value !== retentionLimit.value
    })
    
    function incrementLocal() {
      localValue.value = localValue.value + 1
    }
    
    function decrementLocal() {
      const newValue = Math.max(minLimit.value, localValue.value - 1)
      if (newValue !== localValue.value) {
        localValue.value = newValue
      }
    }
    
    async function saveChanges() {
      const success = await saveRetentionConfig(localValue.value)
      if (!success) {
        // Reset to server value on error
        localValue.value = retentionLimit.value
      }
    }
    
    return {
      expanded,
      localValue,
      retentionLimit,
      unsavedTempCount,
      effectiveLimit,
      minLimit,
      loading,
      saving,
      hasChanges,
      incrementLocal,
      decrementLocal,
      saveChanges
    }
  }
}
</script>

<style scoped>
input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  appearance: none;
  margin: 0;
}

input[type="number"] {
  -moz-appearance: textfield;
  appearance: textfield;
}

/* Force tooltips to appear on top of everything */
.tooltip:before,
.tooltip:after {
  z-index: 99999 !important;
}
</style>
