<template>
  <div>
    <div class="overflow-x-auto">
      <table class="table table-sm">
        <thead>
          <tr class="border-b border-primary/20">
            <th class="text-slate-400">Package Name</th>
            <th class="text-slate-400">Package ID</th>
            <th class="text-slate-400">Status (PID)</th>
            <th class="text-slate-400 text-right">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading && packages.length === 0">
            <td colspan="4" class="text-center py-8">
              <span class="loading loading-spinner loading-lg text-primary"></span>
            </td>
          </tr>
          <tr v-else-if="packages.length === 0">
            <td colspan="4" class="text-center py-8 text-slate-400">
              No packages found
            </td>
          </tr>
          <tr
            v-else
            v-for="pkg in packages"
            :key="pkg.package_id"
            class="hover:bg-primary/5 border-b border-neutral-800 cursor-pointer transition-colors"
            @click="$emit('view-details', pkg)"
          >
            <td class="text-white">
              <div class="flex items-center gap-2">
                <div
                  class="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold"
                  :class="pkg.is_system ? 'bg-slate-700 text-slate-300' : 'bg-violet-500/20 text-violet-400'"
                >
                  {{ getPackageInitials(pkg) }}
                </div>
                <div>
                  <span class="font-medium">{{ pkg.name || pkg.package_id }}</span>
                  <span
                    v-if="pkg.is_system"
                    class="ml-2 badge badge-xs badge-ghost text-slate-500"
                  >
                    system
                  </span>
                </div>
              </div>
            </td>
            <td class="text-slate-400 font-mono text-xs max-w-[200px] truncate" :title="pkg.package_id">
              {{ pkg.package_id }}
            </td>
            <td>
              <div class="flex items-center gap-2">
                <span
                  v-if="pkg.is_running"
                  class="badge badge-sm badge-success cursor-pointer hover:badge-outline transition-all"
                  @click.stop="$emit('navigate-to-process', pkg.pid)"
                  :title="`Click to view in Processes tab`"
                >
                  Running ({{ pkg.pid }})
                </span>
                <span v-else class="badge badge-sm badge-ghost">
                  Stopped
                </span>
              </div>
            </td>
            <td class="text-right">
              <PackageActionsMenu
                :package="pkg"
                :actionInProgress="actionInProgress"
                @view-details="$emit('view-details', pkg)"
                @launch="$emit('launch', pkg)"
                @stop="$emit('stop', pkg)"
                @uninstall="$emit('uninstall', pkg)"
                @pull="$emit('pull', pkg)"
                @clear-cache="$emit('clear-cache', pkg)"
                @clear-data="$emit('clear-data', pkg)"
                @navigate-to-process="$emit('navigate-to-process', pkg.pid)"
              />
            </td>
          </tr>
        </tbody>
      </table>

      <div class="flex justify-between items-center py-3 px-4 border-t border-primary/20 mt-2">
        <div class="text-sm text-slate-400">
          <span v-if="totalCount > 0">
            Showing {{ startIndex + 1 }}-{{ endIndex }} of {{ totalCount }} packages
          </span>
          <span v-else>No packages</span>
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
import PackageActionsMenu from './PackageActionsMenu.vue'

export default {
  name: 'PackageTable',
  components: {
    PackageActionsMenu
  },
  props: {
    packages: {
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
    },
    actionInProgress: {
      type: Boolean,
      default: false
    }
  },
  emits: [
    'page-change',
    'view-details',
    'launch',
    'stop',
    'uninstall',
    'pull',
    'clear-cache',
    'clear-data',
    'navigate-to-process'
  ],
  methods: {
    getPackageInitials(pkg) {
      const name = pkg.name || pkg.package_id
      const parts = name.split(/[.\s]/)
      if (parts.length >= 2) {
        return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
      }
      return name.substring(0, 2).toUpperCase()
    }
  }
}
</script>

