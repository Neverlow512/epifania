<template>
  <div class="overflow-x-auto">
    <table class="table table-sm">
      <thead>
        <tr class="border-b border-primary/20">
          <th class="text-slate-400 font-semibold w-12"></th>
          <th class="text-slate-400 font-semibold">Module / Export</th>
          <th class="text-slate-400 font-semibold">Category</th>
          <th class="text-slate-400 font-semibold">Source</th>
          <th class="text-slate-400 font-semibold text-right">Info</th>
        </tr>
      </thead>
      <tbody>
        <template v-for="moduleData in modules" :key="moduleData.name">
          <ModuleRow
            :moduleData="moduleData"
            :expanded="expandedModules.has(moduleData.name)"
            @toggle-expand="$emit('toggle-expand', moduleData.name)"
          />
          <ExportRow
            v-if="expandedModules.has(moduleData.name)"
            v-for="exportData in moduleData.exports"
            :key="`${moduleData.name}.${exportData.name}`"
            :exportData="exportData"
          />
        </template>
      </tbody>
    </table>
  </div>
</template>

<script>
import ModuleRow from './ModuleRow.vue'
import ExportRow from './ExportRow.vue'

export default {
  name: 'ModuleExportTable',
  components: {
    ModuleRow,
    ExportRow
  },
  props: {
    modules: {
      type: Array,
      required: true
    },
    expandedModules: {
      type: Set,
      required: true
    }
  },
  emits: ['toggle-expand']
}
</script>

