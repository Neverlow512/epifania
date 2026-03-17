<template>
  <div v-if="show" class="modal modal-open">
    <div class="modal-box bg-neutral-900 border border-warning/30">
      <h3 class="font-bold text-lg text-white mb-4 flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-warning" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
        Workshop Session Locked
      </h3>
      
      <p class="text-slate-300 mb-4">
        Another browser tab currently has exclusive access to the Workshop for this device.
      </p>
      
      <div class="bg-black/30 p-4 rounded-lg border border-warning/20 mb-4">
        <div class="space-y-2 text-sm">
          <div class="flex items-center justify-between">
            <span class="text-slate-400">Lock Owner:</span>
            <code class="text-warning font-mono">{{ lockOwner || 'Unknown' }}</code>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-slate-400">Expires In:</span>
            <span class="text-white">{{ expiresIn }}s</span>
          </div>
        </div>
      </div>
      
      <div class="alert alert-info mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-5 w-5" fill="none" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span class="text-sm">The lock will automatically expire after {{ expiresIn }} seconds of inactivity, or you can close the other tab to release it immediately.</span>
      </div>
      
      <div class="modal-action">
        <button 
          type="button"
          class="btn btn-ghost" 
          @click="$emit('close')"
        >
          Close This Tab
        </button>
        <button 
          type="button"
          class="btn btn-primary" 
          @click="$emit('retry')"
        >
          Retry
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SessionLockedModal',
  props: {
    show: {
      type: Boolean,
      required: true
    },
    lockOwner: {
      type: String,
      default: null
    },
    expiresIn: {
      type: Number,
      default: 0
    }
  },
  emits: ['close', 'retry']
}
</script>

