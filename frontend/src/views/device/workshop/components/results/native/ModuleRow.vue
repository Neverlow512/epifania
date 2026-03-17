<template>
  <tr 
    class="hover:bg-neutral-800/50 cursor-pointer border-b border-neutral-700"
    @click="$emit('toggle-expand')"
  >
    <td class="w-12">
      <svg 
        xmlns="http://www.w3.org/2000/svg" 
        class="h-4 w-4 text-slate-400 transition-transform"
        :class="{ 'rotate-90': expanded }"
        fill="none" 
        viewBox="0 0 24 24" 
        stroke="currentColor"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
      </svg>
    </td>
    <td>
      <div class="flex items-center gap-2">
        <span class="badge badge-xs badge-primary">Module</span>
        <code 
          class="text-white text-xs font-mono cursor-help" 
          :title="moduleData.name"
        >{{ moduleData.name }}</code>
      </div>
      <div class="mt-1">
        <code 
          class="text-slate-500 text-[10px] font-mono cursor-pointer inline-block max-w-[520px] align-top"
          :class="pathExpanded ? 'whitespace-normal break-all' : 'truncate'"
          :title="moduleData.path"
          @click.stop="togglePathExpanded"
        >{{ displayPath }}</code>
      </div>
      <div v-if="expanded && moduleData.path" class="mt-1 text-[10px] text-slate-600 font-mono break-all max-w-md">
        Full path: {{ moduleData.path }}
      </div>
    </td>
    <td>
      <CategoryBadge :category="moduleData.module_category || 'Unknown'" />
    </td>
    <td>
      <SourceBadge :source="moduleData.source" />
    </td>
    <td class="text-right">
      <div class="flex flex-col gap-1 items-end">
        <span class="text-slate-400 text-xs">{{ moduleData.export_count || moduleData.exports?.length || 0 }} exports</span>
        <span v-if="moduleData.size" class="text-slate-500 text-[10px]">{{ formatSize(moduleData.size) }}</span>
      </div>
    </td>
  </tr>
</template>

<script>
import CategoryBadge from '../../shared/CategoryBadge.vue'
import SourceBadge from '../../shared/SourceBadge.vue'

export default {
  name: 'ModuleRow',
  components: {
    CategoryBadge,
    SourceBadge
  },
  props: {
    moduleData: {
      type: Object,
      required: true
    },
    expanded: {
      type: Boolean,
      required: true
    }
  },
  emits: ['toggle-expand'],
  data() {
    return {
      pathExpanded: false
    }
  },
  computed: {
    shouldTruncatePath() {
      const path = this.moduleData.path
      if (!path) return false
      return path.length > 110
    },
    displayPath() {
      const path = this.moduleData.path
      if (!path) return ''
      if (this.pathExpanded || !this.shouldTruncatePath) return path
      return path.substring(0, 107) + '...'
    }
  },
  methods: {
    togglePathExpanded() {
      if (!this.shouldTruncatePath) return
      this.pathExpanded = !this.pathExpanded
    },
    formatSize(size) {
      if (!size) return ''
      const bytes = parseInt(size)
      if (isNaN(bytes)) return size
      if (bytes < 1024) return `${bytes} B`
      if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
      return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
    }
  }
}
</script>

