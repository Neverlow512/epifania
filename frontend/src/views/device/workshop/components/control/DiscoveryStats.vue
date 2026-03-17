<template>
  <div class="card bg-black/30 border border-primary/20">
    <div class="card-body p-3">
      <h4 class="text-sm font-semibold text-white mb-3">Discovery Stats</h4>
      
      <div class="grid grid-cols-2 gap-2 text-sm mb-3">
        <div class="bg-neutral-900/50 p-2 rounded">
          <div class="text-slate-400 text-xs">Java Classes</div>
          <div class="text-white font-semibold">{{ stats.totalClasses }}</div>
        </div>
        <div class="bg-neutral-900/50 p-2 rounded">
          <div class="text-slate-400 text-xs">Java Methods</div>
          <div class="text-white font-semibold">{{ stats.totalMethods }}</div>
        </div>
        <div class="bg-neutral-900/50 p-2 rounded">
          <div class="text-slate-400 text-xs">Native Modules</div>
          <div class="text-white font-semibold">{{ stats.totalModules }}</div>
        </div>
        <div class="bg-neutral-900/50 p-2 rounded">
          <div class="text-slate-400 text-xs">Native Exports</div>
          <div class="text-white font-semibold">{{ stats.totalExports }}</div>
        </div>
      </div>
      
      <div v-if="hasCategories" class="collapse collapse-arrow bg-neutral-900/30">
        <input type="checkbox" />
        <div class="collapse-title text-xs font-medium text-white p-2">
          Category Breakdown
        </div>
        <div class="collapse-content p-2">
          <div class="space-y-1 text-xs">
            <div v-for="(count, category) in stats.javaCategories" :key="category" class="flex items-center justify-between">
              <span class="text-slate-400">{{ category }}</span>
              <span class="text-white">{{ count }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DiscoveryStats',
  props: {
    stats: {
      type: Object,
      required: true
    }
  },
  computed: {
    hasCategories() {
      return this.stats.javaCategories && Object.keys(this.stats.javaCategories).length > 0
    }
  }
}
</script>

