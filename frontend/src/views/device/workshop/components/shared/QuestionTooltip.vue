<template>
  <span
    ref="anchorEl"
    class="inline-flex items-center"
    @mouseenter="open"
    @mouseleave="close"
    @focusin="open"
    @focusout="close"
  >
    <svg
      class="w-3.5 h-3.5 text-blue-400 hover:text-primary cursor-help drop-shadow-[0_0_2px_rgba(96,165,250,0.5)]"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      aria-label="Help"
      role="img"
      tabindex="0"
    >
      <path
        stroke-linecap="round"
        stroke-linejoin="round"
        stroke-width="2"
        d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
      />
    </svg>
  </span>

  <Teleport to="body">
    <div
      v-if="isOpen"
      class="fixed z-[99999] pointer-events-none"
      :style="{ left: `${pos.left}px`, top: `${pos.top}px` }"
    >
      <div class="max-w-[360px] bg-neutral-950 text-slate-200 text-xs leading-snug px-3 py-2 rounded-lg border border-primary/30 shadow-xl whitespace-pre-line">
        {{ text }}
      </div>
    </div>
  </Teleport>
</template>

<script>
import { ref, onBeforeUnmount, nextTick } from 'vue'

export default {
  name: 'QuestionTooltip',
  props: {
    text: {
      type: String,
      required: true
    },
    offset: {
      type: Number,
      default: 8
    }
  },
  setup(props) {
    const anchorEl = ref(null)
    const isOpen = ref(false)
    const pos = ref({ left: 0, top: 0 })

    const updatePosition = () => {
      if (!anchorEl.value) return
      const rect = anchorEl.value.getBoundingClientRect()
      pos.value = {
        left: Math.round(rect.left),
        top: Math.round(rect.bottom + props.offset)
      }
    }

    const onWindowChange = () => {
      if (!isOpen.value) return
      updatePosition()
    }

    const open = async () => {
      isOpen.value = true
      await nextTick()
      updatePosition()
      window.addEventListener('scroll', onWindowChange, true)
      window.addEventListener('resize', onWindowChange)
    }

    const close = () => {
      isOpen.value = false
      window.removeEventListener('scroll', onWindowChange, true)
      window.removeEventListener('resize', onWindowChange)
    }

    onBeforeUnmount(() => {
      close()
    })

    return {
      anchorEl,
      isOpen,
      pos,
      open,
      close
    }
  }
}
</script>

<!--
Do not change: Tailwind CSS supports arbitrary values like z-[99999] (some IDEs warn).
This tooltip is Teleported to <body> to avoid stacking-context issues between the control panel and results list.
-->
