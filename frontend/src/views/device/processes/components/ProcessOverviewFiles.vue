<template>
  <div class="space-y-2">
    <div class="flex items-center gap-2">
      <div class="w-7 h-7 rounded bg-indigo-500/20 flex items-center justify-center flex-shrink-0">
        <svg class="w-4 h-4 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
        </svg>
      </div>
      <span class="text-xs text-slate-400 font-medium">File Descriptors</span>
      <span class="text-xs text-slate-500">{{ files?.count || 0 }}</span>
      <button
        v-if="files?.fds?.length"
        type="button"
        class="ml-auto text-[9px] text-slate-500 hover:text-indigo-400 transition-colors border border-slate-700 hover:border-indigo-500/50 rounded px-1.5 py-0.5"
        @click="openModal"
      >
        View all
      </button>
    </div>

    <div v-if="files" class="bg-black/40 rounded-lg border border-slate-700/50 p-3 space-y-2">
      <div v-if="!files.full_access" class="flex items-center gap-2 text-amber-400 text-xs mb-2">
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
        <span>Limited access (requires root for full list)</span>
      </div>

      <div class="flex flex-wrap gap-2 text-xs">
        <div
          v-for="(count, type) in files.categories"
          :key="type"
          class="px-2 py-1 rounded bg-neutral-800 border border-neutral-700"
        >
          <span class="text-slate-400">{{ type }}:</span>
          <span class="text-white ml-1 font-mono">{{ count }}</span>
        </div>
      </div>

      <div v-if="files.soft_limit || files.hard_limit" class="text-[10px] text-slate-500 pt-1 border-t border-neutral-800">
        Limit: {{ files.soft_limit || 'N/A' }} / {{ files.hard_limit || 'N/A' }}
      </div>
    </div>

    <div v-else class="bg-black/40 rounded-lg border border-slate-700/50 p-3">
      <div class="flex items-center gap-2 text-slate-500 text-xs">
        <svg class="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
        <div>
          <span class="block">File descriptors not accessible</span>
          <span class="text-[10px] text-slate-600">Permission denied or process has no open files</span>
        </div>
      </div>
    </div>

    <ProcessOverviewDetailModal
      :show="showModal"
      title="File Descriptors"
      :subtitle="`${files?.count || 0} open files`"
      icon-bg-class="bg-indigo-500/20"
      icon-class="text-indigo-400"
      max-width="3xl"
      @close="closeModal"
    >
      <template #icon>
        <svg class="w-5 h-5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
        </svg>
      </template>

      <div class="space-y-3">
        <div class="flex items-center justify-between gap-4">
          <div class="flex items-center gap-2">
            <input
              v-model="filterText"
              type="text"
              placeholder="Filter by target or type..."
              class="input input-xs input-bordered bg-neutral-900 border-neutral-700 text-slate-300 w-48"
            />
            <select
              v-model="filterType"
              class="select select-xs select-bordered bg-neutral-900 border-neutral-700 text-slate-300"
            >
              <option value="">All types</option>
              <option v-for="type in availableTypes" :key="type" :value="type">{{ type }}</option>
            </select>
          </div>
          <div class="text-xs text-slate-500">
            {{ filteredFds.length }} of {{ files?.fds?.length || 0 }}
          </div>
        </div>

        <div class="overflow-x-auto max-h-[50vh]">
          <table class="table table-xs w-full">
            <thead class="sticky top-0 bg-neutral-900 z-10">
              <tr class="text-slate-400 border-neutral-800">
                <th class="w-16">FD</th>
                <th class="w-24">Type</th>
                <th>Target</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="fd in paginatedFds"
                :key="fd.fd"
                class="border-neutral-800 hover:bg-neutral-800/50"
              >
                <td class="font-mono text-primary">{{ fd.fd }}</td>
                <td>
                  <span class="badge badge-xs" :class="getTypeBadge(fd.type)">{{ fd.type }}</span>
                </td>
                <td class="text-slate-300 font-mono text-[11px] break-all">{{ fd.target }}</td>
              </tr>
              <tr v-if="!paginatedFds.length">
                <td colspan="3" class="text-center text-slate-500 py-4">
                  {{ filterText || filterType ? 'No matching file descriptors' : 'No file descriptors' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="totalPages > 1" class="flex items-center justify-between pt-2 border-t border-neutral-800">
          <div class="text-xs text-slate-500">
            Page {{ currentPage }} of {{ totalPages }}
          </div>
          <div class="flex items-center gap-1">
            <button
              type="button"
              class="btn btn-xs btn-ghost"
              :disabled="currentPage === 1"
              @click="currentPage = 1"
            >
              <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
              </svg>
            </button>
            <button
              type="button"
              class="btn btn-xs btn-ghost"
              :disabled="currentPage === 1"
              @click="currentPage--"
            >
              <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <span class="px-2 text-xs text-slate-400">{{ currentPage }}</span>
            <button
              type="button"
              class="btn btn-xs btn-ghost"
              :disabled="currentPage === totalPages"
              @click="currentPage++"
            >
              <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </button>
            <button
              type="button"
              class="btn btn-xs btn-ghost"
              :disabled="currentPage === totalPages"
              @click="currentPage = totalPages"
            >
              <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </ProcessOverviewDetailModal>
  </div>
</template>

<script>
import ProcessOverviewDetailModal from './ProcessOverviewDetailModal.vue'

export default {
  name: 'ProcessOverviewFiles',
  components: {
    ProcessOverviewDetailModal
  },
  props: {
    files: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      showModal: false,
      currentPage: 1,
      pageSize: 100,
      filterText: '',
      filterType: ''
    }
  },
  computed: {
    availableTypes() {
      if (!this.files?.categories) return []
      return Object.keys(this.files.categories).sort()
    },
    filteredFds() {
      if (!this.files?.fds) return []
      
      let result = this.files.fds
      
      if (this.filterType) {
        result = result.filter(fd => fd.type === this.filterType)
      }
      
      if (this.filterText) {
        const search = this.filterText.toLowerCase()
        result = result.filter(fd => 
          fd.target.toLowerCase().includes(search) ||
          fd.type.toLowerCase().includes(search) ||
          String(fd.fd).includes(search)
        )
      }
      
      return result
    },
    totalPages() {
      return Math.max(1, Math.ceil(this.filteredFds.length / this.pageSize))
    },
    paginatedFds() {
      const start = (this.currentPage - 1) * this.pageSize
      return this.filteredFds.slice(start, start + this.pageSize)
    }
  },
  watch: {
    filterText() {
      this.currentPage = 1
    },
    filterType() {
      this.currentPage = 1
    }
  },
  methods: {
    openModal() {
      this.showModal = true
      this.currentPage = 1
      this.filterText = ''
      this.filterType = ''
    },
    closeModal() {
      this.showModal = false
    },
    getTypeBadge(type) {
      const map = {
        'socket': 'badge-info',
        'pipe': 'badge-warning',
        'file': 'badge-success',
        'device': 'badge-secondary',
        'eventfd': 'badge-accent',
        'epoll': 'badge-accent',
        'proc': 'badge-ghost',
        'sysfs': 'badge-ghost'
      }
      return map[type] || 'badge-ghost'
    }
  }
}
</script>
