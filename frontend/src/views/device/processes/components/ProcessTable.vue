<template>
  <div class="card bg-neutral-900/60 backdrop-blur-sm shadow-xl border border-primary/20">
    <div class="card-body p-0">
      <div class="overflow-x-auto">
        <table class="table table-sm">
          <thead>
            <tr class="border-b border-primary/20">
              <th class="text-slate-400">PID</th>
              <th class="text-slate-400">Process Name</th>
              <th class="text-slate-400">User</th>
              <th class="text-slate-400">Memory</th>
              <th class="text-slate-400">State</th>
              <th class="text-slate-400">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading && paginatedProcesses.length === 0">
              <td colspan="6" class="text-center py-8">
                <span class="loading loading-spinner loading-lg text-primary"></span>
              </td>
            </tr>
            <tr v-else-if="paginatedProcesses.length === 0">
              <td colspan="6" class="text-center py-8 text-slate-400">
                No processes found
              </td>
            </tr>
            <tr 
              v-for="process in paginatedProcesses" 
              :key="process.pid"
              class="hover:bg-primary/5 border-b border-neutral-800"
            >
              <td class="font-mono text-primary">{{ process.pid }}</td>
              <td class="text-white">
                <div class="flex items-center gap-2">
                  <span class="font-medium">{{ process.name }}</span>
                </div>
                <div class="text-xs text-slate-500 font-mono truncate max-w-xs" :title="process.command">
                  {{ process.command }}
                </div>
              </td>
              <td class="text-slate-300 font-mono text-xs">{{ process.user }}</td>
              <td class="text-slate-300">{{ formatMemory(process.memory_mb) }}</td>
              <td>
                <span 
                  class="badge badge-xs"
                  :class="getStateBadgeClass(process.state)"
                >
                  {{ process.state }}
                </span>
              </td>
              <td>
                <div class="flex gap-1">
                  <button 
                    class="btn btn-xs btn-ghost text-blue-400"
                    @click="$emit('inspect', process)"
                    title="Inspect"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  </button>
                  <button 
                    class="btn btn-xs btn-ghost text-red-400"
                    @click="$emit('kill', process)"
                    title="Kill Process"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div class="flex justify-between items-center p-4 border-t border-primary/20">
        <div class="text-sm text-slate-400">
          Showing {{ startIndex + 1 }}-{{ endIndex }} of {{ totalCount }} processes
        </div>
        <div class="flex gap-2">
          <button 
            class="btn btn-sm btn-ghost"
            @click="$emit('page-change', currentPage - 1)"
            :disabled="currentPage === 0"
          >
            Previous
          </button>
          <button 
            class="btn btn-sm btn-ghost"
            @click="$emit('page-change', currentPage + 1)"
            :disabled="endIndex >= totalCount"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProcessTable',
  props: {
    paginatedProcesses: {
      type: Array,
      default: () => []
    },
    startIndex: {
      type: Number,
      default: 0
    },
    endIndex: {
      type: Number,
      default: 0
    },
    totalCount: {
      type: Number,
      default: 0
    },
    currentPage: {
      type: Number,
      default: 0
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['inspect', 'kill', 'page-change'],
  methods: {
    formatMemory(mb) {
      if (!mb) return '0 MB'
      if (mb < 1) return `${(mb * 1024).toFixed(0)} KB`
      return `${mb.toFixed(1)} MB`
    },
    getStateBadgeClass(state) {
      const stateMap = {
        'running': 'badge-success',
        'sleeping': 'badge-info',
        'zombie': 'badge-error',
        'traced': 'badge-warning',
        'disk_sleep': 'badge-warning'
      }
      return stateMap[state] || 'badge-ghost'
    }
  }
}
</script>

