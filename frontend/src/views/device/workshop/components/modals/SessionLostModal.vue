<template>
  <Teleport to="body">
    <div v-if="show" class="modal modal-open">
      <div class="modal-box bg-neutral-900 border border-orange-500/30 max-w-lg">
        <h3 class="font-bold text-lg text-orange-400 flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          Frida Session Lost
        </h3>
        
        <div class="mt-4 space-y-4">
          <p class="text-slate-300">
            The Frida agent crashed during the operation. This can happen when processing certain classes.
          </p>
          
          <div class="bg-neutral-800 rounded-lg p-4">
            <div class="text-sm text-slate-400 mb-2">Operation Progress</div>
            <div class="w-full bg-neutral-700 rounded-full h-2.5 mb-2">
              <div 
                class="bg-orange-500 h-2.5 rounded-full transition-all"
                :style="{ width: progressPercent + '%' }"
              ></div>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-slate-400">Processed {{ processed }} of {{ total }} classes</span>
              <span class="text-orange-400">{{ progressPercent }}%</span>
            </div>
          </div>
          
          <div class="grid grid-cols-2 gap-3 text-sm">
            <div class="bg-neutral-800 rounded p-3">
              <div class="text-green-400 font-medium">{{ successCount }}</div>
              <div class="text-slate-500">Succeeded</div>
            </div>
            <div class="bg-neutral-800 rounded p-3">
              <div class="text-orange-400 font-medium">{{ attemptedCount }}</div>
              <div class="text-slate-500">Attempted (crashed)</div>
            </div>
            <div class="bg-neutral-800 rounded p-3">
              <div class="text-red-400 font-medium">{{ errorCount }}</div>
              <div class="text-slate-500">Errors</div>
            </div>
            <div class="bg-neutral-800 rounded p-3">
              <div class="text-slate-300 font-medium">{{ remainingCount }}</div>
              <div class="text-slate-500">Not processed</div>
            </div>
          </div>
          
          <div class="text-sm text-slate-400 bg-neutral-800/50 rounded p-3">
            <p class="font-medium text-slate-300 mb-1">What to do next:</p>
            <ul class="list-disc list-inside space-y-1">
              <li>Reattach to the process using the Attach button</li>
              <li>Select the remaining classes and retry the operation</li>
              <li>Classes marked with an orange badge caused the crash</li>
            </ul>
          </div>
        </div>
        
        <div class="modal-action">
          <button 
            class="btn btn-ghost btn-sm"
            @click="$emit('view-logs')"
          >
            View Logs
          </button>
          <button 
            class="btn btn-primary btn-sm"
            @click="$emit('close')"
          >
            Continue
          </button>
        </div>
      </div>
      <div class="modal-backdrop bg-black/70" @click.stop></div>
    </div>
  </Teleport>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'SessionLostModal',
  props: {
    show: {
      type: Boolean,
      required: true
    },
    data: {
      type: Object,
      default: null
    }
  },
  emits: ['close', 'view-logs'],
  setup(props) {
    const processed = computed(() => props.data?.processed || 0)
    const total = computed(() => props.data?.total || 0)
    const errors = computed(() => props.data?.errors || [])
    
    const progressPercent = computed(() => {
      if (total.value === 0) return 0
      return Math.round((processed.value / total.value) * 100)
    })
    
    const successCount = computed(() => {
      const results = props.data?.results || []
      return results.filter(r => r.success && !r.attempted).length
    })
    
    const attemptedCount = computed(() => {
      const results = props.data?.results || []
      return results.filter(r => r.attempted).length
    })
    
    const errorCount = computed(() => errors.value.length)
    
    const remainingCount = computed(() => {
      return Math.max(0, total.value - processed.value)
    })
    
    return {
      processed,
      total,
      progressPercent,
      successCount,
      attemptedCount,
      errorCount,
      remainingCount
    }
  }
}
</script>
