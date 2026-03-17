<template>
  <Teleport to="body">
    <div v-if="show" class="fixed inset-0 z-[99999] flex items-center justify-center p-4">
      <div
        class="absolute inset-0 bg-black/70 backdrop-blur-sm"
        @click="$emit('close')"
      ></div>
      
      <div class="relative bg-neutral-900 border border-primary/30 rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <button 
          class="btn btn-sm btn-circle absolute right-4 top-4 z-10"
          @click="$emit('close')"
        >
          ✕
        </button>
        
        <div class="p-6">
          <div class="flex items-center gap-3 mb-6">
            <div class="p-3 bg-accent/20 rounded-lg">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <h3 class="text-xl font-bold text-white">Instrumentation Control Help</h3>
              <p class="text-sm text-slate-400">Coming Soon</p>
            </div>
          </div>
          
          <div class="space-y-4">
            <div class="alert bg-neutral-800/50 border border-accent/30">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <p class="text-sm text-white">Help documentation for Instrumentation Control panel is under development.</p>
              </div>
            </div>
            
            <div class="space-y-2">
              <h4 class="text-sm font-semibold text-white">Control Panel Features (Coming Soon):</h4>
              
              <div class="bg-neutral-800/30 rounded p-3 space-y-2 text-sm text-slate-300">
                <p>• Managing hook templates</p>
                <p>• Loading and configuring plugins</p>
                <p>• Viewing active hooks</p>
                <p>• Real-time console output</p>
                <p>• Hook session management</p>
                <p>• Bulk hook operations</p>
              </div>
            </div>
            
            <div class="divider"></div>
            
            <p class="text-xs text-slate-500 text-center">
              Check back soon for comprehensive control panel documentation.
            </p>
          </div>
          
          <div class="flex justify-end mt-6">
            <button 
              class="btn btn-primary"
              @click="$emit('close')"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script>
export default {
  name: 'InstrumentationControlHelpModal',
  props: {
    show: {
      type: Boolean,
      required: true
    }
  },
  emits: ['close']
}
</script>
