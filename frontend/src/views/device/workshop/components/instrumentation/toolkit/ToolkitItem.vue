<template>
  <button
    type="button"
    class="w-full flex items-center justify-between px-2 py-2 rounded-md text-left transition-colors duration-150 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary/40"
    :class="itemClasses"
    :aria-disabled="isPlaceholder ? 'true' : 'false'"
    @click="handleClick"
    @mouseenter="handlePreview"
    @mouseleave="handleClearPreview"
    @focus="handlePreview"
    @blur="handleClearPreview"
  >
    <span class="text-sm font-medium truncate" :class="labelColorClass">{{ label }}</span>
    <span class="flex items-center gap-2 shrink-0 ml-3">
      <span v-if="statusText" class="text-[10px] font-semibold tracking-[0.18em] uppercase" :class="statusColorClass">
        {{ statusText }}
      </span>
      <svg
        v-if="expandable"
        xmlns="http://www.w3.org/2000/svg"
        class="h-4 w-4 text-slate-500 transition-transform duration-200"
        :class="{ 'rotate-180': expanded }"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        aria-hidden="true"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </span>
  </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  id: {
    type: String,
    default: ''
  },
  label: {
    type: String,
    required: true
  },
  description: {
    type: String,
    default: ''
  },
  status: {
    type: String,
    default: 'placeholder',
    validator: (value) => ['active', 'development', 'placeholder'].includes(value)
  },
  icon: {
    type: String,
    default: ''
  },
  selected: {
    type: Boolean,
    default: false
  },
  expandable: {
    type: Boolean,
    default: false
  },
  expanded: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['click', 'preview', 'select', 'clearPreview'])

const isPlaceholder = computed(() => props.status === 'placeholder')

const itemClasses = computed(() => {
  if (props.selected) {
    if (props.status === 'development') return 'text-white bg-primary/15 cursor-pointer'
    if (props.status === 'placeholder') return 'text-slate-300 bg-neutral-900/40 cursor-pointer'
    return 'text-white bg-neutral-900/40 cursor-pointer'
  }
  if (props.status === 'active') {
    return 'text-white hover:bg-neutral-800/40 cursor-pointer'
  } else if (props.status === 'development') {
    return 'text-white bg-primary/5 hover:bg-primary/10 cursor-pointer'
  } else {
    return 'text-slate-400 opacity-60 cursor-default'
  }
})

const labelColorClass = computed(() => {
  if (props.status === 'placeholder') {
    return 'text-slate-400'
  }
  return 'text-white'
})

const statusText = computed(() => {
  if (props.status === 'development') return 'In development'
  if (props.status === 'placeholder') return 'Coming soon'
  return ''
})

const statusColorClass = computed(() => {
  if (props.status === 'development') return 'text-primary/90'
  if (props.status === 'placeholder') return 'text-slate-500'
  return 'text-slate-400'
})

const handleClick = () => {
  emit('select', { id: props.id, label: props.label, description: props.description, status: props.status })
  emit('preview', { id: props.id, label: props.label, description: props.description, status: props.status })
  if (props.status !== 'placeholder') emit('click', props.id)
}

const handlePreview = () => {
  emit('preview', { id: props.id, label: props.label, description: props.description, status: props.status })
}

const handleClearPreview = () => {
  emit('clearPreview')
}
</script>
