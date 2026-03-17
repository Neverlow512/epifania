<template>
  <tr class="bg-neutral-900/30 hover:bg-neutral-800/50 border-b border-neutral-700/50">
    <td class="w-12"></td>
    <td class="pl-8">
      <div class="flex items-center gap-2 flex-wrap">
        <span class="badge badge-xs badge-secondary">Export</span>
        <code 
          class="text-slate-300 text-xs font-mono cursor-help break-all" 
          :title="exportData.name"
        >{{ exportData.name }}</code>
        <span v-if="exportData.type" class="badge badge-xs badge-ghost">{{ exportData.type }}</span>
      </div>
      <div v-if="exportData.address" class="mt-1 text-[10px] text-slate-600 font-mono">
        Address: {{ exportData.address }}
      </div>
    </td>
    <td>
      <CategoryBadge :category="exportData.export_category || 'Unknown'" />
    </td>
    <td></td>
    <td class="text-right"></td>
  </tr>
</template>

<script>
import CategoryBadge from '../../shared/CategoryBadge.vue'

export default {
  name: 'ExportRow',
  components: {
    CategoryBadge
  },
  props: {
    exportData: {
      type: Object,
      required: true
    }
  }
}
</script>

