<template>
  <div class="card bg-black/30 border border-primary/20">
    <div class="card-body p-3">
      <h4 class="text-sm font-semibold text-white mb-2">Discovery Progress</h4>
      
      <div class="space-y-3">
        <div class="flex items-center justify-between text-sm">
          <span class="text-slate-400">{{ phase }}</span>
          <span class="text-primary font-semibold">{{ progress }}%</span>
        </div>
        
        <progress 
          class="progress progress-primary w-full" 
          :value="progress" 
          max="100"
        ></progress>
        
        <div v-if="message" class="text-xs text-slate-500 truncate" :title="message">
          {{ message }}
        </div>
        
        <button 
          type="button"
          class="btn btn-sm btn-warning btn-block"
          @click="$emit('cancel')"
        >
          Cancel Discovery
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DiscoveryProgress',
  props: {
    progress: {
      type: Number,
      default: 0
    },
    phase: {
      type: String,
      default: ''
    },
    message: {
      type: String,
      default: ''
    }
  },
  emits: ['cancel']
}
</script>

