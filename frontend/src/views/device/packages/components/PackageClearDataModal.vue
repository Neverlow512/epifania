<template>
  <Teleport to="body">
    <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div
        class="absolute inset-0 bg-black/70 backdrop-blur-sm"
        @click="$emit('close')"
      ></div>

      <div class="relative bg-neutral-900 border border-red-500/30 rounded-xl shadow-2xl max-w-md w-full">
        <div class="flex items-center justify-between p-4 border-b border-neutral-800">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg bg-red-500/20 flex items-center justify-center">
              <svg class="w-5 h-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <div>
              <h3 class="text-lg font-semibold text-white">Clear App Data</h3>
              <p class="text-xs text-red-400">This action cannot be undone</p>
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

        <div class="p-4 space-y-4">
          <p class="text-slate-300">
            Are you sure you want to clear all data for
            <span class="font-medium text-white">{{ packageName }}</span>?
          </p>

          <div class="bg-red-500/10 border border-red-500/30 rounded-lg p-3 space-y-2">
            <p class="text-sm text-red-300 font-medium">This will permanently delete:</p>
            <ul class="text-sm text-slate-400 space-y-1 ml-4 list-disc">
              <li>All app settings and preferences</li>
              <li>User accounts and login data</li>
              <li>Databases and local storage</li>
              <li>Cache files</li>
            </ul>
          </div>

          <p class="text-xs text-slate-500">
            The app will reset to its initial state as if freshly installed.
          </p>
        </div>

        <div class="flex justify-end gap-2 p-4 border-t border-neutral-800">
          <button
            type="button"
            class="btn btn-sm btn-ghost"
            @click="$emit('close')"
          >
            Cancel
          </button>
          <button
            type="button"
            class="btn btn-sm btn-error"
            :disabled="clearing"
            @click="handleConfirm"
          >
            <span v-if="clearing" class="loading loading-spinner loading-xs"></span>
            {{ clearing ? 'Clearing...' : 'Clear Data' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'PackageClearDataModal',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    package: {
      type: Object,
      default: null
    },
    clearing: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close', 'confirm'],
  setup(props, { emit }) {
    const packageName = computed(() => {
      if (!props.package) return ''
      return props.package.name || props.package.package_id
    })

    const handleConfirm = () => {
      if (!props.package) return
      emit('confirm', props.package.package_id)
    }

    return {
      packageName,
      handleConfirm
    }
  }
}
</script>

