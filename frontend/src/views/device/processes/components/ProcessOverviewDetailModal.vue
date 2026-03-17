<template>
  <Teleport to="body">
    <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div
        class="absolute inset-0 bg-black/70 backdrop-blur-sm"
        @click="$emit('close')"
      ></div>
      <div class="relative bg-neutral-900 border border-primary/30 rounded-xl shadow-2xl w-full max-h-[85vh] overflow-hidden"
           :class="maxWidthClass">
        <div class="flex items-center justify-between p-4 border-b border-neutral-800">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg flex items-center justify-center" :class="iconBgClass">
              <slot name="icon">
                <svg class="w-5 h-5" :class="iconClass" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </slot>
            </div>
            <div>
              <h3 class="text-lg font-semibold text-white">{{ title }}</h3>
              <p v-if="subtitle" class="text-xs text-slate-500">{{ subtitle }}</p>
            </div>
          </div>
          <button
            type="button"
            class="btn btn-ghost btn-sm btn-circle"
            @click="$emit('close')"
          >
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="p-4 overflow-y-auto max-h-[calc(85vh-80px)]">
          <slot></slot>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script>
export default {
  name: 'ProcessOverviewDetailModal',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    title: {
      type: String,
      required: true
    },
    subtitle: {
      type: String,
      default: ''
    },
    iconBgClass: {
      type: String,
      default: 'bg-violet-500/20'
    },
    iconClass: {
      type: String,
      default: 'text-violet-400'
    },
    maxWidth: {
      type: String,
      default: '2xl'
    }
  },
  emits: ['close'],
  computed: {
    maxWidthClass() {
      const widths = {
        'lg': 'max-w-lg',
        'xl': 'max-w-xl',
        '2xl': 'max-w-2xl',
        '3xl': 'max-w-3xl',
        '4xl': 'max-w-4xl'
      }
      return widths[this.maxWidth] || 'max-w-2xl'
    }
  }
}
</script>

