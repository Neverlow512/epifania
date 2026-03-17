<template>
  <Teleport to="body">
    <div v-if="show" class="modal modal-open">
      <div class="modal-box bg-neutral-900 border border-yellow-500/30 max-w-md">
        <h3 class="font-bold text-lg text-yellow-400 flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          Active Frida Session
        </h3>
        
        <div class="mt-4 space-y-4">
          <p class="text-slate-300">
            You have an active Frida session attached to the target process. Leaving this tab will detach the session.
          </p>
          
          <div class="bg-neutral-800 rounded-lg p-4 space-y-2">
            <div class="flex justify-between text-sm">
              <span class="text-slate-400">Attached PID:</span>
              <span class="text-white font-mono">{{ pid }}</span>
            </div>
            <div v-if="unsavedCount > 0" class="flex justify-between text-sm">
              <span class="text-slate-400">Unsaved classes:</span>
              <span class="text-yellow-400 font-medium">{{ unsavedCount }}</span>
            </div>
          </div>
          
          <div class="text-sm text-slate-400">
            Are you sure you want to leave?
          </div>
        </div>
        
        <div class="modal-action">
          <button 
            class="btn btn-ghost btn-sm"
            @click="$emit('confirm')"
          >
            Leave Anyway
          </button>
          <button 
            class="btn btn-primary btn-sm"
            @click="$emit('cancel')"
          >
            Stay
          </button>
        </div>
      </div>
      <div class="modal-backdrop bg-black/70" @click.stop></div>
    </div>
  </Teleport>
</template>

<script>
export default {
  name: 'ExitWarningModal',
  props: {
    show: {
      type: Boolean,
      required: true
    },
    pid: {
      type: [Number, String],
      default: ''
    },
    unsavedCount: {
      type: Number,
      default: 0
    }
  },
  emits: ['confirm', 'cancel']
}
</script>
