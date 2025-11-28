<template>
  <div class="card bg-neutral-900/60 backdrop-blur-sm shadow-xl border border-primary/20">
    <div class="card-body p-4 space-y-3">
      <div class="flex items-center justify-between">
        <h3 class="text-sm font-semibold text-white">Runtime Overview</h3>
        <button
          type="button"
          class="btn btn-ghost btn-xs text-xs px-2 h-6 min-h-0"
          @click="$emit('refresh')"
        >
          Refresh
        </button>
      </div>

      <div class="grid grid-cols-2 gap-3 text-xs">
        <div class="space-y-1">
          <div class="text-slate-400">Total Processes</div>
          <div class="text-white text-lg leading-tight">
            {{ stats.total || 0 }}
          </div>
          <div class="text-slate-500">
            User: {{ stats.user || 0 }} • System: {{ stats.system || 0 }}
          </div>
        </div>

        <div class="space-y-1">
          <div class="text-slate-400">Memory Usage</div>
          <div class="text-white text-lg leading-tight">
            {{ formatMemory(stats.total_memory_mb) }}
          </div>
          <div class="text-slate-500">
            Total RAM consumed
          </div>
        </div>

        <div class="space-y-1">
          <div class="text-slate-400">Auto Refresh</div>
          <div class="flex items-center gap-2">
            <label class="cursor-pointer flex items-center gap-1 text-xs">
              <input
                type="checkbox"
                class="toggle toggle-xs toggle-primary"
                :checked="autoRefresh"
                @change="$emit('toggle-auto-refresh')"
              />
              <span :class="autoRefresh ? 'text-green-400' : 'text-slate-500'">
                {{ autoRefresh ? 'On' : 'Off' }}
              </span>
            </label>
          </div>
          <div class="text-slate-500">
            {{ refreshInterval / 1000 }}s interval
          </div>
        </div>

        <div class="space-y-1">
          <div class="text-slate-400">Last Updated</div>
          <div class="text-white">
            {{ lastUpdate }}
          </div>
        </div>
      </div>

      <div class="pt-2 border-t border-primary/20 space-y-3">
        <div class="flex items-center justify-between text-xs">
          <span class="text-slate-400">Refresh Interval</span>
          <div class="join join-xs">
            <button
              v-for="option in intervalOptions"
              :key="option"
              type="button"
              class="btn btn-xs join-item px-2"
              :class="option === refreshInterval ? 'btn-primary' : 'btn-ghost text-slate-400'"
              @click="$emit('update-refresh-interval', option)"
            >
              {{ option / 1000 }}s
            </button>
          </div>
        </div>

        <div class="space-y-2">
          <div class="flex items-center justify-between text-xs text-slate-400">
            <span>Processes over time</span>
            <span v-if="processHistory && processHistory.length" class="text-slate-500">
              {{ processHistory[processHistory.length - 1].total }} now
            </span>
          </div>
          <div class="h-10 bg-black/40 rounded overflow-hidden">
            <svg
              v-if="processHistory && processHistory.length > 1"
              class="w-full h-full"
              viewBox="0 0 100 40"
              preserveAspectRatio="none"
            >
              <polyline
                :points="buildLinePoints(processHistory.map(p => p.total))"
                fill="none"
                stroke="#7100d0"
                stroke-width="1.5"
              />
            </svg>
          </div>

          <div class="flex items-center justify-between text-xs text-slate-400">
            <span>Memory over time</span>
            <span v-if="memoryHistory && memoryHistory.length" class="text-slate-500">
              {{ formatMemory(memoryHistory[memoryHistory.length - 1].memoryMb) }} now
            </span>
          </div>
          <div class="h-10 bg-black/40 rounded overflow-hidden">
            <svg
              v-if="memoryHistory && memoryHistory.length > 1"
              class="w-full h-full"
              viewBox="0 0 100 40"
              preserveAspectRatio="none"
            >
              <polyline
                :points="buildLinePoints(memoryHistory.map(p => p.memoryMb))"
                fill="none"
                stroke="#10b981"
                stroke-width="1.5"
              />
            </svg>
          </div>
        </div>
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
    },
    processHistory: {
      type: Array,
      default: () => []
    },
    memoryHistory: {
      type: Array,
      default: () => []
    }
  },
  emits: ['refresh', 'toggle-auto-refresh', 'update-refresh-interval'],
  methods: {
    buildLinePoints(values) {
      if (!values || values.length < 2) return ''

      const max = Math.max(...values)
      const min = Math.min(...values)
      const span = max - min || 1
      const step = values.length > 1 ? 100 / (values.length - 1) : 100

      return values
        .map((v, index) => {
          const x = step * index
          const normalized = (v - min) / span
          const y = 40 - normalized * 30 - 5
          return `${x},${y}`
        })
        .join(' ')
    },
    formatMemory(mb) {
      if (!mb) return '0 MB'
      if (mb < 1) return `${(mb * 1024).toFixed(0)} KB`
      return `${mb.toFixed(1)} MB`
    }
  },
  computed: {
    intervalOptions() {
      return [1000, 2000, 5000, 10000]
    }
  }
}
</script>

