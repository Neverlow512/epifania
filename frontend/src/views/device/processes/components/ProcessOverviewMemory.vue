<template>
  <div class="space-y-2">
    <div class="flex items-center gap-2">
      <div class="w-7 h-7 rounded bg-emerald-500/20 flex items-center justify-center flex-shrink-0">
        <svg class="w-4 h-4 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
      </div>
      <span class="text-xs text-slate-400 font-medium">Memory</span>
    </div>

    <div v-if="memory" class="bg-black/40 rounded-lg border border-slate-700/50 p-3 space-y-3">
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
        <div>
          <div class="text-slate-500">RSS</div>
          <div class="text-white font-mono">{{ formatKb(memory.rss_kb) }}</div>
        </div>
        <div>
          <div class="text-slate-500">PSS</div>
          <div class="text-white font-mono">{{ formatKb(effectivePss) }}</div>
          <div v-if="!memory.smaps_available && memory.dumpsys_available" class="text-[10px] text-slate-600">(dumpsys)</div>
        </div>
        <div v-if="memory.uss_kb">
          <div class="text-slate-500">USS</div>
          <div class="text-white font-mono">{{ formatKb(memory.uss_kb) }}</div>
        </div>
        <div v-if="memory.swap_kb">
          <div class="text-slate-500">Swap</div>
          <div class="text-white font-mono">{{ formatKb(memory.swap_kb) }}</div>
        </div>
      </div>

      <div v-if="memory.dumpsys && memory.dumpsys_available" class="border-t border-neutral-800 pt-2">
        <div class="text-[10px] text-slate-500 mb-2">Heap Breakdown (dumpsys)</div>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
          <div v-if="memory.dumpsys.java_heap_kb">
            <span class="text-slate-500">Java:</span>
            <span class="text-emerald-400 ml-1">{{ formatKb(memory.dumpsys.java_heap_kb) }}</span>
          </div>
          <div v-if="memory.dumpsys.native_heap_kb">
            <span class="text-slate-500">Native:</span>
            <span class="text-blue-400 ml-1">{{ formatKb(memory.dumpsys.native_heap_kb) }}</span>
          </div>
          <div v-if="memory.dumpsys.code_kb">
            <span class="text-slate-500">Code:</span>
            <span class="text-violet-400 ml-1">{{ formatKb(memory.dumpsys.code_kb) }}</span>
          </div>
          <div v-if="memory.dumpsys.graphics_kb">
            <span class="text-slate-500">Graphics:</span>
            <span class="text-amber-400 ml-1">{{ formatKb(memory.dumpsys.graphics_kb) }}</span>
          </div>
          <div v-if="memory.dumpsys.stack_kb">
            <span class="text-slate-500">Stack:</span>
            <span class="text-slate-300 ml-1">{{ formatKb(memory.dumpsys.stack_kb) }}</span>
          </div>
          <div v-if="memory.dumpsys.system_kb">
            <span class="text-slate-500">System:</span>
            <span class="text-slate-300 ml-1">{{ formatKb(memory.dumpsys.system_kb) }}</span>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="bg-black/40 rounded-lg border border-slate-700/50 p-3">
      <div class="flex items-center gap-2 text-slate-500 text-xs">
        <svg class="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div>
          <span class="block">Memory info not available</span>
          <span class="text-[10px] text-slate-600">Kernel threads do not have userspace memory</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProcessOverviewMemory',
  props: {
    memory: {
      type: Object,
      default: null
    }
  },
  computed: {
    effectivePss() {
      if (this.memory?.pss_kb) return this.memory.pss_kb
      if (this.memory?.dumpsys?.total_pss_kb) return this.memory.dumpsys.total_pss_kb
      return null
    }
  },
  methods: {
    formatKb(kb) {
      if (!kb) return 'N/A'
      if (kb < 1024) return `${kb} KB`
      const mb = kb / 1024
      if (mb < 1024) return `${mb.toFixed(1)} MB`
      const gb = mb / 1024
      return `${gb.toFixed(2)} GB`
    }
  }
}
</script>

