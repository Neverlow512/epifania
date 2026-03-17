<template>
  <div v-if="show && process" class="modal modal-open">
    <div class="modal-box bg-neutral-900 border border-primary/30">
      <h3 class="font-bold text-lg text-white mb-4">Confirm Kill Process</h3>
      <p class="text-slate-300 mb-4">
        Are you sure you want to terminate this process?
      </p>
      <div class="bg-black/30 p-3 rounded mb-4">
        <div class="text-sm"><span class="text-slate-400">PID:</span> <span class="text-white">{{ process.pid }}</span></div>
        <div class="text-sm"><span class="text-slate-400">Name:</span> <span class="text-white">{{ process.name }}</span></div>
        <div class="text-sm"><span class="text-slate-400">User:</span> <span class="text-white">{{ process.user }}</span></div>
      </div>
      <div class="alert alert-warning mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <span>This action cannot be undone. The process will be forcefully terminated.</span>
      </div>
      <div class="modal-action">
        <button class="btn btn-ghost" @click="$emit('close')">Cancel</button>
        <button class="btn btn-error" @click="$emit('confirm')" :disabled="killing">
          {{ killing ? 'Killing...' : 'Kill Process' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProcessKillModal',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    process: {
      type: Object,
      default: null
    },
    killing: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close', 'confirm']
}
</script>

