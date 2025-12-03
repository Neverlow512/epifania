<template>
  <div class="space-y-2">
    <div class="flex items-center gap-2">
      <div class="w-7 h-7 rounded bg-cyan-500/20 flex items-center justify-center flex-shrink-0">
        <svg class="w-4 h-4 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
        </svg>
      </div>
      <span class="text-xs text-slate-400 font-medium">I/O Stats</span>
    </div>

    <div v-if="io && io.available" class="bg-black/40 rounded-lg border border-slate-700/50 p-3">
      <div class="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
        <div>
          <div class="text-slate-500">Read</div>
          <div class="text-green-400 font-mono">{{ formatBytes(io.read_bytes) }}</div>
        </div>
        <div>
          <div class="text-slate-500">Write</div>
          <div class="text-blue-400 font-mono">{{ formatBytes(io.write_bytes) }}</div>
        </div>
        <div v-if="io.cancelled_write_bytes">
          <div class="text-slate-500">Cancelled</div>
          <div class="text-amber-400 font-mono">{{ formatBytes(io.cancelled_write_bytes) }}</div>
        </div>
        <div>
          <div class="text-slate-500">Read Syscalls</div>
          <div class="text-slate-300 font-mono">{{ formatNumber(io.syscr) }}</div>
        </div>
        <div>
          <div class="text-slate-500">Write Syscalls</div>
          <div class="text-slate-300 font-mono">{{ formatNumber(io.syscw) }}</div>
        </div>
      </div>
    </div>

    <div v-else class="bg-black/40 rounded-lg border border-slate-700/50 p-3">
      <div class="flex items-center gap-2 text-slate-500 text-xs">
        <svg v-if="errorReason === 'kernel_not_supported'" class="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
        <svg v-else class="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
        <div>
          <span class="block">{{ errorTitle }}</span>
          <span class="text-[10px] text-slate-600">{{ errorDescription }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProcessOverviewIO',
  props: {
    io: {
      type: Object,
      default: null
    },
    available: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    errorReason() {
      return this.io?.error || 'permission_denied'
    },
    errorTitle() {
      const titles = {
        kernel_not_supported: 'I/O stats not supported',
        permission_denied: 'I/O stats not available',
        unknown: 'I/O stats unavailable',
        parse_error: 'I/O stats error'
      }
      return titles[this.errorReason] || 'I/O stats not available'
    },
    errorDescription() {
      const descriptions = {
        kernel_not_supported: 'Kernel not compiled with CONFIG_TASK_IO_ACCOUNTING',
        permission_denied: 'Requires root access to read /proc/[pid]/io',
        unknown: 'Could not read I/O statistics',
        parse_error: 'Failed to parse I/O statistics'
      }
      return descriptions[this.errorReason] || 'Requires root access to read /proc/[pid]/io'
    }
  },
  methods: {
    formatBytes(bytes) {
      if (!bytes && bytes !== 0) return 'N/A'
      if (bytes < 1024) return `${bytes} B`
      const kb = bytes / 1024
      if (kb < 1024) return `${kb.toFixed(1)} KB`
      const mb = kb / 1024
      if (mb < 1024) return `${mb.toFixed(1)} MB`
      const gb = mb / 1024
      return `${gb.toFixed(2)} GB`
    },
    formatNumber(num) {
      if (!num && num !== 0) return 'N/A'
      if (num < 1000) return num.toString()
      if (num < 1000000) return `${(num / 1000).toFixed(1)}K`
      return `${(num / 1000000).toFixed(1)}M`
    }
  }
}
</script>

