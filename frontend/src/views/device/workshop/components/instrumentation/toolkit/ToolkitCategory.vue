<template>
  <section class="space-y-1">
    <button
      type="button"
      class="group w-full flex items-center gap-3 py-1 px-1 rounded-md text-left cursor-pointer transition-colors duration-150 hover:bg-neutral-900/30 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary/40"
      @click="toggleExpanded"
      :aria-expanded="isExpanded ? 'true' : 'false'"
      :title="isExpanded ? 'Collapse section' : 'Expand section'"
    >
      <span class="text-[11px] font-semibold tracking-[0.18em] uppercase text-slate-400 transition-colors duration-150 group-hover:text-slate-200">
        {{ title }}
      </span>
      <div class="h-px flex-1 bg-primary/10"></div>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="h-4 w-4 text-slate-500 transition-transform duration-200 transition-colors group-hover:text-slate-300"
        :class="{ 'rotate-180': isExpanded }"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <div v-show="isExpanded" class="pl-1 space-y-0.5">
      <slot></slot>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  icon: {
    type: String,
    required: true
  },
  defaultExpanded: {
    type: Boolean,
    default: true
  }
})

const isExpanded = ref(false)

onMounted(() => {
  isExpanded.value = props.defaultExpanded
})

const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value
}
</script>
