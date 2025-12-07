<template>
  <div class="space-y-4">
    <div class="card bg-neutral-900/60 backdrop-blur-sm shadow-xl border border-primary/20">
      <div class="card-body p-4">
        <h3 class="text-sm font-medium text-slate-300 mb-3">Package Statistics</h3>

        <div class="grid grid-cols-2 gap-3">
          <div class="bg-black/40 rounded-lg p-3 border border-neutral-800">
            <div class="text-2xl font-bold text-white">{{ totalCount }}</div>
            <div class="text-xs text-slate-500">Total Packages</div>
          </div>
          <div class="bg-black/40 rounded-lg p-3 border border-neutral-800">
            <div class="text-2xl font-bold text-emerald-400">{{ stats.running || 0 }}</div>
            <div class="text-xs text-slate-500">Running</div>
          </div>
          <div class="bg-black/40 rounded-lg p-3 border border-neutral-800">
            <div class="text-2xl font-bold text-violet-400">{{ stats.user || 0 }}</div>
            <div class="text-xs text-slate-500">User Apps</div>
          </div>
          <div class="bg-black/40 rounded-lg p-3 border border-neutral-800">
            <div class="text-2xl font-bold text-slate-400">{{ stats.system || 0 }}</div>
            <div class="text-xs text-slate-500">System Apps</div>
          </div>
        </div>

        <div class="text-xs text-slate-500 mt-3">
          Last updated: {{ lastUpdate }}
        </div>
      </div>
    </div>

    <div class="card bg-neutral-900/60 backdrop-blur-sm shadow-xl border border-primary/20">
      <div class="card-body p-4">
        <h3 class="text-sm font-medium text-slate-300 mb-3">Quick Actions</h3>

        <div class="space-y-2">
          <button
            type="button"
            class="btn btn-sm btn-primary w-full"
            @click="$emit('install')"
          >
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Install APK
          </button>

          <button
            type="button"
            class="btn btn-sm btn-ghost w-full"
            :disabled="loading"
            @click="$emit('refresh')"
          >
            <svg
              class="w-4 h-4"
              :class="{ 'animate-spin': loading }"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh List
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'PackageStatsBar',
  props: {
    stats: {
      type: Object,
      default: () => ({ user: 0, system: 0, running: 0 })
    },
    lastUpdate: {
      type: String,
      default: 'Never'
    },
    loading: {
      type: Boolean,
      default: false
    },
    activeFilter: {
      type: String,
      default: 'user'
    },
    hasActiveFilters: {
      type: Boolean,
      default: false
    }
  },
  emits: ['refresh', 'clear-filters', 'install'],
  setup(props) {
    const totalCount = computed(() => {
      return (props.stats.user || 0) + (props.stats.system || 0)
    })

    return {
      totalCount
    }
  }
}
</script>
