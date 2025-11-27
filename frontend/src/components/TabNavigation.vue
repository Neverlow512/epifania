<template>
  <div class="border-b border-primary/20 bg-neutral-900/40">
    <div class="flex overflow-x-auto">
      <button
        v-for="tab in tabs"
        :key="tab.name"
        type="button"
        @click="handleTabClick(tab.name)"
        @keydown.enter="handleTabClick(tab.name)"
        class="px-6 py-3 text-sm font-medium transition-colors whitespace-nowrap focus:outline-none focus:ring-2 focus:ring-primary/50"
        :class="[
          activeTab === tab.name
            ? 'text-white border-b-2 border-primary'
            : 'text-slate-400 hover:text-slate-300 border-b-2 border-transparent hover:border-primary/30'
        ]"
      >
        {{ tab.label }}
        <span
          v-if="tab.badge"
          class="ml-2 px-2 py-0.5 text-xs rounded-full bg-primary/20 text-primary"
        >
          {{ tab.badge }}
        </span>
      </button>
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
    const handleTabClick = (tabName) => {
      emit('tab-change', tabName)
    }

    return {
      handleTabClick
    }
  }
}
</script>

