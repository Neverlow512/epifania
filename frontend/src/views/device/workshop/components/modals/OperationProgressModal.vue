<template>
  <Teleport to="body">
    <div v-if="show" class="modal modal-open">
      <div class="modal-box bg-neutral-900 border max-w-md"
           :class="sessionLost ? 'border-orange-500/30' : 'border-primary/30'">
        <h3 class="font-bold text-lg text-white mb-4">{{ title }}</h3>
        
        <div class="space-y-4">
          <div class="w-full bg-neutral-800 rounded-full h-3 overflow-hidden">
            <div 
              class="h-full transition-all duration-200 rounded-full"
              :class="barClass"
              :style="{ width: progressPercent + '%' }"
            ></div>
          </div>
          
          <div class="flex justify-between text-sm">
            <span class="text-slate-400">
              <template v-if="sessionLost">
                Session lost - partial results
              </template>
              <template v-else-if="cancelled">
                Cancelling...
              </template>
              <template v-else>
                Processing {{ current }} of {{ total }}
              </template>
            </span>
            <span :class="sessionLost ? 'text-orange-400' : 'text-primary'" class="font-medium">
              {{ progressPercent }}%
            </span>
          </div>
          
          <div v-if="sessionLost" class="grid grid-cols-2 gap-3 text-sm">
            <div class="bg-neutral-800 rounded p-3">
              <div class="text-green-400 font-medium">{{ successCount }}</div>
              <div class="text-slate-500">Succeeded</div>
            </div>
            <div class="bg-neutral-800 rounded p-3">
              <div class="text-orange-400 font-medium">{{ attemptedCount }}</div>
              <div class="text-slate-500">Attempted</div>
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
          
          <div v-if="currentItem && !cancelled && !sessionLost" class="text-xs text-slate-500 font-mono truncate">
            {{ currentItem }}
          </div>
          
          <div class="text-xs text-slate-500">
            Elapsed: {{ elapsedTime }}
          </div>
        </div>
        
        <div class="modal-action">
          <template v-if="sessionLost">
            <button 
              class="btn btn-sm btn-ghost"
              @click="$emit('view-logs')"
            >
              View Logs
            </button>
            <button 
              class="btn btn-sm btn-primary"
              @click="$emit('continue')"
            >
              Continue
            </button>
          </template>
          <template v-else>
            <button 
              class="btn btn-sm bg-orange-600 hover:bg-orange-500 border-none text-white"
              :disabled="cancelled"
              @click="handleCancel"
            >
              {{ cancelled ? 'Cancelling...' : 'Cancel' }}
            </button>
          </template>
        </div>
      </div>
      <div class="modal-backdrop bg-black/70" @click.stop></div>
    </div>
  </Teleport>
</template>

<script>
import { computed, ref, watch, onUnmounted } from 'vue'

export default {
  name: 'OperationProgressModal',
  props: {
    show: {
      type: Boolean,
      required: true
    },
    title: {
      type: String,
      default: 'Processing...'
    },
    current: {
      type: Number,
      default: 0
    },
    total: {
      type: Number,
      default: 0
    },
    currentItem: {
      type: String,
      default: ''
    },
    cancelled: {
      type: Boolean,
      default: false
    },
    sessionLost: {
      type: Boolean,
      default: false
    },
    results: {
      type: Array,
      default: () => []
    },
    errors: {
      type: Array,
      default: () => []
    }
  },
  emits: ['cancel', 'view-logs', 'continue'],
  setup(props, { emit }) {
    const startTime = ref(Date.now())
    const elapsedSeconds = ref(0)
    let timer = null
    
    const progressPercent = computed(() => {
      if (props.total === 0) return 0
      return Math.round((props.current / props.total) * 100)
    })
    
    const barClass = computed(() => {
      if (props.sessionLost) return 'bg-orange-500'
      if (props.cancelled) return 'bg-orange-500'
      return 'bg-primary'
    })
    
    const successCount = computed(() => {
      return props.results.filter(r => r.success && !r.attempted).length
    })
    
    const attemptedCount = computed(() => {
      return props.results.filter(r => r.attempted).length
    })
    
    const errorCount = computed(() => {
      return props.errors.length
    })
    
    const remainingCount = computed(() => {
      return Math.max(0, props.total - props.current)
    })
    
    const elapsedTime = computed(() => {
      const minutes = Math.floor(elapsedSeconds.value / 60)
      const seconds = elapsedSeconds.value % 60
      return `${minutes}:${seconds.toString().padStart(2, '0')}`
    })
    
    const updateElapsed = () => {
      elapsedSeconds.value = Math.floor((Date.now() - startTime.value) / 1000)
    }
    
    const handleCancel = () => {
      emit('cancel')
    }
    
    watch(() => props.show, (isShow) => {
      if (isShow) {
        startTime.value = Date.now()
        elapsedSeconds.value = 0
        timer = setInterval(updateElapsed, 1000)
      } else {
        if (timer) {
          clearInterval(timer)
          timer = null
        }
      }
    })
    
    onUnmounted(() => {
      if (timer) {
        clearInterval(timer)
      }
    })
    
    return {
      progressPercent,
      barClass,
      successCount,
      attemptedCount,
      errorCount,
      remainingCount,
      elapsedTime,
      handleCancel
    }
  }
}
</script>
