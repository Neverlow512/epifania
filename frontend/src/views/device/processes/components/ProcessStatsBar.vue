<template>
  <div class="grid grid-cols-4 gap-3">
    <div class="stat bg-neutral-900/60 backdrop-blur-sm rounded-lg p-4 border border-primary/20">
      <div class="stat-title text-slate-400 text-xs">Total Processes</div>
      <div class="stat-value text-white text-2xl">{{ stats.total || 0 }}</div>
      <div class="stat-desc text-slate-500 text-xs">
        User: {{ stats.user || 0 }} • System: {{ stats.system || 0 }}
      </div>
    </div>
    <div class="stat bg-neutral-900/60 backdrop-blur-sm rounded-lg p-4 border border-primary/20">
      <div class="stat-title text-slate-400 text-xs">Memory Usage</div>
      <div class="stat-value text-white text-2xl">{{ formatMemory(stats.total_memory_mb) }}</div>
      <div class="stat-desc text-slate-500 text-xs">Total RAM consumed</div>
    </div>
    <div class="stat bg-neutral-900/60 backdrop-blur-sm rounded-lg p-4 border border-primary/20">
      <div class="stat-title text-slate-400 text-xs">Auto Refresh</div>
      <div class="stat-value text-sm">
        <label class="swap swap-flip">
          <input type="checkbox" :checked="autoRefresh" @change="$emit('toggle-auto-refresh')" />
          <div class="swap-on text-green-400">ON</div>
          <div class="swap-off text-gray-400">OFF</div>
        </label>
      </div>
      <div class="stat-desc text-slate-500 text-xs">{{ refreshInterval / 1000 }}s interval</div>
    </div>
    <div class="stat bg-neutral-900/60 backdrop-blur-sm rounded-lg p-4 border border-primary/20">
      <div class="stat-title text-slate-400 text-xs">Last Updated</div>
      <div class="stat-value text-white text-sm">{{ lastUpdate }}</div>
      <div class="stat-desc text-slate-500 text-xs">
        <button 
          class="btn btn-xs btn-outline btn-primary mt-1"
          @click="$emit('refresh')"
          :disabled="loading"
        >
          {{ loading ? 'Refreshing...' : 'Refresh Now' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProcessStatsBar',
  props: {
    stats: {
      type: Object,
      default: () => ({})
    },
    autoRefresh: {
      type: Boolean,
      default: true
    },
    refreshInterval: {
      type: Number,
      default: 2000
    },
    lastUpdate: {
      type: String,
      default: 'Never'
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['refresh', 'toggle-auto-refresh'],
  methods: {
    formatMemory(mb) {
      if (!mb) return '0 MB'
      if (mb < 1) return `${(mb * 1024).toFixed(0)} KB`
      return `${mb.toFixed(1)} MB`
    }
  }
}
</script>

