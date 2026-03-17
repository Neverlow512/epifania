<template>
  <div class="card bg-black/30 border border-primary/20">
    <div class="card-body p-3">
      <h4 class="text-sm font-semibold text-white mb-2">Frida Status</h4>
      <div class="space-y-2 text-sm">
        <div class="flex items-center justify-between">
          <span class="text-slate-400">Server:</span>
          <div class="flex items-center gap-2">
            <div 
              class="w-2 h-2 rounded-full" 
              :class="fridaServerRunning ? 'bg-green-500 status-indicator' : 'bg-gray-500'"
            ></div>
            <span :class="fridaServerRunning ? 'text-green-400' : 'text-gray-400'">
              {{ fridaServerRunning ? 'Running' : 'Stopped' }}
            </span>
          </div>
        </div>
        
        <div v-if="fridaServerVersion" class="flex items-center justify-between">
          <span class="text-slate-400">Version:</span>
          <span class="text-white font-mono text-xs">{{ fridaServerVersion }}</span>
        </div>
        
        <div class="flex items-center justify-between">
          <span class="text-slate-400">Connection:</span>
          <div class="flex items-center gap-2">
            <div 
              class="w-2 h-2 rounded-full" 
              :class="fridaConnected ? 'bg-green-500 status-indicator' : 'bg-gray-500'"
            ></div>
            <span :class="fridaConnected ? 'text-green-400' : 'text-gray-400'">
              {{ fridaConnected ? 'Connected' : 'Not Connected' }}
            </span>
          </div>
        </div>
      </div>
      
      <div class="flex gap-2 mt-3">
        <button 
          type="button"
          class="btn btn-xs btn-success"
          @click="$emit('start-frida')"
          :disabled="fridaServerRunning"
        >
          Start
        </button>
        <button 
          type="button"
          class="btn btn-xs btn-error"
          @click="$emit('stop-frida')"
          :disabled="!fridaServerRunning"
        >
          Stop
        </button>
        <button 
          type="button"
          class="btn btn-xs btn-warning"
          @click="$emit('restart-frida')"
        >
          Restart
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FridaStatusIndicator',
  props: {
    fridaServerRunning: {
      type: Boolean,
      default: false
    },
    fridaServerVersion: {
      type: String,
      default: null
    },
    fridaConnected: {
      type: Boolean,
      default: false
    }
  },
  emits: ['start-frida', 'stop-frida', 'restart-frida']
}
</script>

