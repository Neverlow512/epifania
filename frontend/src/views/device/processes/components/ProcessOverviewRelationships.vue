<template>
  <div class="space-y-2">
    <div class="flex items-center gap-2">
      <div class="w-7 h-7 rounded bg-rose-500/20 flex items-center justify-center flex-shrink-0">
        <svg class="w-4 h-4 text-rose-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      </div>
      <span class="text-xs text-slate-400 font-medium">Relationships</span>
      <button
        v-if="relationships?.children?.length > 3"
        type="button"
        class="ml-auto text-[9px] text-slate-500 hover:text-rose-400 transition-colors border border-slate-700 hover:border-rose-500/50 rounded px-1.5 py-0.5"
        @click="showModal = true"
      >
        View all
      </button>
    </div>

    <div v-if="relationships" class="bg-black/40 rounded-lg border border-slate-700/50 p-3 space-y-2">
      <div class="flex items-center gap-4 text-xs">
        <div>
          <span class="text-slate-500">Parent:</span>
          <button
            v-if="relationships.parent"
            type="button"
            class="ml-1 text-primary hover:underline font-mono"
            @click="$emit('inspect-process', relationships.parent.pid)"
          >
            {{ relationships.parent.name }} ({{ relationships.parent.pid }})
          </button>
          <span v-else class="ml-1 text-slate-400">None (init)</span>
        </div>
        <div>
          <span class="text-slate-500">Depth:</span>
          <span class="ml-1 text-slate-300">{{ relationships.tree_depth || 0 }}</span>
        </div>
      </div>

      <div v-if="relationships.children_count > 0" class="border-t border-neutral-800 pt-2">
        <div class="text-[10px] text-slate-500 mb-1">Children ({{ relationships.children_count }})</div>
        <div class="flex flex-wrap gap-1">
          <button
            v-for="child in topChildren"
            :key="child.pid"
            type="button"
            class="px-2 py-0.5 rounded bg-neutral-800 border border-neutral-700 text-xs hover:border-primary/50 hover:text-primary transition-colors"
            @click="$emit('inspect-process', child.pid)"
          >
            <span class="text-primary font-mono">{{ child.pid }}</span>
            <span class="text-slate-400 ml-1">{{ child.name }}</span>
          </button>
          <span
            v-if="relationships.children_count > 3"
            class="px-2 py-0.5 text-xs text-slate-500"
          >
            +{{ relationships.children_count - 3 }} more
          </span>
        </div>
      </div>

      <div v-else class="text-[10px] text-slate-500">No child processes</div>
    </div>

    <div v-else class="bg-black/40 rounded-lg border border-slate-700/50 p-3">
      <div class="flex items-center gap-2 text-slate-500 text-xs">
        <svg class="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div>
          <span class="block">Relationship info not available</span>
          <span class="text-[10px] text-slate-600">Unable to determine process hierarchy</span>
        </div>
      </div>
    </div>

    <ProcessOverviewDetailModal
      :show="showModal"
      title="Process Relationships"
      :subtitle="`${relationships?.children_count || 0} children`"
      icon-bg-class="bg-rose-500/20"
      icon-class="text-rose-400"
      max-width="2xl"
      @close="showModal = false"
    >
      <template #icon>
        <svg class="w-5 h-5 text-rose-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      </template>

      <div class="space-y-4">
        <div v-if="relationships?.parent" class="bg-black/40 rounded-lg border border-neutral-800 p-3">
          <div class="text-xs text-slate-500 mb-2">Parent Process</div>
          <button
            type="button"
            class="flex items-center gap-2 hover:text-primary transition-colors"
            @click="inspectAndClose(relationships.parent.pid)"
          >
            <span class="text-primary font-mono">{{ relationships.parent.pid }}</span>
            <span class="text-slate-300">{{ relationships.parent.name }}</span>
          </button>
        </div>

        <div>
          <div class="text-xs text-slate-500 mb-2">Child Processes ({{ relationships?.children_count || 0 }})</div>
          <div class="overflow-x-auto max-h-[50vh]">
            <table class="table table-xs w-full">
              <thead class="sticky top-0 bg-neutral-900 z-10">
                <tr class="text-slate-400 border-neutral-800">
                  <th>PID</th>
                  <th>Name</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="child in relationships?.children || []"
                  :key="child.pid"
                  class="border-neutral-800 hover:bg-neutral-800/50"
                >
                  <td class="font-mono text-primary">{{ child.pid }}</td>
                  <td class="text-slate-300">{{ child.name }}</td>
                  <td class="text-right">
                    <button
                      type="button"
                      class="btn btn-xs btn-ghost text-sky-400"
                      @click="inspectAndClose(child.pid)"
                    >
                      Inspect
                    </button>
                  </td>
                </tr>
                <tr v-if="!relationships?.children?.length">
                  <td colspan="3" class="text-center text-slate-500 py-4">No child processes</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </ProcessOverviewDetailModal>
  </div>
</template>

<script>
import ProcessOverviewDetailModal from './ProcessOverviewDetailModal.vue'

export default {
  name: 'ProcessOverviewRelationships',
  components: {
    ProcessOverviewDetailModal
  },
  props: {
    relationships: {
      type: Object,
      default: null
    }
  },
  emits: ['inspect-process'],
  data() {
    return {
      showModal: false
    }
  },
  computed: {
    topChildren() {
      if (!this.relationships?.children) return []
      return this.relationships.children.slice(0, 3)
    }
  },
  methods: {
    inspectAndClose(pid) {
      this.showModal = false
      this.$emit('inspect-process', pid)
    }
  }
}
</script>

