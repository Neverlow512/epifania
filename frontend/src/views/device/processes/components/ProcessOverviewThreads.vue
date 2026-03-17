<template>
  <div class="space-y-2">
    <div class="flex items-center gap-2">
      <div class="w-7 h-7 rounded bg-amber-500/20 flex items-center justify-center flex-shrink-0">
        <svg class="w-4 h-4 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h7" />
        </svg>
      </div>
      <span class="text-xs text-slate-400 font-medium">Threads</span>
      <span class="text-xs text-slate-500">{{ threads?.count || 0 }}</span>
      <button
        v-if="threads?.threads?.length > 3"
        type="button"
        class="ml-auto text-[9px] text-slate-500 hover:text-amber-400 transition-colors border border-slate-700 hover:border-amber-500/50 rounded px-1.5 py-0.5"
        @click="showModal = true"
      >
        View all
      </button>
    </div>

    <div v-if="threads?.threads?.length" class="bg-black/40 rounded-lg border border-slate-700/50 p-3">
      <div class="space-y-1.5">
        <div
          v-for="thread in topThreads"
          :key="thread.tid"
          class="flex items-center justify-between text-xs"
        >
          <div class="flex items-center gap-2">
            <span class="text-primary font-mono w-12">{{ thread.tid }}</span>
            <span class="text-slate-300 truncate max-w-[120px]" :title="thread.name">{{ thread.name }}</span>
            <span v-if="thread.is_main" class="text-[9px] px-1 py-0.5 rounded bg-violet-500/20 text-violet-400">main</span>
          </div>
          <span class="text-slate-500 font-mono">{{ formatTicks(thread.cpu_time_ticks) }}</span>
        </div>
      </div>
    </div>

    <div v-else class="bg-black/40 rounded-lg border border-slate-700/50 p-3">
      <div class="flex items-center gap-2 text-slate-500 text-xs">
        <svg class="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div>
          <span class="block">Thread info not available</span>
          <span class="text-[10px] text-slate-600">Unable to read /proc/[pid]/task</span>
        </div>
      </div>
    </div>

    <ProcessOverviewDetailModal
      :show="showModal"
      title="All Threads"
      :subtitle="`${threads?.count || 0} threads`"
      icon-bg-class="bg-amber-500/20"
      icon-class="text-amber-400"
      max-width="2xl"
      @close="showModal = false"
    >
      <template #icon>
        <svg class="w-5 h-5 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h7" />
        </svg>
      </template>

      <div class="overflow-x-auto">
        <table class="table table-xs w-full">
          <thead>
            <tr class="text-slate-400 border-neutral-800">
              <th>TID</th>
              <th>Name</th>
              <th>State</th>
              <th class="text-right">CPU Time</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="thread in threads?.threads || []"
              :key="thread.tid"
              class="border-neutral-800 hover:bg-neutral-800/50"
            >
              <td class="font-mono text-primary">{{ thread.tid }}</td>
              <td class="text-slate-200">
                {{ thread.name }}
                <span v-if="thread.is_main" class="ml-1 text-[9px] px-1 py-0.5 rounded bg-violet-500/20 text-violet-400">main</span>
              </td>
              <td>
                <span class="badge badge-xs" :class="getStateBadge(thread.state)">{{ thread.state }}</span>
              </td>
              <td class="text-right text-slate-300 font-mono">{{ formatTicks(thread.cpu_time_ticks) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </ProcessOverviewDetailModal>
  </div>
</template>

<script>
import ProcessOverviewDetailModal from './ProcessOverviewDetailModal.vue'

export default {
  name: 'ProcessOverviewThreads',
  components: {
    ProcessOverviewDetailModal
  },
  props: {
    threads: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      showModal: false
    }
  },
  computed: {
    topThreads() {
      if (!this.threads?.threads) return []
      return [...this.threads.threads]
        .sort((a, b) => (b.cpu_time_ticks || 0) - (a.cpu_time_ticks || 0))
        .slice(0, 3)
    }
  },
  methods: {
    formatTicks(ticks) {
      if (!ticks && ticks !== 0) return 'N/A'
      if (ticks < 1000) return `${ticks} ticks`
      if (ticks < 1000000) return `${(ticks / 1000).toFixed(1)}K`
      return `${(ticks / 1000000).toFixed(1)}M`
    },
    getStateBadge(state) {
      const map = {
        'S': 'badge-info',
        'R': 'badge-success',
        'D': 'badge-warning',
        'Z': 'badge-error',
        'T': 'badge-secondary'
      }
      return map[state] || 'badge-ghost'
    }
  }
}
</script>

