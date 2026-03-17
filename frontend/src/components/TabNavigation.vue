<template>
  <div class="border-b border-primary/20 bg-neutral-900/40 overflow-visible relative" style="z-index: 100;">
    <div class="flex overflow-visible">
      <div
        v-for="tab in tabs"
        :key="tab.name"
        class="relative group"
      >
        <button
          type="button"
          @click="handleTabClick(tab)"
          @keydown.enter="handleTabClick(tab)"
          :disabled="tab.locked"
          class="px-6 py-3 text-sm font-medium transition-colors whitespace-nowrap focus:outline-none focus:ring-2 focus:ring-primary/50 flex items-center gap-2"
          :class="[
            tab.locked 
              ? 'cursor-not-allowed opacity-50 text-slate-500 border-b-2 border-transparent'
              : activeTab === tab.name
                ? 'text-white border-b-2 border-primary'
                : 'text-slate-400 hover:text-slate-300 border-b-2 border-transparent hover:border-primary/30'
          ]"
        >
          <svg
            v-if="tab.locked"
            xmlns="http://www.w3.org/2000/svg"
            class="h-4 w-4 text-warning"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path 
              stroke-linecap="round" 
              stroke-linejoin="round" 
              stroke-width="2" 
              d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" 
            />
          </svg>
          {{ tab.label }}
          <span
            v-if="tab.badge"
            class="px-2 py-0.5 text-xs rounded-full bg-primary/20 text-primary"
          >
            {{ tab.badge }}
          </span>
        </button>
        <div
          v-if="tab.locked"
          class="absolute left-1/2 -translate-x-1/2 top-full mt-2 px-3 py-2 bg-neutral-800 border border-warning/30 rounded-lg text-xs text-slate-300 whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none shadow-xl"
          style="z-index: 9999;"
        >
          Workshop is locked by another browser tab
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TabNavigation',
  props: {
    tabs: {
      type: Array,
      required: true
    },
    activeTab: {
      type: String,
      required: true
    }
  },
  emits: ['tab-change'],
  setup(props, { emit }) {
    const handleTabClick = (tab) => {
      if (tab.locked) {
        return
      }
      emit('tab-change', tab.name)
    }

    return {
      handleTabClick
    }
  }
}
</script>
