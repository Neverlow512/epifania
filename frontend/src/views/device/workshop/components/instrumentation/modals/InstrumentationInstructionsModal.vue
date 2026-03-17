<template>
  <Teleport to="body">
    <div v-if="show" class="fixed inset-0 z-[99999] flex items-center justify-center p-4">
      <div
        class="absolute inset-0 bg-black/70 backdrop-blur-sm"
        @click="$emit('close')"
      ></div>
      
      <div class="relative bg-neutral-900 border border-primary/30 rounded-xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        <button 
          class="btn btn-sm btn-circle absolute right-4 top-4 z-10"
          @click="$emit('close')"
        >
          ✕
        </button>
        
        <div class="p-6">
          <div class="flex items-center gap-3 mb-6">
            <div class="p-3 bg-primary/20 rounded-lg">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <div>
              <h3 class="text-xl font-bold text-white">Instrumentation Instructions</h3>
              <p class="text-sm text-slate-400">Coming Soon</p>
            </div>
          </div>
          
          <div class="space-y-4">
            <div class="alert bg-neutral-800/50 border border-primary/30">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <p class="text-sm text-white">Step-by-step instructions for Instrumentation Mode are under development.</p>
              </div>
            </div>
            
            <div class="space-y-3">
              <h4 class="text-sm font-semibold text-white">Instruction Guides (Coming Soon):</h4>
              
              <div class="space-y-2">
                <div class="bg-neutral-800/30 rounded p-3">
                  <h5 class="text-sm font-semibold text-white mb-2">Getting Started with Hooks</h5>
                  <p class="text-xs text-slate-400">Learn the basics of applying hooks to discovered methods.</p>
                </div>
                
                <div class="bg-neutral-800/30 rounded p-3">
                  <h5 class="text-sm font-semibold text-white mb-2">Using Hook Templates</h5>
                  <p class="text-xs text-slate-400">Apply pre-built hooks for common instrumentation patterns.</p>
                </div>
                
                <div class="bg-neutral-800/30 rounded p-3">
                  <h5 class="text-sm font-semibold text-white mb-2">Custom Plugin Development</h5>
                  <p class="text-xs text-slate-400">Create and load your own Frida scripts as plugins.</p>
                </div>
                
                <div class="bg-neutral-800/30 rounded p-3">
                  <h5 class="text-sm font-semibold text-white mb-2">Monitoring Hook Events</h5>
                  <p class="text-xs text-slate-400">Use the real-time console to view hook triggers and outputs.</p>
                </div>
                
                <div class="bg-neutral-800/30 rounded p-3">
                  <h5 class="text-sm font-semibold text-white mb-2">Advanced Techniques</h5>
                  <p class="text-xs text-slate-400">Hook recipes, bulk operations, and session recording.</p>
                </div>
              </div>
            </div>
            
            <div class="divider"></div>
            
            <p class="text-xs text-slate-500 text-center">
              Detailed step-by-step guides will be available once instrumentation features are implemented.
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
  name: 'InstrumentationInstructionsModal',
  props: {
    show: {
      type: Boolean,
      required: true
    }
  },
  emits: ['close']
}
</script>
